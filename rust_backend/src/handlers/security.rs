use std::sync::Arc;
use std::time::Duration;
use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use chrono::{Utc, Duration as ChronoDuration};
use bcrypt::{hash, verify, DEFAULT_COST};
use jwt::{SignWithKey, VerifyWithKey};
use rand::Rng;
use base32::Alphabet;
use qrcode::QrCode;
use image::Luma;
use reqwest::Client;
use serde_urlencoded;
use rate_limit::{RateLimiter, RateLimitError};
use hmac::{Hmac, Mac};
use sha1::Sha1;
use std::env;
use auth0::client::Client as Auth0Client;
use auth0::models::{User, TotpSettings};
use tracing::{error, warn, info};
use thiserror::Error;

const TOTP_INTERVAL: u64 = 30;
const MAX_ATTEMPTS: i32 = 5;
const LOCKOUT_DURATION: i64 = 3600;  // 1 hour lockout

#[derive(Error, Debug)]
pub enum SecurityError {
    #[error("Rate limit exceeded")]
    RateLimitExceeded,
    
    #[error("Account locked due to too many failed attempts")]
    AccountLocked,
    
    #[error("Invalid Auth0 credentials")]
    InvalidAuth0Credentials,
    
    #[error("TOTP not configured")]
    TotpNotConfigured,
    
    #[error("Invalid TOTP code")]
    InvalidTotpCode,
    
    #[error("KYC verification already in progress")]
    KycInProgress,
    
    #[error("Database error: {0}")]
    DatabaseError(String),
    
    #[error("Auth0 error: {0}")]
    Auth0Error(String),
    
    #[error("Internal server error: {0}")]
    InternalError(String),
}

impl From<SecurityError> for HttpResponse {
    fn from(err: SecurityError) -> Self {
        match err {
            SecurityError::RateLimitExceeded => 
                HttpResponse::TooManyRequests().body(err.to_string()),
            SecurityError::AccountLocked => 
                HttpResponse::Locked().body(err.to_string()),
            SecurityError::InvalidAuth0Credentials => 
                HttpResponse::Unauthorized().body(err.to_string()),
            SecurityError::TotpNotConfigured => 
                HttpResponse::BadRequest().body(err.to_string()),
            SecurityError::InvalidTotpCode => 
                HttpResponse::Unauthorized().body(err.to_string()),
            SecurityError::KycInProgress => 
                HttpResponse::Conflict().body(err.to_string()),
            SecurityError::DatabaseError(msg) => 
                HttpResponse::InternalServerError().body(msg),
            SecurityError::Auth0Error(msg) => 
                HttpResponse::InternalServerError().body(msg),
            SecurityError::InternalError(msg) => 
                HttpResponse::InternalServerError().body(msg),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserSecurity {
    pub id: String,
    pub user_id: String,
    pub kyc_verification_id: Option<String>,
    pub kyc_status: String,
    pub kyc_updated_at: chrono::DateTime<Utc>,
    pub failed_attempts: i32,
    pub last_attempt: Option<chrono::DateTime<Utc>>,
    pub locked_until: Option<chrono::DateTime<Utc>>,
    pub created_at: chrono::DateTime<Utc>,
    pub updated_at: chrono::DateTime<Utc>,
}

#[derive(Deserialize)]
pub struct TotpRequest {
    pub user_id: String,
    pub code: String,
    pub auth0_access_token: String,
    pub device: Option<String>,  // Device information for logging
    pub ip_address: Option<String>,  // IP address for logging
}

#[derive(Deserialize)]
pub struct KycRequest {
    pub user_id: String,
    pub email: String,
    pub first_name: String,
    pub last_name: String,
    pub auth0_access_token: String,  // Required for Auth0 verification
}

/// Main security service struct
/// Handles all security-related operations including TOTP and KYC
pub struct SecurityService {
    pool: PgPool,                // Database connection pool
    rate_limiter: RateLimiter,   // Rate limiting service
    bridge_client: reqwest::Client,  // Bridge.xyz API client
    persona_client: reqwest::Client, // Persona API client
}

impl SecurityService {
    /// Creates a new security service instance
    /// Initializes database connection and API clients
    pub fn new(pool: PgPool) -> Self {
        SecurityService {
            pool,
            rate_limiter: RateLimiter::new(100, 60),  // 100 requests per minute
            bridge_client: reqwest::Client::new(),
            persona_client: reqwest::Client::new(),
        }
    }

    /// Retrieves user security information from database
    /// Used internally by other methods
    async fn get_user_security(&self, user_id: &str) -> Result<HttpResponse, HttpResponse> {
        sqlx::query_as!(
            UserSecurity,
            r#"
            SELECT * FROM user_security WHERE user_id = $1
            "#,
            user_id
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| HttpResponse::InternalServerError().body(format!("Database error: {}", e)))
    }

    /// Generates a new TOTP secret for user
    /// Used during 2FA setup
    pub async fn generate_totp_secret(&self, user_id: &str) -> Result<HttpResponse, HttpResponse> {
        // Check rate limiting
        if let Err(_) = self.rate_limiter.check() {
            return Ok(HttpResponse::TooManyRequests().body("Rate limit exceeded"));
        }

        // Generate new TOTP secret using base32 encoding
        let secret = base32::encode(base32::Alphabet::RFC4648 { padding: false }, &rand::random::<[u8; 20]>());
        
        // Update user's security record with new secret
        sqlx::query!(
            r#"
            UPDATE user_security
            SET totp_secret = $1, totp_enabled = false, failed_attempts = 0
            WHERE user_id = $2
            "#,
            secret,
            user_id
        )
        .execute(&self.pool)
        .await
        .map_err(|e| HttpResponse::InternalServerError().body(format!("Database error: {}", e)))?;

        Ok(HttpResponse::Ok().json(secret))
    }

    /// Verifies a TOTP code for user
    /// Implements HMAC-based TOTP verification
    pub async fn verify_totp(&self, req: web::Json<TotpRequest>) -> Result<HttpResponse, HttpResponse> {
        // Check rate limiting
        if let Err(_) = self.rate_limiter.check() {
            return Ok(HttpResponse::TooManyRequests().body("Rate limit exceeded"));
        }

        // Get user's security information
        let user = self.get_user_security(&req.user_id).await?;
        
        // Check if account is locked due to too many failed attempts
        if user.locked_until.is_some() && user.locked_until.unwrap() > Utc::now() {
            return Ok(HttpResponse::Locked().body("Account locked due to too many failed attempts"));
        }

        // Verify if TOTP is configured
        if !user.totp_secret.is_some() {
            return Ok(HttpResponse::BadRequest().body("TOTP not configured"));
        }

        // Get user's secret and current time
        let secret = user.totp_secret.unwrap();
        let time = Utc::now().timestamp() as u64;
        let code = &req.code;

        // Generate HMAC using SHA1
        let mut hash = [0u8; 20];
        hmac::Hmac::<sha1::Sha1>::new_from_slice(secret.as_bytes())
            .map_err(|_| HttpResponse::InternalServerError().body("HMAC error"))?
            .chain_update(time.to_be_bytes())
            .finalize_into(&mut hash);

        // Generate 6-digit TOTP code from HMAC
        let truncated_hash = hash[0] & 0x0f;
        let offset = (truncated_hash as usize) * 8;
        let code_bytes = &hash[offset..offset + 4];
        let code_num = u32::from_be_bytes(code_bytes.try_into().unwrap()) & 0x7fffffff;
        let code_str = format!("{:06}", code_num % 1_000_000);

        // Verify code and update user status
        if code_str == code {
            sqlx::query!(
                r#"
                UPDATE user_security
                SET totp_enabled = true, totp_last_verified = $1, failed_attempts = 0
                WHERE user_id = $2
                "#,
                Utc::now(),
                &req.user_id
            )
            .execute(&self.pool)
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("Database error: {}", e)))?;

            Ok(HttpResponse::Ok().body("TOTP verified successfully"))
        } else {
            // Increment failed attempts and potentially lock account
            let failed_attempts = user.failed_attempts + 1;
            let locked_until = if failed_attempts >= MAX_ATTEMPTS {
                Some(Utc::now() + ChronoDuration::seconds(LOCKOUT_DURATION))
            } else {
                None
            };

            sqlx::query!(
                r#"
                UPDATE user_security
                SET failed_attempts = $1, last_attempt = $2, locked_until = $3
                WHERE user_id = $4
                "#,
                failed_attempts,
                Utc::now(),
                locked_until,
                &req.user_id
            )
            .execute(&self.pool)
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("Database error: {}", e)))?;

            Ok(HttpResponse::Unauthorized().body("Invalid TOTP code"))
        }
    }

    /// Initiates KYC verification process
    /// Creates customer in Bridge.xyz and verification in Persona
    pub async fn initiate_kyc(&self, req: web::Json<KycRequest>) -> Result<HttpResponse, HttpResponse> {
        // Check rate limiting
        if let Err(_) = self.rate_limiter.check() {
            return Ok(HttpResponse::TooManyRequests().body("Rate limit exceeded"));
        }

        // Get user's security information
        let user = self.get_user_security(&req.user_id).await?;
        
        // Check if KYC is already in progress
        if user.kyc_status == "PENDING" {
            return Ok(HttpResponse::Conflict().body("KYC verification already in progress"));
        }

        // Create customer in Bridge.xyz
        let bridge_response = self.bridge_client
            .post("https://api.bridge.xyz/v0/customers")
            .json(&json!({
                "email": req.email,
                "name": format!("{} {}", req.first_name, req.last_name)
            }))
            .send()
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("Bridge API error: {}", e)))?;

        // Handle Bridge API response
        if !bridge_response.status().is_success() {
            return Ok(HttpResponse::InternalServerError().body("Failed to create customer"));
        }

        let customer_data = bridge_response
            .json::<serde_json::Value>()
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("JSON parse error: {}", e)))?;

        // Create verification in Persona
        let persona_response = self.persona_client
            .post("https://api.persona.id/v1/verifications")
            .json(&json!({
                "type": "IDENTITY",
                "subject": {
                    "email": req.email,
                    "name": format!("{} {}", req.first_name, req.last_name)
                },
                "metadata": {
                    "customer_id": customer_data["id"].as_str().unwrap_or_default()
                }
            }))
            .send()
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("Persona API error: {}", e)))?;

        // Handle Persona API response
        if !persona_response.status().is_success() {
            return Ok(HttpResponse::InternalServerError().body("Failed to create verification"));
        }

        let verification_data = persona_response
            .json::<serde_json::Value>()
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("JSON parse error: {}", e)))?;

        // Update user's KYC status
        sqlx::query!(
            r#"
            UPDATE user_security
            SET kyc_verification_id = $1, kyc_status = 'PENDING', kyc_updated_at = $2
            WHERE user_id = $3
            "#,
            verification_data["id"].as_str().unwrap_or_default(),
            Utc::now(),
            &req.user_id
        )
        .execute(&self.pool)
        .await
        .map_err(|e| HttpResponse::InternalServerError().body(format!("Database error: {}", e)))?;

        // Return verification details
        Ok(HttpResponse::Ok().json(json!({
            "verification_id": verification_data["id"].as_str().unwrap_or_default(),
            "status": "PENDING",
            "customer_id": customer_data["id"].as_str().unwrap_or_default()
        })))
    }

    /// Checks current KYC verification status
    /// Retrieves status from Persona API and updates database
    pub async fn check_kyc_status(&self, user_id: &str) -> Result<HttpResponse, HttpResponse> {
        // Check rate limiting
        if let Err(_) = self.rate_limiter.check() {
            return Ok(HttpResponse::TooManyRequests().body("Rate limit exceeded"));
        }

        // Get user's security information
        let user = self.get_user_security(user_id).await?;
        
        // Check if KYC verification has been initiated
        if user.kyc_verification_id.is_none() {
            return Ok(HttpResponse::BadRequest().body("No KYC verification initiated"));
        }

        // Get verification ID and check status in Persona
        let verification_id = user.kyc_verification_id.unwrap();
        let persona_response = self.persona_client
            .get(format!("https://api.persona.id/v1/verifications/{}", verification_id))
            .send()
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("Persona API error: {}", e)))?;

        // Handle Persona API response
        if !persona_response.status().is_success() {
            return Ok(HttpResponse::InternalServerError().body("Failed to check verification status"));
        }

        let verification_data = persona_response
            .json::<serde_json::Value>()
            .await
            .map_err(|e| HttpResponse::InternalServerError().body(format!("JSON parse error: {}", e)))?;

        // Update user's KYC status
        sqlx::query!(
            r#"
            UPDATE user_security
            SET kyc_status = $1, kyc_updated_at = $2
            WHERE user_id = $3
            "#,
            verification_data["status"].as_str().unwrap_or_default(),
            Utc::now(),
            user_id
        )
        .execute(&self.pool)
        .await
        .map_err(|e| HttpResponse::InternalServerError().body(format!("Database error: {}", e)))?;

        // Return verification status
        Ok(HttpResponse::Ok().json(json!({
            "status": verification_data["status"].as_str().unwrap_or_default(),
            "updated_at": verification_data["updated_at"].as_str().unwrap_or_default(),
            "reason": verification_data["reason"].as_str().unwrap_or_default()
        })))
    }
}
