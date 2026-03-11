# ─────────────────────────────────────────────────────────────────
# config.py
# ─────────────────────────────────────────────────────────────────
# Centralized configuration for openvista-exlorer, using Pydantic
# ─────────────────────────────────────────────────────────────────

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Application Settings
class AppSettings(BaseSettings):
    name: str = "openvista-exp (config.py)"
    version: str = "0.1.0 (config.py)"
    port: int = 8010
    debug: bool = True
    log_level: str = "INFO"

    # Pydantic will look for APP_NAME, APP_VERSION, APP_LOG_LEVEL, etc.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix='APP_',
        extra="ignore"
    )


# PostgreSQL Database Settings
class PostgresSettings(BaseSettings):
    """
    Database configuration using Pydantic Settings.
    To be implemented in upcoming development phase.

    Will include:
    - host, port, db, user, password fields
    - Validator for required password
    - Computed property for DATABASE_URL connection string
    """
    host: str = "localhost"
    port: int = 5432
    db: str = "openvista"
    user: str = "postgres"
    password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Computed property: SQLAlchemy async connection string"""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @field_validator("password")
    @classmethod
    def validate_password_required(cls, v: str) -> str:
        """Validator: Ensure password is provided"""
        if not v:
            raise ValueError("POSTGRES_PASSWORD must be set in .env file")
        return v


# Main Settings Container
class Settings(BaseSettings):
    """
    Main settings container that groups all configuration classes.
    Import this single object in application code.
    """
    app: AppSettings = AppSettings()
    postgres: PostgresSettings = PostgresSettings()


# Instantiate the settings once to be imported elsewhere
settings = Settings()
