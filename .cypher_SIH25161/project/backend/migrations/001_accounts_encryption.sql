-- Migration: Account Encryption & API Key Management
-- Date: 2025-12-08
-- Purpose: Add multi-tenant account encryption layer

-- ============================================================================
-- 1. ACCOUNTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    data_key_encrypted TEXT NOT NULL, -- AES-GCM encrypted per-account key
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_accounts_status ON accounts(status);

-- ============================================================================
-- 2. API KEYS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    prefix TEXT NOT NULL, -- First 8 chars for lookup
    key_hash TEXT NOT NULL, -- bcrypt/argon2 hash
    name TEXT, -- Optional friendly name
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used TIMESTAMPTZ,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    
    UNIQUE(prefix)
);

CREATE INDEX idx_api_keys_account ON api_keys(account_id);
CREATE INDEX idx_api_keys_prefix ON api_keys(prefix);
CREATE INDEX idx_api_keys_revoked ON api_keys(revoked) WHERE NOT revoked;

-- ============================================================================
-- 3. UPDATE THREATS TABLE
-- ============================================================================
-- Add account_id and encryption fields
ALTER TABLE threats 
ADD COLUMN IF NOT EXISTS account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS text_enc TEXT, -- Encrypted text content
ADD COLUMN IF NOT EXISTS nonce TEXT, -- Base64 encoded nonce
ADD COLUMN IF NOT EXISTS tag TEXT; -- Base64 encoded auth tag

-- Create index for account isolation
CREATE INDEX IF NOT EXISTS idx_threats_account ON threats(account_id);

-- ============================================================================
-- 4. AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL, -- 'api_key_created', 'analyze_called', etc.
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB,
    ip_address TEXT,
    user_agent TEXT
);

CREATE INDEX idx_audit_account ON audit_log(account_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_event_type ON audit_log(event_type);

-- ============================================================================
-- 5. ROW LEVEL SECURITY
-- ============================================================================

-- Enable RLS on accounts
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own account
CREATE POLICY account_isolation ON accounts
    FOR ALL
    USING (id::text = current_setting('request.account_id', TRUE));

-- Enable RLS on threats
ALTER TABLE threats ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own threats
CREATE POLICY threat_isolation ON threats
    FOR ALL
    USING (account_id::text = current_setting('request.account_id', TRUE));

-- Enable RLS on api_keys
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own API keys
CREATE POLICY api_key_isolation ON api_keys
    FOR ALL
    USING (account_id::text = current_setting('request.account_id', TRUE));

-- ============================================================================
-- 6. FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for accounts table
CREATE TRIGGER accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- 7. MIGRATION NOTES
-- ============================================================================
-- To apply this migration:
-- 1. Ensure MASTER_KEY is set in environment
-- 2. Run migration against Supabase database
-- 3. Migrate existing user_api_keys to new accounts + api_keys structure
-- 4. Encrypt existing threat text fields
-- 5. Update application code to use new encryption layer
