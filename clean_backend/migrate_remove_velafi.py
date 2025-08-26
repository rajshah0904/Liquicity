#!/usr/bin/env python3
"""
Database migration script to remove VelaFi-related columns and requirements fields
This script should be run once to clean up the database schema after model changes.
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://liquicity_user:Liquicity2025!@localhost:5432/liquicity_db")

def migrate_database():
    """Remove VelaFi-related columns and requirements fields from existing tables"""
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.begin() as conn:
            logger.info("Starting database migration to remove VelaFi and requirements fields...")
            
            # Check if tables exist before trying to modify them
            tables_to_check = ['bridge_customers', 'kyc_states']
            
            for table_name in tables_to_check:
                # Check if table exists
                table_exists = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    );
                """)).scalar()
                
                if not table_exists:
                    logger.info(f"Table {table_name} does not exist, skipping...")
                    continue
                
                logger.info(f"Processing table: {table_name}")
                
                if table_name == 'bridge_customers':
                    # Remove requirements fields from bridge_customers table
                    columns_to_remove = ['future_requirements_due', 'requirements_due']
                    
                    for column in columns_to_remove:
                        # Check if column exists
                        column_exists = conn.execute(text(f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.columns 
                                WHERE table_name = '{table_name}' AND column_name = '{column}'
                            );
                        """)).scalar()
                        
                        if column_exists:
                            logger.info(f"Dropping column {column} from {table_name}")
                            conn.execute(text(f"ALTER TABLE {table_name} DROP COLUMN {column}"))
                        else:
                            logger.info(f"Column {column} does not exist in {table_name}, skipping...")
                
                elif table_name == 'kyc_states':
                    # Remove VelaFi-related fields from kyc_states table
                    columns_to_remove = [
                        'requires_velafi',
                        'velafi_merchant_id', 
                        'velafi_status',
                        'velafi_kyc_link',
                        'velafi_raw_metadata'
                    ]
                    
                    for column in columns_to_remove:
                        # Check if column exists
                        column_exists = conn.execute(text(f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.columns 
                                WHERE table_name = '{table_name}' AND column_name = '{column}'
                            );
                        """)).scalar()
                        
                        if column_exists:
                            logger.info(f"Dropping column {column} from {table_name}")
                            conn.execute(text(f"ALTER TABLE {table_name} DROP COLUMN {column}"))
                        else:
                            logger.info(f"Column {column} does not exist in {table_name}, skipping...")
            
            logger.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            logger.info("Verifying migration...")
            
            # Check bridge_customers table structure
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bridge_customers'
                ORDER BY column_name;
            """))
            
            bridge_columns = [row[0] for row in result.fetchall()]
            logger.info(f"bridge_customers columns: {bridge_columns}")
            
            # Check kyc_states table structure
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'kyc_states'
                ORDER BY column_name;
            """))
            
            kyc_columns = [row[0] for row in result.fetchall()]
            logger.info(f"kyc_states columns: {kyc_columns}")
            
            # Verify VelaFi columns are gone
            velafi_columns = [col for col in kyc_columns if 'velafi' in col.lower()]
            requirements_columns = [col for col in bridge_columns if 'requirements' in col.lower()]
            
            if velafi_columns:
                logger.warning(f"VelaFi columns still exist: {velafi_columns}")
                return False
            
            if requirements_columns:
                logger.warning(f"Requirements columns still exist: {requirements_columns}")
                return False
            
            logger.info("Migration verification successful!")
            return True
            
    except Exception as e:
        logger.error(f"Migration verification failed: {e}")
        return False

if __name__ == "__main__":
    print("Liquicity Database Migration - Remove VelaFi and Requirements Fields")
    print("=" * 60)
    
    # Ask for confirmation
    response = input("This will modify your database schema. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify migration
        verify_migration()
        print("\nMigration completed successfully!")
        print("You can now restart your backend application.")
    else:
        print("\nMigration failed! Please check the logs above.")
        sys.exit(1)