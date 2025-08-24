from pydantic_settings import BaseSettings
from typing import List
import os
import json
import boto3


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = ""
    DATABASE_HOST: str = os.getenv("DATABASE_ENDPOINT", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "shoppingcart")
    DATABASE_USER: str = ""
    DATABASE_PASSWORD: str = ""
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # AWS settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_database_credentials()
        self._build_database_url()
    
    def _load_database_credentials(self):
        """Load database credentials from AWS Secrets Manager."""
        try:
            # Try to get credentials from environment (for local development)
            db_credentials = os.getenv("DATABASE_CREDENTIALS")
            if db_credentials:
                creds = json.loads(db_credentials)
                self.DATABASE_USER = creds.get("username", "cartadmin")
                self.DATABASE_PASSWORD = creds.get("password", "")
                return
            
            # Try to get from AWS Secrets Manager (for production)
            session = boto3.Session()
            secrets_client = session.client('secretsmanager', region_name=self.AWS_REGION)
            
            # Get the secret ARN from environment or use default pattern
            secret_name = os.getenv("DATABASE_SECRET_ARN", "shopping-cart-db-credentials")
            
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret = json.loads(response['SecretString'])
            
            self.DATABASE_USER = secret.get("username", "cartadmin")
            self.DATABASE_PASSWORD = secret.get("password", "")
            
        except Exception as e:
            print(f"Warning: Could not load database credentials: {e}")
            # Fallback to default values for local development
            self.DATABASE_USER = "cartadmin"
            self.DATABASE_PASSWORD = "password"
    
    def _build_database_url(self):
        """Build database URL from components."""
        self.DATABASE_URL = (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    class Config:
        env_file = ".env"


settings = Settings()
