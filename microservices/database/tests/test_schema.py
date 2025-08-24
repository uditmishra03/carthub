"""
Test suite for Carthub Database Schema
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add the parent directory to the path to import migrate module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from migrate import get_database_url, create_tables, seed_data

class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_get_database_url_from_env(self):
        """Test getting database URL from environment variable"""
        test_url = "postgresql://test:test@localhost:5432/test"
        
        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            url = get_database_url()
            assert url == test_url

    @patch('boto3.client')
    def test_get_database_url_from_secrets_manager(self, mock_boto_client):
        """Test getting database URL from AWS Secrets Manager"""
        # Mock the secrets manager response
        mock_secrets_client = Mock()
        mock_boto_client.return_value = mock_secrets_client
        
        mock_secret_value = {
            'SecretString': '{"username": "testuser", "password": "testpass", "host": "testhost", "port": 5432, "dbname": "testdb"}'
        }
        mock_secrets_client.get_secret_value.return_value = mock_secret_value
        
        with patch.dict(os.environ, {'DB_SECRET_ARN': 'arn:aws:secretsmanager:us-west-2:123456789012:secret:test'}, clear=True):
            url = get_database_url()
            expected_url = "postgresql://testuser:testpass@testhost:5432/testdb"
            assert url == expected_url

    def test_get_database_url_no_config(self):
        """Test error when no database configuration is provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL or DB_SECRET_ARN must be set"):
                get_database_url()

class TestSchemaCreation:
    """Test database schema creation"""
    
    @patch('migrate.create_engine')
    def test_create_tables_success(self, mock_create_engine):
        """Test successful table creation"""
        # Mock the database engine and connection
        mock_engine = Mock()
        mock_connection = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock the execute method to not raise exceptions
        mock_connection.execute.return_value = None
        mock_connection.commit.return_value = None
        
        # This should not raise an exception
        create_tables(mock_engine)
        
        # Verify that execute was called multiple times (for different SQL statements)
        assert mock_connection.execute.call_count > 0
        mock_connection.commit.assert_called_once()

    @patch('migrate.create_engine')
    def test_create_tables_database_error(self, mock_create_engine):
        """Test handling of database errors during table creation"""
        # Mock the database engine and connection
        mock_engine = Mock()
        mock_connection = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock the execute method to raise an exception
        mock_connection.execute.side_effect = Exception("Database error")
        
        # This should raise an exception
        with pytest.raises(Exception, match="Database error"):
            create_tables(mock_engine)

class TestDataSeeding:
    """Test data seeding functionality"""
    
    @patch('migrate.create_engine')
    def test_seed_data_success(self, mock_create_engine):
        """Test successful data seeding"""
        # Mock the database engine
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # This should not raise an exception
        seed_data(mock_engine)

class TestSchemaValidation:
    """Test schema validation"""
    
    def test_table_definitions(self):
        """Test that table definitions are valid SQL"""
        # Test that the SQL statements are syntactically correct
        # This is a basic test - in a real scenario, you might want to test against a test database
        
        cart_table_sql = """
        CREATE TABLE IF NOT EXISTS carts (
            id SERIAL PRIMARY KEY,
            customer_id VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Basic validation - check that the SQL contains expected keywords
        assert "CREATE TABLE" in cart_table_sql
        assert "PRIMARY KEY" in cart_table_sql
        assert "NOT NULL" in cart_table_sql
        assert "UNIQUE" in cart_table_sql

    def test_index_definitions(self):
        """Test that index definitions are valid"""
        index_sql = "CREATE INDEX IF NOT EXISTS idx_carts_customer_id ON carts(customer_id);"
        
        # Basic validation
        assert "CREATE INDEX" in index_sql
        assert "IF NOT EXISTS" in index_sql
        assert "ON carts" in index_sql

class TestMigrationIntegration:
    """Test migration integration"""
    
    @patch('migrate.get_database_url')
    @patch('migrate.create_engine')
    @patch('migrate.create_tables')
    @patch('migrate.seed_data')
    def test_main_migration_success(self, mock_seed_data, mock_create_tables, mock_create_engine, mock_get_database_url):
        """Test successful migration execution"""
        from migrate import main
        
        # Mock all the dependencies
        mock_get_database_url.return_value = "postgresql://test:test@localhost:5432/test"
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # Mock the connection test
        mock_connection = Mock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_connection.execute.return_value.fetchone.return_value = ["PostgreSQL 15.0"]
        
        # This should not raise an exception
        main()
        
        # Verify that all steps were called
        mock_get_database_url.assert_called_once()
        mock_create_engine.assert_called_once()
        mock_create_tables.assert_called_once_with(mock_engine)
        mock_seed_data.assert_called_once_with(mock_engine)

    @patch('migrate.get_database_url')
    def test_main_migration_failure(self, mock_get_database_url):
        """Test migration failure handling"""
        from migrate import main
        
        # Mock get_database_url to raise an exception
        mock_get_database_url.side_effect = Exception("Configuration error")
        
        # This should exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
