# Privacy & Training Data Consent

## Overview

Guardian respects user privacy and provides full control over how your data is used. This document explains the privacy controls for machine learning model training.

## Privacy-First Design

### Default Setting: **DISABLED**
- By default, NO user data is used for training
- Users must explicitly opt-in to contribute their data
- This ensures privacy protection out of the box

### What Gets Stored

When training data consent is **ENABLED**:
- ✅ Feature vectors (mathematical representations)
- ✅ Classification labels and confidence scores
- ✅ Metadata about the analysis
- ❌ **NOT** the raw text content (for privacy)

When training data consent is **DISABLED**:
- ❌ Nothing is stored for training
- ✅ Analysis still works normally
- ✅ Results are still returned

## User Controls

### Settings UI

Located in **Settings → Privacy & Data Usage**:

```
┌─────────────────────────────────────────┐
│  Privacy & Data Usage                   │
├─────────────────────────────────────────┤
│                                         │
│  🔒 Training Data Consent               │
│                                         │
│  Status: [Enabled/Disabled]             │
│                                         │
│  Your data is [being used / NOT being  │
│  used] for training...                  │
│                                         │
│  [Disable Training Data] button         │
│                                         │
│  ℹ️ How it works:                       │
│  • Features (not raw text) stored       │
│  • Data remains encrypted & isolated    │
│  • Improves detection accuracy          │
│  • Can disable anytime                  │
│                                         │
└─────────────────────────────────────────┘
```

### API Endpoints

#### Get Privacy Settings
```bash
GET /api/ml/privacy
Headers:
  X-API-Key: your_api_key

Response:
{
  "allow_training_data": false,
  "training_consent_at": "2025-12-09T10:30:00Z",
  "message": "Privacy settings retrieved successfully"
}
```

#### Update Privacy Settings
```bash
POST /api/ml/privacy
Headers:
  X-API-Key: your_api_key
  Content-Type: application/json

Body:
{
  "allow_training_data": true
}

Response:
{
  "allow_training_data": true,
  "training_consent_at": "2025-12-09T10:35:00Z",
  "message": "Training data usage enabled. Your data will help improve model accuracy."
}
```

## Technical Implementation

### Database Schema

**Accounts Table:**
```sql
ALTER TABLE accounts 
ADD COLUMN allow_training_data BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN training_consent_at TIMESTAMPTZ;
```

**Training Data Table:**
```sql
ALTER TABLE training_data
ADD COLUMN consent_verified BOOLEAN NOT NULL DEFAULT FALSE;
```

### Backend Logic

1. **Before Storing Training Data:**
```python
# Check user consent
consent_result = supabase.table("accounts")
    .select("allow_training_data")
    .eq("id", str(account_id))
    .execute()

consent_verified = consent_result.data[0].get("allow_training_data", False)

# Only store if consent granted
if consent_verified:
    store_training_sample(..., consent_verified=True)
```

2. **During Training:**
```python
# Only query consent-verified data
query = supabase.table('training_data')
    .select('*')
    .eq('trained', False)
    .eq('consent_verified', True)  # Critical filter
```

### Frontend Component

Located in: `frontend/src/pages/Settings.tsx`

Key features:
- Toggle switch for enable/disable
- Clear status indicators
- Last updated timestamp
- Informational tooltip about data usage

## Security & Privacy Guarantees

### 1. Opt-In Only
- Default is DISABLED
- Users must actively choose to enable
- Clear explanation provided before enabling

### 2. Account Isolation
- Data is scoped to individual accounts
- Row Level Security (RLS) policies enforced
- No cross-account data leakage

### 3. Feature Vectors Only
- Raw text is NOT stored in database
- Only mathematical features stored
- Cannot reverse-engineer original text

### 4. Immediate Effect
- Changes take effect immediately
- Future analyses respect new setting
- Past data remains unchanged

### 5. Audit Trail
- `training_consent_at` timestamp recorded
- Every data record has `consent_verified` flag
- Full transparency and traceability

## Migration Guide

### Step 1: Apply Database Migration

```bash
# Run migration helper
python apply_privacy_migration.py

# Or manually in Supabase SQL Editor:
# Execute: migrations/003_privacy_training_consent.sql
```

### Step 2: Verify Backend Integration

Check that ML router is registered:
```python
# In app/main.py
from app.routes import health, analyze, stats, keys, ml
app.include_router(ml.router)
```

### Step 3: Test Privacy Endpoints

```bash
# Get current settings
curl -X GET http://localhost:8000/api/ml/privacy \
  -H "X-API-Key: your_key"

# Enable training data
curl -X POST http://localhost:8000/api/ml/privacy \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"allow_training_data": true}'
```

### Step 4: Verify Frontend UI

1. Navigate to Settings page
2. Scroll to "Privacy & Data Usage" section
3. Toggle training data consent
4. Verify status updates correctly

## User Communication

### When Users Enable Training Data

Show message:
> "Training data usage enabled. Your data will help improve model accuracy."

### When Users Disable Training Data

Show message:
> "Training data usage disabled. Your data will not be used for training."

### In Settings Page

Explanation text:
```
Control how your data is used to improve our machine learning models

When enabled:
• Text features (not raw text) are stored for model training
• Your data remains encrypted and isolated to your account
• Helps improve detection accuracy through machine learning
• You can disable this at any time
• Only applies to future analyses (doesn't affect past data)
```

## Compliance Considerations

### GDPR Compliance
- ✅ Explicit consent required
- ✅ Easy to withdraw consent
- ✅ Clear explanation of data usage
- ✅ Data minimization (features only)
- ✅ Account isolation and security

### Best Practices
- Default to most privacy-protective setting
- Provide clear, non-technical explanations
- Allow easy opt-out at any time
- Track consent timestamp for audit
- Only use consented data for training

## FAQ

**Q: What happens if I disable training data?**
A: Your analyses continue working normally. Only future data won't be stored for training.

**Q: Can I delete previously stored training data?**
A: Yes, contact support or use the data deletion API (future feature).

**Q: Is my raw text stored in the database?**
A: No, only mathematical feature vectors are stored, not the original text.

**Q: Who can access my training data?**
A: Only you via your account. RLS policies prevent cross-account access.

**Q: Does disabling affect model accuracy for my analyses?**
A: No, the static classifiers continue working. You just won't benefit from personalized online learning.

**Q: Can I see what data is stored?**
A: Yes, query the `training_data` table filtered by your `account_id`.

## Monitoring & Analytics

### Track Consent Rates

```sql
-- Percentage of users who enabled training data
SELECT 
  COUNT(CASE WHEN allow_training_data THEN 1 END)::float / COUNT(*) * 100 as consent_rate_pct
FROM accounts;
```

### Training Data Volume

```sql
-- Count of consent-verified training samples
SELECT 
  COUNT(*) as total_samples,
  COUNT(CASE WHEN consent_verified THEN 1 END) as consented_samples
FROM training_data;
```

## Support

For questions or issues with privacy settings:
- Open GitHub issue
- Contact: privacy@guardian-security.com
- Documentation: /docs/privacy

---

**Last Updated:** December 9, 2025  
**Version:** 1.0.0
