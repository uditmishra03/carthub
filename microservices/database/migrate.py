#!/usr/bin/env python3
"""
Database migration script for Carthub
Handles schema creation and data migrations
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import boto3
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment or AWS Secrets Manager"""
    # Try environment variables first
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # Get from AWS Secrets Manager
    secret_arn = os.getenv('DB_SECRET_ARN')
    if not secret_arn:
        raise ValueError("DATABASE_URL or DB_SECRET_ARN must be set")
    
    try:
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(response['SecretString'])
        
        username = secret['username']
        password = secret['password']
        host = secret.get('host', 'localhost')
        port = secret.get('port', 5432)
        database = secret.get('dbname', 'carthub')
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    except Exception as e:
        logger.error(f"Failed to get database credentials: {e}")
        raise

def create_tables(engine):
    """Create database tables"""
    logger.info("Creating database tables...")
    
    # Shopping cart tables
    cart_table_sql = """
    CREATE TABLE IF NOT EXISTS carts (
        id SERIAL PRIMARY KEY,
        customer_id VARCHAR(255) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cart_items_table_sql = """
    CREATE TABLE IF NOT EXISTS cart_items (
        id SERIAL PRIMARY KEY,
        cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
        product_id VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(cart_id, product_id)
    );
    """
    
    # Orders table for checkout functionality
    orders_table_sql = """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        customer_id VARCHAR(255) NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    order_items_table_sql = """
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        product_id VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        quantity INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create indexes
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_carts_customer_id ON carts(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);",
        "CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);",
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);"
    ]
    
    # Update triggers for timestamps
    trigger_sql = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    DROP TRIGGER IF EXISTS update_carts_updated_at ON carts;
    CREATE TRIGGER update_carts_updated_at 
        BEFORE UPDATE ON carts 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_cart_items_updated_at ON cart_items;
    CREATE TRIGGER update_cart_items_updated_at 
        BEFORE UPDATE ON cart_items 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
    CREATE TRIGGER update_orders_updated_at 
        BEFORE UPDATE ON orders 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    with engine.connect() as conn:
        # Create tables
        conn.execute(text(cart_table_sql))
        conn.execute(text(cart_items_table_sql))
        conn.execute(text(orders_table_sql))
        conn.execute(text(order_items_table_sql))
        
        # Create indexes
        for index_sql in indexes_sql:
            conn.execute(text(index_sql))
        
        # Create triggers
        conn.execute(text(trigger_sql))
        
        conn.commit()
    
    logger.info("Database tables created successfully")

def seed_data(engine):
    """Seed initial data if needed"""
    logger.info("Seeding initial data...")
    
    # Add any initial data here if needed
    # For now, we'll just log that seeding is complete
    
    logger.info("Data seeding completed")

def main():
    """Main migration function"""
    try:
        logger.info("Starting database migration...")
        
        # Get database URL
        database_url = get_database_url()
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"Connected to PostgreSQL: {version}")
        
        # Create tables
        create_tables(engine)
        
        # Seed data
        seed_data(engine)
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
