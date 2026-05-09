from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class PostgreDatabase:
    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(
            url=db_url,
            pool_size=20,
        )

        self._session_factory = sessionmaker(bind=self.engine)
