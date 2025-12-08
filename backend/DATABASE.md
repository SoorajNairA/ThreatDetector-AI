# Database Schema Documentation

## Supabase Threats Table

### Table: `threats`

Stores all analyzed threat records with risk assessments and detailed analysis.

### Schema Definition

```sql
CREATE TABLE threats (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Content
  text TEXT NOT NULL,
  
  -- Risk assessment
  risk_level TEXT NOT NULL CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
  risk_score FLOAT NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
  
  -- Classification results
  intent TEXT,                    -- Classification: phishing, spam, scam, unknown
  ai_generated BOOLEAN,           -- Whether text appears AI-generated
  
  -- Metadata
  actor TEXT,                     -- User/actor identifier (if available)
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Detailed scores
  style_score FLOAT,              -- Stylometry analysis score
  url_detected BOOLEAN DEFAULT FALSE,
  domains TEXT[],                 -- Array of URLs found in text
  keywords TEXT[],                -- Array of threat keywords detected
  
  -- System
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes

```sql
-- Optimize queries by risk level
CREATE INDEX idx_threats_risk_level ON threats(risk_level);

-- Optimize time-based queries
CREATE INDEX idx_threats_timestamp ON threats(timestamp DESC);

-- Optimize actor-based queries
CREATE INDEX idx_threats_actor ON threats(actor);
```

### Realtime Configuration

```sql
-- Enable Realtime for frontend auto-updates
ALTER PUBLICATION supabase_realtime ADD TABLE threats;
```

### Column Details

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `id` | UUID | Yes | Auto-generated unique identifier |
| `text` | TEXT | Yes | Original text content analyzed |
| `risk_level` | TEXT | Yes | HIGH, MEDIUM, or LOW |
| `risk_score` | FLOAT | Yes | Computed risk score (0.0 to 1.0) |
| `intent` | TEXT | No | Detected intent: phishing, spam, scam, unknown |
| `ai_generated` | BOOLEAN | No | True if text appears AI-generated |
| `actor` | TEXT | No | User/actor identifier |
| `timestamp` | TIMESTAMPTZ | Yes | When analysis was performed |
| `style_score` | FLOAT | No | Stylometry analysis score |
| `url_detected` | BOOLEAN | No | True if URLs found in text |
| `domains` | TEXT[] | No | Array of domains/URLs found |
| `keywords` | TEXT[] | No | Array of threat keywords detected |
| `created_at` | TIMESTAMPTZ | No | Record creation time (system) |

### Example Record

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Click here to verify your bank account!",
  "risk_level": "HIGH",
  "risk_score": 0.84,
  "intent": "phishing",
  "ai_generated": false,
  "actor": "user-123",
  "timestamp": "2025-12-08T10:30:00Z",
  "style_score": 0.6,
  "url_detected": true,
  "domains": ["http://suspicious-site.com"],
  "keywords": ["click", "verify", "bank", "account"],
  "created_at": "2025-12-08T10:30:00Z"
}
```

### Query Examples

**Get all high-risk threats:**
```sql
SELECT * FROM threats 
WHERE risk_level = 'HIGH' 
ORDER BY timestamp DESC;
```

**Get statistics:**
```sql
SELECT 
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE risk_level = 'HIGH') as high,
  COUNT(*) FILTER (WHERE risk_level = 'MEDIUM') as medium,
  COUNT(*) FILTER (WHERE risk_level = 'LOW') as low,
  COUNT(DISTINCT actor) as unique_actors,
  MAX(timestamp) as last_detection
FROM threats;
```

**Get recent phishing attempts:**
```sql
SELECT * FROM threats
WHERE intent = 'phishing'
ORDER BY timestamp DESC
LIMIT 10;
```

### Row Level Security (Optional)

If you need multi-tenant security:

```sql
-- Enable RLS
ALTER TABLE threats ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own threats
CREATE POLICY "Users can view own threats"
ON threats FOR SELECT
USING (auth.uid()::text = actor);

-- Policy: Service role can do anything
CREATE POLICY "Service role full access"
ON threats FOR ALL
USING (auth.role() = 'service_role');
```

### Maintenance

**Archive old records:**
```sql
-- Archive threats older than 90 days
DELETE FROM threats 
WHERE timestamp < NOW() - INTERVAL '90 days';
```

**Analyze table performance:**
```sql
ANALYZE threats;
```

### Realtime Subscriptions

**Frontend can subscribe to new threats:**

```javascript
const supabase = createClient(url, anonKey)

supabase
  .channel('threats')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'threats' },
    (payload) => {
      console.log('New threat:', payload.new)
      // Update UI automatically
    }
  )
  .subscribe()
```

### Backup and Recovery

**Export threats:**
```sql
COPY threats TO '/path/to/backup.csv' WITH CSV HEADER;
```

**Import threats:**
```sql
COPY threats FROM '/path/to/backup.csv' WITH CSV HEADER;
```

---

**Note:** This schema is designed for the hackathon/demo but is production-ready with proper indexes and constraints.
