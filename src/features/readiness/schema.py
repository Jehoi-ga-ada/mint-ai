from pydantic import BaseModel


class Ready(BaseModel):
    postgres: str = "not ready"
