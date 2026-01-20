"""
Configuration management for the Loan & Lease Contract AI backend.
Centralizes all environment variables and settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # OCR Configuration
    POPPLER_PATH: Optional[str] = os.getenv("POPPLER_PATH")
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD")
    
    # Security
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:8501,http://127.0.0.1:8501"
    )
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate required settings and return list of missing/invalid settings.
        Returns empty list if all required settings are present.
        """
        errors = []
        
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is required for AI features")
        
        return errors
    
    @classmethod
    def get_allowed_origins_list(cls) -> list[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in cls.ALLOWED_ORIGINS.split(",") if origin.strip()]


# Global settings instance
settings = Settings()
