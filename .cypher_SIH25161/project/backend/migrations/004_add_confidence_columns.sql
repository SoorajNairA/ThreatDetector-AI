-- Add confidence score columns to threats table
-- These track model prediction confidence for success rate calculation

ALTER TABLE threats
ADD COLUMN IF NOT EXISTS ai_confidence FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS intent_confidence FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS style_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS url_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS keyword_score FLOAT DEFAULT 0.0;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_threats_confidence ON threats(ai_confidence, intent_confidence);

-- Update existing records with default confidence based on risk score
-- High risk = high confidence, low risk = low confidence
UPDATE threats 
SET 
    ai_confidence = CASE 
        WHEN risk_level = 'HIGH' THEN 0.85
        WHEN risk_level = 'MEDIUM' THEN 0.65
        WHEN risk_level = 'LOW' THEN 0.45
        ELSE 0.50
    END,
    intent_confidence = CASE 
        WHEN risk_level = 'HIGH' THEN 0.80
        WHEN risk_level = 'MEDIUM' THEN 0.60
        WHEN risk_level = 'LOW' THEN 0.40
        ELSE 0.50
    END,
    style_score = 0.5,
    url_score = 0.0,
    keyword_score = 0.0
WHERE ai_confidence IS NULL OR intent_confidence IS NULL;
