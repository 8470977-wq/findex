from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    index_path: Path = Path("index.bin")
    app_name: str = "findex Web Search"
    
    class Config:
        env_prefix = "FINDEX_"

settings = Settings()
