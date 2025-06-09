use std::sync::Arc;
use std::time::SystemTime;
use actix_web::web;
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use chrono::{Utc, Duration};
use tracing::{info, warn, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

// Security logging service implementation
// This module provides structured logging for security events

/// Struct representing a security log entry
/// Used for storing security events in the database
#[derive(Debug, Serialize, Deserialize)]
pub struct SecurityLog {
    pub user_id: String,        // User identifier
    pub action: String,         // Type of action (e.g., TOTP_VERIFY, KYC_CHECK)
    pub status: String,         // Status of the action (SUCCESS, FAILURE, etc.)
    pub details: serde_json::Value,  // Additional details about the event
    pub timestamp: String,      // Timestamp of the event
    pub ip_address: Option<String>,  // IP address of the user
    pub user_agent: Option<String>,  // User agent of the user
    pub device: Option<String>,  // Device information
    pub auth0_operation: Option<String>,  // Auth0 operation type
    pub auth0_status: Option<String>,    // Auth0 operation status
    pub auth0_error: Option<String>,     // Auth0 error details
    pub session_id: Option<String>,      // Session identifier
}

/// Main logging service struct
/// Handles all security logging operations
pub struct LoggingService {
    pool: PgPool,  // Database connection pool
    log_level: String,  // Logging level
}

impl LoggingService {
    /// Creates a new logging service instance
    /// Initializes with database connection pool and logging level
    pub fn new(pool: PgPool, log_level: String) -> Self {
        LoggingService { pool, log_level }
    }

    /// Initializes the logging service
    /// Sets up the logging level and tracing subscriber
    pub fn init(&self) {
        let filter = match self.log_level.as_str() {
            "debug" => "debug",
            "info" => "info",
            "warn" => "warn",
            "error" => "error",
            _ => "info",
        };

        tracing_subscriber::registry()
            .with(tracing_subscriber::fmt::layer())
            .with(tracing_subscriber::EnvFilter::new(filter))
            .init();
    }

    /// Logs a security event
    /// Stores the event in the security_audit_logs table
    pub async fn log_security_event(&self, event: SecurityLog) -> Result<(), String> {
        // Log to database
        sqlx::query!(
            r#"
            INSERT INTO security_audit_logs (
                user_id,
                action,
                status,
                details,
                ip_address,
                user_agent
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            "#,
            event.user_id,
            event.action,
            event.status,
            event.details,
            event.ip_address,
            event.user_agent
        )
        .execute(&self.pool)
        .await
        .map_err(|e| e.to_string())?;

        // Log to tracing
        match event.status.as_str() {
            "ERROR" => error!(
                user_id = event.user_id,
                action = event.action,
                details = ?event.details,
                "Security event occurred"
            ),
            "WARN" => warn!(
                user_id = event.user_id,
                action = event.action,
                details = ?event.details,
                "Security warning"
            ),
            _ => info!(
                user_id = event.user_id,
                action = event.action,
                details = ?event.details,
                "Security event logged"
            ),
        }

        Ok(())
    }

    /// Retrieves security logs for a user
    /// Returns recent events in descending order
    pub async fn get_security_logs(
        &self,
        user_id: Option<String>,
        action: Option<String>,
        start_time: Option<String>,
        end_time: Option<String>,
        limit: Option<i64>,
    ) -> Result<Vec<SecurityLog>, String> {
        let mut query = sqlx::query_as!(
            SecurityLog,
            r#"
            SELECT 
                user_id,
                action,
                status,
                details,
                to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as timestamp,
                ip_address,
                user_agent
            FROM security_audit_logs
            WHERE 1=1
            "#
        );

        if let Some(uid) = user_id {
            query = query.bind(uid);
        }

        if let Some(act) = action {
            query = query.bind(act);
        }

        if let Some(start) = start_time {
            query = query.bind(start);
        }

        if let Some(end) = end_time {
            query = query.bind(end);
        }

        if let Some(lim) = limit {
            query = query.bind(lim);
        }

        query.fetch_all(&self.pool)
            .await
            .map_err(|e| e.to_string())
    }

    pub async fn get_failed_attempts(
        &self,
        user_id: Option<String>,
        start_time: Option<String>,
        end_time: Option<String>,
        limit: Option<i64>,
    ) -> Result<Vec<FailedAttempt>, String> {
        let mut query = sqlx::query_as!(
            FailedAttempt,
            r#"
            SELECT 
                user_id,
                attempt_time,
                ip_address,
                user_agent
            FROM failed_login_attempts
            WHERE 1=1
            "#
        );

        if let Some(uid) = user_id {
            query = query.bind(uid);
        }

        if let Some(start) = start_time {
            query = query.bind(start);
        }

        if let Some(end) = end_time {
            query = query.bind(end);
        }

        if let Some(lim) = limit {
            query = query.bind(lim);
        }

        query.fetch_all(&self.pool)
            .await
            .map_err(|e| e.to_string())
    }
}
