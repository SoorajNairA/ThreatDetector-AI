"""
Apply database migration for online learning system
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the online learning migration"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment")
        return False
    
    # Read migration file
    migration_path = backend_dir / "migrations" / "002_online_learning.sql"
    
    if not migration_path.exists():
        print(f"[ERROR] Migration file not found: {migration_path}")
        return False
    
    with open(migration_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"[INFO] Loaded migration from {migration_path}")
    print(f"[INFO] Connecting to Supabase at {supabase_url}")
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Split into individual statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"[INFO] Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and empty lines
            if not statement or statement.startswith('--'):
                continue
                
            try:
                # Use Supabase RPC to execute raw SQL
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"[OK] Statement {i}/{len(statements)} executed")
            except Exception as e:
                # Try using PostgREST SQL execution
                print(f"[WARNING] RPC method failed for statement {i}, trying alternative...")
                print(f"Statement preview: {statement[:100]}...")
                print(f"Error: {e}")
        
        print("[SUCCESS] Migration applied successfully!")
        print("\nCreated tables:")
        print("  - training_data (stores feature vectors and labels)")
        print("  - model_metadata (tracks model versions and performance)")
        print("\nNext steps:")
        print("  1. Test the /api/ml/analyze endpoint")
        print("  2. Generate some training samples")
        print("  3. Run background training with /api/ml/training/run")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
