# Database Migration Instructions

## Overview
The KYC system has been updated to remove VelaFi verification requirements and simplify the Bridge API integration. This requires a database schema update to remove unused columns.

## What Changed

### Backend Models
1. **BridgeCustomer model** - Removed fields:
   - `future_requirements_due`
   - `requirements_due`

2. **KycState model** - Removed VelaFi fields:
   - `requires_velafi`
   - `velafi_merchant_id`
   - `velafi_status`
   - `velafi_kyc_link`
   - `velafi_raw_metadata`

### KYC Flow Changes
- Removed all VelaFi integration code
- Simplified to use only Bridge API with region-specific payloads
- Updated frontend to remove VelaFi references

## Migration Steps

### Option 1: Automatic Migration (Recommended)
Run the provided migration script:

```bash
cd /Users/hadeermotair/Liquicty/Liquicity
source venv/bin/activate
python clean_backend/migrate_remove_velafi.py
```

This script will:
- Check for existing tables
- Remove obsolete columns safely
- Verify the migration was successful

### Option 2: Manual Database Update
If you prefer to run the SQL manually:

```sql
-- Remove requirements fields from bridge_customers
ALTER TABLE bridge_customers DROP COLUMN IF EXISTS future_requirements_due;
ALTER TABLE bridge_customers DROP COLUMN IF EXISTS requirements_due;

-- Remove VelaFi fields from kyc_states  
ALTER TABLE kyc_states DROP COLUMN IF EXISTS requires_velafi;
ALTER TABLE kyc_states DROP COLUMN IF EXISTS velafi_merchant_id;
ALTER TABLE kyc_states DROP COLUMN IF EXISTS velafi_status;
ALTER TABLE kyc_states DROP COLUMN IF EXISTS velafi_kyc_link;
ALTER TABLE kyc_states DROP COLUMN IF EXISTS velafi_raw_metadata;
```

## After Migration

1. **Restart the backend application**
   ```bash
   # If running with Docker
   docker-compose restart backend
   
   # If running locally
   # Kill the uvicorn process and restart
   ```

2. **Verify the changes**
   - The KYC flow now uses only Bridge API
   - All regions (US, EU, International) use the same verification process
   - No more dual KYC requirements

## New Bridge API Integration

The updated system now uses region-specific payloads for Bridge customer creation:

- **US**: SSN + driver's license/passport
- **International** (Mexico, Brazil, Colombia, Peru, Argentina): Enhanced payload with employment info, payment volumes, etc.
- **Europe**: Passport + proof of address documents

## Rollback Instructions

If you need to rollback the changes, you would need to:

1. Restore the original model definitions
2. Recreate the dropped columns
3. Restore VelaFi integration code

Note: This is not recommended as it would require significant code changes.

## Support

If you encounter any issues during migration:

1. Check the migration script logs for error details
2. Verify database connectivity
3. Ensure you have proper database permissions
4. Contact support if the migration fails