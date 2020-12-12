from pydantic import BaseSettings


class Settings(BaseSettings):
    gmap_key: str

settings = Settings()