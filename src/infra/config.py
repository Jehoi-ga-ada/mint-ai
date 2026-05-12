from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str
    debug: bool

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


config = Config()
print(config.secret_key)
print(config.algorithm)
print(config.access_token_expire_minutes)
