from pydantic import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"
    STORAGE_BUCKET: str = "pkh-legal-brain"
    AWS_REGION: str = "eu-west-2"
    USE_TEXTRACT: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://pkh:pkh_password_change_me@postgres:5432/pkh_legal_brain"
    
    # Optional S3-compatible storage (Hetzner)
    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    
    # LLM keys
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    
    # Vector DB (choose one)
    PINECONE_API_KEY: str | None = None
    PINECONE_INDEX: str | None = None
    PG_DSN: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
