from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import delete as sa_delete
from sqlalchemy import func, insert, select
from sqlalchemy import update as sa_update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepo(Generic[T]):
    model: Type[T]

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        return entity

    def create_many(self, entities: Sequence[T]) -> Sequence[T]:
        self.session.add_all(entities)
        self.session.flush()
        return entities

    def bulk_insert(self, rows: Sequence[dict]) -> None:
        self.session.execute(insert(self.model), rows)

    def get(self, id: Any) -> T | None:
        return self.session.get(self.model, id)

    def get_by(self, **filters: Any) -> T | None:
        stmt = select(self.model).filter_by(**filters)
        return self.session.execute(stmt).scalar_one_or_none()

    def list(
        self,
        *,  # to force the function to use named arguments after the bare '*'
        limit: int | None = None,
        offset: int | None = None,
        order_by: Any | None = None,
        **filters: Any,
    ) -> Sequence[T]:
        stmt = select(self.model).filter_by(**filters)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return self.session.execute(stmt).scalars().all()

    def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model).filter_by(**filters)
        return self.session.execute(stmt).scalar_one()

    def exists(self, **filters: Any) -> bool:
        stmt = select(self.model).filter_by(**filters).limit(1)
        return self.session.execute(stmt).first() is not None

    def update(self, entity: T) -> T:
        # update the object directly, then call this function
        self.session.flush()
        return entity

    def update_by_id(self, id: Any, **values: Any) -> int:
        stmt = (
            sa_update(self.model)
            .where(self.model.id == id)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        return self.session.execute(stmt).rowcount

    def update_many(self, filters: dict, values: dict) -> int:
        stmt = (
            sa_update(self.model)
            .filter_by(**filters)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        return self.session.execute(stmt).rowcount

    def delete(self, entity: T) -> None:
        self.session.delete(T)
        self.session.flush()

    def delete_by_id(self, id: Any) -> int:
        stmt = (
            sa_delete(self.model)
            .where(self.model.id == id)
            .execution_options(synchronize_session="fetch")
        )
        return self.session.execute(stmt).rowcount

    def delete_many(self, id: Sequence[Any]) -> int:
        stmt = (
            sa_delete(self.model)
            .where(self.model.id.in_(ids))
            .execution_options(synchronize_session="fetch")
        )
        return self.session.execute(stmt).rowcount

    def upsert(
        self,
        rows: Sequence[dict],
        index_elements: Sequence[str],
        update_cols: Sequence[str],
    ) -> None:
        stmt = pg_insert(self.model).values(list(rows))
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_={c: stmt.excluded[c] for c in update_cols},
        )
        self.session.execute(stmt)
