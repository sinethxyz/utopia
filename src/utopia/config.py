"""Historical Utopia runtime configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # PostgreSQL: async application driver + synchronous Alembic driver.
    database_url: str = "postgresql+asyncpg://utopia:utopia@localhost:5432/utopia"
    database_url_sync: str = "postgresql+psycopg://utopia:utopia@localhost:5432/utopia"

    # WHOOP integration
    whoop_client_id: str = ""
    whoop_client_secret: str = ""
    whoop_redirect_uri: str = "http://localhost:8000/integrations/whoop/callback"

    # AI providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Embeddings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536


settings = Settings()
