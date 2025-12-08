-- ============================================================================
-- Migration: Add Privacy Settings for Training Data Consent
-- ============================================================================

-- Add privacy settings to accounts table
ALTER TABLE accounts 
ADD COLUMN IF NOT EXISTS allow_training_data BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS training_consent_at TIMESTAMPTZ;

-- Add comment for clarity
COMMENT ON COLUMN accounts.allow_training_data IS 'User consent to use their data for model training';
COMMENT ON COLUMN accounts.training_consent_at IS 'Timestamp when user granted/revoked training consent';

-- Create index for efficient filtering
CREATE INDEX IF NOT EXISTS idx_accounts_training_consent ON accounts(allow_training_data) WHERE allow_training_data = TRUE;

-- Update training_data table to track consent at time of storage
-- Note: Adding with DEFAULT FALSE first, then updating existing rows
ALTER TABLE training_data
ADD COLUMN IF NOT EXISTS consent_verified BOOLEAN DEFAULT FALSE;

-- Update existing rows to have the default value
UPDATE training_data SET consent_verified = FALSE WHERE consent_verified IS NULL;

-- Now make it NOT NULL
ALTER TABLE training_data
ALTER COLUMN consent_verified SET NOT NULL;

COMMENT ON COLUMN training_data.consent_verified IS 'Whether user consent was verified at time of data storage';

-- Create index for filtering training data by consent
CREATE INDEX IF NOT EXISTS idx_training_data_consent ON training_data(consent_verified) WHERE consent_verified = TRUE;
