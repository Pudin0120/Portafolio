# Migration Fix - Task Hierarchy

## Problem Identified
The deployment workflow was trying to run the migration script without the correct path:
- **Wrong**: `python migrate_task_hierarchy.py`
- **Correct**: `python scripts/migrate_task_hierarchy.py`

## Solution Applied
Updated `.github/workflows/deploy.yml` to use the correct path for the migration script.

## What Happens on Next Deploy

### 1. **Automatic Migration**
The deployment workflow will:
1. Pull the latest code
2. Build and start containers
3. Run `python scripts/migrate_task_hierarchy.py` inside the backend container
4. The script will check if columns exist and add them if needed

### 2. **Migration Script Safety**
The migration script (`scripts/migrate_task_hierarchy.py`) is idempotent:
- OK Checks if columns already exist
- OK Only adds missing columns
- OK Safe to run multiple times
- OK Creates indexes for performance

### 3. **Columns Added**
The migration adds these columns to the `tasks` table:
- `parent_composite_id` (UUID, FK to products)
- `composite_task_slot` (INTEGER)
- `composite_total_slots` (INTEGER)

## Validation Steps After Deploy

### Check Migration Success
```bash
# SSH into VPS
ssh <user>@<host>

# Check migration logs
cd /root/apps/serviperfiles-backend
docker-compose -f docker-compose.prod.yml logs backend | grep -A 20 "Migracion"

# Verify columns exist
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U desarrollo -d desarrollo -c "\d tasks"
```

### Test API Response
```bash
# Get works and verify hierarchy fields
curl -X GET "https://api.yourdomin.com/api/v1/works" \
  -H "Authorization: Bearer <token>"

# Check that tasks have hierarchy fields:
# - parent_composite_id
# - composite_task_slot
# - composite_total_slots
```

## If Migration Fails

If the automatic migration fails, you can run it manually:

```bash
# SSH into VPS
ssh <user>@<host>
cd /root/apps/serviperfiles-backend

# Run migration manually
docker-compose -f docker-compose.prod.yml exec backend python scripts/migrate_task_hierarchy.py

# Restart backend to apply changes
docker-compose -f docker-compose.prod.yml restart backend
```

## Files Updated
- `.github/workflows/deploy.yml` - Fixed migration script path
- This documentation file

## Next Steps
1. Commit and push this fix
2. Wait for automatic deployment
3. Verify migration runs successfully
4. Test that new tasks have hierarchy fields in DB and API

## Deployment Workflow Summary
```yaml
1. Checkout code from GitHub
2. Update code on VPS
3. Create .env and firebase-credentials.json
4. Build and start containers (docker-compose up)
5.  Run migration: python scripts/migrate_task_hierarchy.py
6. Show logs and verify status
7. Clean up old Docker images
```

The migration runs **inside the backend container** so it has access to:
- SQLAlchemy models
- Database connection via DATABASE_URL
- All Python dependencies
