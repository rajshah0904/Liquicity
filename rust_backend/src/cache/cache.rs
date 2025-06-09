// Cache service implementation for security-related data
// This module provides Redis-based caching for security operations

use std::sync::Arc;
use std::time::Duration;
use redis::aio::ConnectionManager;
use redis::AsyncCommands;
use serde::{Deserialize, Serialize};
use tokio::sync::Mutex;

/// Struct representing cached security data for a user
/// Used for storing security-related information in Redis
#[derive(Debug, Serialize, Deserialize)]
pub struct CachedSecurityData {
    pub user_id: String,        // User identifier
    pub totp_enabled: bool,     // 2FA status
    pub kyc_status: String,     // KYC verification status
    pub last_verified: Option<String>,  // Timestamp of last verification
    pub failed_attempts: u32,   // Number of failed login attempts
    pub locked_until: Option<String>,  // Lockout expiration timestamp
}

/// Main cache service struct
/// Handles all Redis operations for security data
pub struct CacheService {
    conn: Arc<Mutex<ConnectionManager>>,  // Redis client connection
    ttl: Duration,  // Time to live for cached data
}

impl CacheService {
    /// Creates a new cache service instance
    /// Initializes Redis client with provided connection manager and TTL
    pub fn new(conn: ConnectionManager, ttl: Duration) -> Self {
        CacheService {
            conn: Arc::new(Mutex::new(conn)),
            ttl,
        }
    }

    /// Retrieves cached security data for a user
    /// Returns None if no data exists in cache
    pub async fn get_user_data(&self, user_id: &str) -> Result<Option<CachedSecurityData>, String> {
        let mut conn = self.conn.lock().await;
        let key = format!("security:user:{}", user_id);
        
        match conn.get::<_, Option<String>>(&key).await {
            Ok(Some(data)) => match serde_json::from_str(&data) {
                Ok(user_data) => Ok(Some(user_data)),
                Err(e) => Err(format!("Failed to deserialize cached data: {}", e)),
            },
            Ok(None) => Ok(None),
            Err(e) => Err(format!("Redis error: {}", e)),
        }
    }

    /// Stores security data in cache for a user
    /// Serializes data to JSON and stores in Redis
    pub async fn set_user_data(&self, user_id: &str, data: &CachedSecurityData) -> Result<(), String> {
        let mut conn = self.conn.lock().await;
        let key = format!("security:user:{}", user_id);
        let data_json = serde_json::to_string(data)
            .map_err(|e| format!("Failed to serialize data: {}", e))?;

        conn.set_ex(&key, data_json, self.ttl.as_secs() as usize)
            .await
            .map_err(|e| format!("Redis error: {}", e))
    }

    /// Invalidates cache for a user
    /// Removes all cached data for the specified user
    pub async fn invalidate_user_cache(&self, user_id: &str) -> Result<(), String> {
        let mut conn = self.conn.lock().await;
        let key = format!("security:user:{}", user_id);
        
        conn.del(&key)
            .await
            .map_err(|e| format!("Redis error: {}", e))
    }

    /// Retrieves rate limit counter for a key
    /// Used for rate limiting security operations
    pub async fn get_rate_limit(&self, user_id: &str, action: &str) -> Result<u64, String> {
        let mut conn = self.conn.lock().await;
        let key = format!("rate_limit:{}:{}", user_id, action);
        
        match conn.get::<_, Option<u64>>(&key).await {
            Ok(Some(count)) => Ok(count),
            Ok(None) => Ok(0),
            Err(e) => Err(format!("Redis error: {}", e)),
        }
    }

    /// Increments rate limit counter for a key
    /// Sets expiration time for the counter
    pub async fn increment_rate_limit(&self, user_id: &str, action: &str) -> Result<u64, String> {
        let mut conn = self.conn.lock().await;
        let key = format!("rate_limit:{}:{}", user_id, action);
        
        conn.incr(&key)
            .await
            .map_err(|e| format!("Redis error: {}", e))
    }

    /// Resets rate limit counter for a key
    /// Removes the counter from Redis
    pub async fn clear_rate_limit(&self, user_id: &str, action: &str) -> Result<(), String> {
        let mut conn = self.conn.lock().await;
        let key = format!("rate_limit:{}:{}", user_id, action);
        
        conn.del(&key)
            .await
            .map_err(|e| format!("Redis error: {}", e))
    }
}
