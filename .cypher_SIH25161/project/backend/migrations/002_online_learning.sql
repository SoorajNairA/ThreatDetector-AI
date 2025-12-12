-- ============================================================================
-- Online Learning System - Training Data Storage
-- ============================================================================

-- Training data table to store feature vectors and labels
CREATE TABLE IF NOT EXISTS training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    -- Feature vector (stored as JSON array for flexibility)
    features JSONB NOT NULL,
    
    -- Label information
    label VARCHAR(50) NOT NULL, -- 'threat', 'safe', 'phishing', 'scam', etc.
    confidence FLOAT DEFAULT 0.0,
    
    -- Model information
    model_version VARCHAR(50),
    trained BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'inference', -- 'inference', 'feedback', 'manual'
    feedback_corrected BOOLEAN DEFAULT FALSE,
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trained_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional context
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for efficient querying
CREATE INDEX idx_training_data_account ON training_data(account_id);
CREATE INDEX idx_training_data_trained ON training_data(trained) WHERE trained = FALSE;
CREATE INDEX idx_training_data_label ON training_data(label);
CREATE INDEX idx_training_data_created ON training_data(created_at);
CREATE INDEX idx_training_data_model_version ON training_data(model_version);

-- Model metadata table to track versions and performance
CREATE TABLE IF NOT EXISTS model_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    
    -- Model information
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'logistic_regression', 'xgboost', etc.
    model_path VARCHAR(255),
    
    -- Performance metrics
    accuracy FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    
    -- Training info
    training_samples INTEGER DEFAULT 0,
    feature_dim INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT FALSE,
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_trained_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_model_metadata_account ON model_metadata(account_id);
CREATE INDEX idx_model_metadata_active ON model_metadata(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_model_metadata_version ON model_metadata(model_version);

-- RLS Policies
ALTER TABLE training_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metadata ENABLE ROW LEVEL SECURITY;

-- Training data policies
CREATE POLICY training_data_select_policy ON training_data
    FOR SELECT
    USING (account_id::text = current_setting('request.account_id', TRUE));

CREATE POLICY training_data_insert_policy ON training_data
    FOR INSERT
    WITH CHECK (account_id::text = current_setting('request.account_id', TRUE));

CREATE POLICY training_data_update_policy ON training_data
    FOR UPDATE
    USING (account_id::text = current_setting('request.account_id', TRUE));

-- Model metadata policies
CREATE POLICY model_metadata_select_policy ON model_metadata
    FOR SELECT
    USING (account_id::text = current_setting('request.account_id', TRUE) OR account_id IS NULL);

CREATE POLICY model_metadata_insert_policy ON model_metadata
    FOR INSERT
    WITH CHECK (account_id::text = current_setting('request.account_id', TRUE) OR account_id IS NULL);

CREATE POLICY model_metadata_update_policy ON model_metadata
    FOR UPDATE
    USING (account_id::text = current_setting('request.account_id', TRUE) OR account_id IS NULL);

-- Comments
COMMENT ON TABLE training_data IS 'Stores feature vectors and labels for online learning';
COMMENT ON TABLE model_metadata IS 'Tracks model versions and performance metrics';
COMMENT ON COLUMN training_data.features IS 'JSON array of feature values (embeddings + extracted features)';
COMMENT ON COLUMN training_data.trained IS 'Whether this sample has been used for training';
