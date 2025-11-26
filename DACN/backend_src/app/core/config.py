import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:UHRSmsuSvwIjYsBRKXfhcRqrnQdJowGs@ballast.proxy.rlwy.net:43052/railway"
    SECRET_KEY: str = "dangvanthai1704"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
