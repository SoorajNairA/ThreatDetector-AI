# Privacy Consent - Quick Reference

## For Developers

### ⚡ Quick Start

1. **Apply Migration**
   ```bash
   # In Supabase SQL Editor
   Execute: migrations/003_privacy_training_consent.sql
   ```

2. **Test Privacy Endpoints**
   ```bash
   # Get settings
   curl http://localhost:8000/api/ml/privacy -H "X-API-Key: key"
   
   # Enable training
   curl -X POST http://localhost:8000/api/ml/privacy \
     -H "X-API-Key: key" -H "Content-Type: application/json" \
     -d '{"allow_training_data": true}'
   ```

3. **Verify in UI**
   - Navigate to `/settings`
   - Scroll to "Privacy & Data Usage"
   - Toggle should work

---

## 🔑 Key Concepts

### Default State
```
allow_training_data = FALSE (privacy-first)
```

### Consent Check (Before Storage)
```python
consent = supabase.table("accounts")
    .select("allow_training_data")
    .eq("id", account_id)
    .execute()

if consent.data[0].get("allow_training_data"):
    store_training_sample(..., consent_verified=True)
```

### Training Filter
```python
query = supabase.table('training_data')
    .eq('trained', False)
    .eq('consent_verified', True)  # Only consented data
```

---

## 📋 Checklist

### Backend
- [x] `ml.py` - Added privacy endpoints
- [x] `training_service.py` - Added consent parameter
- [x] `ml.py` - Consent check in analyze endpoint
- [x] Migration SQL created

### Frontend
- [x] `Settings.tsx` - Privacy UI section
- [x] Toggle enable/disable
- [x] Status indicators
- [x] API integration

### Database
- [ ] Apply migration (manual step)
- [x] Schema designed
- [x] Indexes planned

---

## 🛠️ Files Modified

```
backend/
  ├── app/routes/ml.py                    [MODIFIED]
  ├── app/services/training_service.py    [MODIFIED]
  └── migrations/
      └── 003_privacy_training_consent.sql [NEW]

frontend/
  └── src/pages/Settings.tsx              [MODIFIED]
```

---

## 🔒 Privacy Guarantees

1. **Opt-In**: Default OFF, must enable
2. **Verified**: Checked on every request
3. **Filtered**: Training uses only consented data
4. **Isolated**: RLS per account
5. **Minimal**: Features only, no raw text

---

## 📊 Monitoring Queries

### Consent Rate
```sql
SELECT 
  COUNT(CASE WHEN allow_training_data THEN 1 END)::float / COUNT(*) * 100
FROM accounts;
```

### Consented Data Volume
```sql
SELECT COUNT(*) FROM training_data WHERE consent_verified = TRUE;
```

---

## 🚀 Deployment

1. Apply migration in Supabase
2. Backend auto-deploys (already integrated)
3. Frontend rebuild + deploy
4. Test privacy endpoints
5. Verify UI toggle works

---

## 📖 Full Docs

- **PRIVACY_CONSENT.md** - Complete documentation
- **PRIVACY_IMPLEMENTATION_SUMMARY.md** - Detailed summary
- **PRIVACY_FLOW_DIAGRAM.md** - Visual flow

---

## ✅ Status

**Implementation:** Complete  
**Testing:** Ready  
**Documentation:** Complete  
**Migration:** Ready to apply
