"""
Apply privacy settings migration

This script adds the allow_training_data and consent_verified columns
to enable user control over data usage for model training.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("Privacy Settings Migration")
print("=" * 70)
print()
print("This migration adds privacy controls for training data consent.")
print()
print("Database changes:")
print("  1. Add 'allow_training_data' column to accounts table (default: FALSE)")
print("  2. Add 'training_consent_at' timestamp to accounts table")
print("  3. Add 'consent_verified' column to training_data table")
print("  4. Create indexes for efficient filtering")
print()
print("To apply this migration:")
print("  1. Open your Supabase dashboard (https://app.supabase.com)")
print("  2. Navigate to: SQL Editor")
print("  3. Copy the contents of: migrations/003_privacy_training_consent.sql")
print("  4. Paste and execute in the SQL Editor")
print()
print("=" * 70)
print()

# Read and display migration SQL
migration_path = backend_dir / "migrations" / "003_privacy_training_consent.sql"

if migration_path.exists():
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("Migration SQL Preview:")
    print("-" * 70)
    print(sql_content[:500] + "..." if len(sql_content) > 500 else sql_content)
    print("-" * 70)
    print()
    print(f"Full migration file: {migration_path}")
else:
    print(f"[ERROR] Migration file not found: {migration_path}")
    sys.exit(1)

print()
print("After applying the migration:")
print("  - Users can enable/disable training data in Settings")
print("  - Only consented data will be used for model training")
print("  - Default is DISABLED for privacy protection")
print()
print("API Endpoints added:")
print("  - GET  /api/ml/privacy - Get current privacy settings")
print("  - POST /api/ml/privacy - Update privacy settings")
print()
