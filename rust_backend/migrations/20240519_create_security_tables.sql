-- Create user_security table
CREATE TABLE IF NOT EXISTS user_security (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT UNIQUE NOT NULL,
    kyc_verification_id TEXT,
    kyc_status TEXT DEFAULT 'NOT_STARTED',
    kyc_updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    last_attempt TIMESTAMPTZ,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_kyc_status CHECK (kyc_status IN ('NOT_STARTED', 'PENDING', 'VERIFIED', 'FAILED'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_security_user_id ON user_security(user_id);
CREATE INDEX IF NOT EXISTS idx_user_security_kyc_status ON user_security(kyc_status);
CREATE INDEX IF NOT EXISTS idx_user_security_locked_until ON user_security(locked_until);

-- Create audit log table
CREATE TABLE IF NOT EXISTS security_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_action CHECK (action IN (
        'TOTP_GENERATE',
        'TOTP_VERIFY',
        'KYC_INITIATE',
        'KYC_CHECK',
        'RATE_LIMIT_HIT',
        'LOGIN_ATTEMPT'
    ))
);

-- Create indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_security_audit_logs_user_id ON security_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_logs_action ON security_audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_security_audit_logs_created_at ON security_audit_logs(created_at);

-- Create failed login attempts table
CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    attempt_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    CONSTRAINT fk_user_security
        FOREIGN KEY (user_id)
        REFERENCES user_security(user_id)
        ON DELETE CASCADE
);

-- Create indexes for failed attempts
CREATE INDEX IF NOT EXISTS idx_failed_attempts_user_id ON failed_login_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_failed_attempts_attempt_time ON failed_login_attempts(attempt_time);
