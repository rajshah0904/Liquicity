use std::sync::Arc;
use std::time::SystemTime;
use actix_web::web;
// Security monitoring service implementation
// This module provides monitoring and statistics for security operations

use serde::{Deserialize, Serialize};
use chrono::{Utc, Duration};
use sqlx::PgPool;
use tokio::time::Instant;

/// Struct representing overall security metrics
/// Contains aggregated statistics for security operations
#[derive(Debug, Serialize, Deserialize)]
pub struct SecurityMetrics {
    pub total_requests: i64,      // Total requests in last 24 hours
    pub failed_attempts: i64,     // Total failed login attempts in last 24 hours
    pub locked_accounts: i64,     // Number of currently locked accounts
    pub active_sessions: i64,     // Number of active sessions in last hour
    pub last_24h_metrics: Vec<HourlyMetrics>,  // Hourly statistics
}

/// Struct representing hourly statistics
/// Used for tracking request patterns over time
#[derive(Debug, Serialize, Deserialize)]
pub struct HourlyMetrics {
    pub hour: String,             // Hour of the day (HH24 format)
    pub requests: i64,           // Number of requests in that hour
    pub failed_attempts: i64,    // Number of failed attempts in that hour
    pub successful_verifications: i64,    // Number of successful verifications in that hour
}

/// Main monitoring service struct
/// Handles all security monitoring operations
pub struct MonitoringService {
    pool: PgPool,  // Database connection pool
    metrics: Arc<std::sync::Mutex<MetricsCache>>,
    last_update: Instant,
}

struct MetricsCache {
    total_requests: i64,
    failed_attempts: i64,
    locked_accounts: i64,
    active_sessions: i64,
    hourly_metrics: std::collections::HashMap<String, HourlyMetrics>,
}

impl MonitoringService {
    /// Creates a new monitoring service instance
    /// Initializes with database connection pool
    pub fn new(pool: PgPool) -> Self {
        MonitoringService {
            pool,
            metrics: Arc::new(std::sync::Mutex::new(MetricsCache {
                total_requests: 0,
                failed_attempts: 0,
                locked_accounts: 0,
                active_sessions: 0,
                hourly_metrics: std::collections::HashMap::new(),
            })),
            last_update: Instant::now(),
        }
    }

    /// Retrieves comprehensive security metrics
    /// Includes total requests, failed attempts, locked accounts, etc.
    pub async fn get_metrics(&self) -> Result<SecurityMetrics, String> {
        self.update_metrics().await?;
        let metrics = self.metrics.lock().unwrap();
        
        Ok(SecurityMetrics {
            total_requests: metrics.total_requests,
            failed_attempts: metrics.failed_attempts,
            locked_accounts: metrics.locked_accounts,
            active_sessions: metrics.active_sessions,
            last_24h_metrics: metrics.hourly_metrics
                .values()
                .cloned()
                .collect(),
        })
    }

    /// Updates metrics from database
    pub async fn update_metrics(&self) -> Result<(), String> {
        // Get total requests
        let total_requests = sqlx::query!(
            r#"
            SELECT COUNT(*) FROM security_audit_logs
            WHERE created_at > NOW() - INTERVAL '24 hours'
            "#
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| e.to_string())?
        .count
        .unwrap_or(0);

        // Get failed attempts
        let failed_attempts = sqlx::query!(
            r#"
            SELECT COUNT(*) FROM failed_login_attempts
            WHERE attempt_time > NOW() - INTERVAL '24 hours'
            "#
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| e.to_string())?
        .count
        .unwrap_or(0);

        // Get locked accounts
        let locked_accounts = sqlx::query!(
            r#"
            SELECT COUNT(*) FROM user_security
            WHERE locked_until IS NOT NULL AND locked_until > NOW()
            "#
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| e.to_string())?
        .count
        .unwrap_or(0);

        // Get active sessions
        let active_sessions = sqlx::query!(
            r#"
            SELECT COUNT(DISTINCT user_id) as count
            FROM security_audit_logs
            WHERE action = 'LOGIN_ATTEMPT'
            AND status = 'SUCCESS'
            AND created_at > NOW() - INTERVAL '1 hour'
            "#
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| e.to_string())?
        .count
        .unwrap_or(0);

        // Update hourly metrics
        let current_hour = Utc::now().format("%Y-%m-%d %H:00:00").to_string();
        let hourly_metrics = sqlx::query!(
            r#"
            SELECT 
                date_trunc('hour', created_at) as hour,
                COUNT(*) as requests,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_attempts,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_verifications
            FROM security_audit_logs
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour
            "#
        )
        .fetch_all(&self.pool)
        .await
        .map_err(|e| e.to_string())?
        .into_iter()
        .map(|row| HourlyMetrics {
            hour: row.hour.expect("hour should exist").to_string(),
            requests: row.requests.unwrap_or(0),
            failed_attempts: row.failed_attempts.unwrap_or(0),
            successful_verifications: row.successful_verifications.unwrap_or(0),
        })
        .collect::<Vec<_>>();

        // Update cache
        let mut metrics = self.metrics.lock().unwrap();
        metrics.total_requests = total_requests;
        metrics.failed_attempts = failed_attempts;
        metrics.locked_accounts = locked_accounts;
        metrics.active_sessions = active_sessions;
        metrics.hourly_metrics = hourly_metrics
            .into_iter()
            .map(|m| (m.hour.clone(), m))
            .collect();

        Ok(())
    }

    pub async fn get_metrics(&self) -> Result<SecurityMetrics, String> {
        self.update_metrics().await?;
        let metrics = self.metrics.lock().unwrap();
        
        Ok(SecurityMetrics {
            total_requests: metrics.total_requests,
            failed_attempts: metrics.failed_attempts,
            locked_accounts: metrics.locked_accounts,
            active_sessions: metrics.active_sessions,
            last_24h_metrics: metrics.hourly_metrics
                .values()
                .cloned()
                .collect(),
        })
    }

    pub async fn alert_on_security_event(&self, event_type: &str, details: serde_json::Value) {
        // Send alert to monitoring system
        // This could be integrated with external monitoring services
        // or internal alerting system
        let alert = serde_json::json!({
            "event_type": event_type,
            "timestamp": Utc::now().to_rfc3339(),
            "details": details,
            "severity": match event_type {
                "RATE_LIMIT" => "WARNING",
                "ACCOUNT_LOCKED" => "CRITICAL",
                "FAILED_ATTEMPT" => "WARNING",
                _ => "INFO",
            }
        });

        // TODO: Implement actual alerting mechanism
        println!("Security alert: {}", alert.to_string());
    }
}
