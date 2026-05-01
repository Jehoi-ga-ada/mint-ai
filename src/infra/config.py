from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str
    debug: bool


config = Config()
