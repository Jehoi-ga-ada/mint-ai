from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str
    debug: bool

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


config = Config()
