# Privacy Consent Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        USER PRIVACY CONSENT SYSTEM                          │
└─────────────────────────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 1: USER OPENS SETTINGS PAGE                                         │
└───────────────────────────────────────────────────────────────────────────┘

    User navigates to: /settings
           ↓
    GET /api/ml/privacy
           ↓
    ┌─────────────────────────────┐
    │  Backend checks:            │
    │  - accounts.allow_training  │
    │  - training_consent_at      │
    └─────────────────────────────┘
           ↓
    Returns current status: DISABLED (default)


┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 2: USER ENABLES TRAINING DATA                                       │
└───────────────────────────────────────────────────────────────────────────┘

    User clicks: "Enable Training Data"
           ↓
    POST /api/ml/privacy
    { "allow_training_data": true }
           ↓
    ┌─────────────────────────────────────┐
    │  UPDATE accounts SET                │
    │    allow_training_data = TRUE       │
    │    training_consent_at = NOW()      │
    │  WHERE id = current_user            │
    └─────────────────────────────────────┘
           ↓
    Success: "Training data usage enabled..."


┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 3: USER ANALYZES TEXT                                               │
└───────────────────────────────────────────────────────────────────────────┘

    User sends text for analysis
           ↓
    POST /api/ml/analyze
    { "text": "...", "store_for_training": true }
           ↓
    ┌─────────────────────────────────────────┐
    │  1. Extract features                    │
    │  2. Get prediction                      │
    │  3. Return results immediately          │
    └─────────────────────────────────────────┘
           ↓
    ┌──────────────────────────────────────────────────────────┐
    │  4. Background Task: Check Consent                       │
    │     ┌─────────────────────────────────────────────┐     │
    │     │  SELECT allow_training_data                 │     │
    │     │  FROM accounts                              │     │
    │     │  WHERE id = current_user                    │     │
    │     └─────────────────────────────────────────────┘     │
    │              ↓                                           │
    │         consent = TRUE?                                 │
    │              ↓                                           │
    │         ┌────YES────┐        ┌────NO────┐              │
    │         │           │        │          │              │
    │    Store with       │        │   Skip   │              │
    │    consent_verified │        │  storage │              │
    │    = TRUE           │        │          │              │
    └──────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 4: BACKGROUND TRAINING                                              │
└───────────────────────────────────────────────────────────────────────────┘

    POST /api/ml/training/run
           ↓
    ┌──────────────────────────────────────────────────┐
    │  Query training data:                            │
    │                                                  │
    │  SELECT * FROM training_data                     │
    │  WHERE trained = FALSE                           │
    │    AND consent_verified = TRUE  ← Critical!      │
    │  ORDER BY created_at                             │
    │  LIMIT 1000                                      │
    └──────────────────────────────────────────────────┘
           ↓
    ┌─────────────────────────────┐
    │  Train model with:          │
    │  - Only consented data      │
    │  - Feature vectors          │
    │  - Verified labels          │
    └─────────────────────────────┘
           ↓
    Mark samples as trained


┌───────────────────────────────────────────────────────────────────────────┐
│  STEP 5: USER DISABLES TRAINING DATA                                      │
└───────────────────────────────────────────────────────────────────────────┘

    User clicks: "Disable Training Data"
           ↓
    POST /api/ml/privacy
    { "allow_training_data": false }
           ↓
    ┌─────────────────────────────────────┐
    │  UPDATE accounts SET                │
    │    allow_training_data = FALSE      │
    │    training_consent_at = NOW()      │
    │  WHERE id = current_user            │
    └─────────────────────────────────────┘
           ↓
    ┌───────────────────────────────────────────┐
    │  Future analyses:                         │
    │  - Still work normally                    │
    │  - Return predictions                     │
    │  - Do NOT store training data             │
    │  - consent_verified stays FALSE           │
    └───────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────────────┐
│  DATA FLOW COMPARISON                                                      │
└───────────────────────────────────────────────────────────────────────────┘

WITH CONSENT ENABLED (allow_training_data = TRUE):
─────────────────────────────────────────────────
  User Text
     ↓
  Feature Extraction → [19-dim vector]
     ↓                         ↓
  Prediction            INSERT training_data
  (returned)            consent_verified = TRUE
                              ↓
                        Used in training


WITH CONSENT DISABLED (allow_training_data = FALSE):
──────────────────────────────────────────────────
  User Text
     ↓
  Feature Extraction → [19-dim vector]
     ↓                         ↓
  Prediction              NOT STORED
  (returned)              


┌───────────────────────────────────────────────────────────────────────────┐
│  DATABASE STATE DIAGRAM                                                    │
└───────────────────────────────────────────────────────────────────────────┘

accounts table:
┌──────────┬────────────────────┬────────────────────┐
│ id       │ allow_training_data│ training_consent_at│
├──────────┼────────────────────┼────────────────────┤
│ user-123 │ FALSE (default)    │ NULL               │  ← New user
│ user-456 │ TRUE               │ 2025-12-09 10:30   │  ← Enabled
│ user-789 │ FALSE              │ 2025-12-09 11:45   │  ← Disabled
└──────────┴────────────────────┴────────────────────┘

training_data table:
┌───────────┬────────────┬──────────┬──────────────────┐
│ id        │ account_id │ features │ consent_verified │
├───────────┼────────────┼──────────┼──────────────────┤
│ sample-1  │ user-456   │ [0.1,..] │ TRUE             │  ← Can train
│ sample-2  │ user-789   │ [0.2,..] │ FALSE            │  ← Skip in training
│ sample-3  │ user-123   │ [0.3,..] │ FALSE            │  ← Skip in training
└───────────┴────────────┴──────────┴──────────────────┘
                                           ↑
                    Training query filters here:
                    WHERE consent_verified = TRUE


┌───────────────────────────────────────────────────────────────────────────┐
│  SECURITY & PRIVACY LAYERS                                                 │
└───────────────────────────────────────────────────────────────────────────┘

Layer 1: Default Privacy
┌──────────────────────────────────────────┐
│  allow_training_data = FALSE (default)   │
│  User must explicitly enable             │
└──────────────────────────────────────────┘

Layer 2: Consent Verification
┌──────────────────────────────────────────┐
│  Check consent before EVERY storage      │
│  Even if store_for_training = true       │
└──────────────────────────────────────────┘

Layer 3: Training Filter
┌──────────────────────────────────────────┐
│  WHERE consent_verified = TRUE           │
│  No unconsented data in training         │
└──────────────────────────────────────────┘

Layer 4: Account Isolation
┌──────────────────────────────────────────┐
│  Row Level Security (RLS)                │
│  account_id scoped queries               │
└──────────────────────────────────────────┘

Layer 5: Data Minimization
┌──────────────────────────────────────────┐
│  Feature vectors only (not raw text)     │
│  Cannot reverse-engineer original        │
└──────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────────────┐
│  SUMMARY                                                                   │
└───────────────────────────────────────────────────────────────────────────┘

✅ Privacy by Default:  allow_training_data = FALSE
✅ Explicit Consent:    User must enable in Settings
✅ Real-time Check:     Verified on every request
✅ Training Filter:     Only consented data used
✅ Audit Trail:         Timestamps + flags recorded
✅ Data Minimization:   Features only, not raw text
✅ Account Isolation:   RLS enforced
✅ Immediate Effect:    Changes apply instantly

Result: Users have complete control over their data privacy.
