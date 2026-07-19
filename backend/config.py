from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    NEO4J_URI: str
    NEO4J_PASSWORD: str
    NEO4J_USER: str = "b3a8d7d2"

    SUPABASE_URL: str
    SUPABASE_KEY: str

    GROQ_API_KEY: str

    GROQ_TEXT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_VISION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"


settings = Settings()
