import logging
import time
from datetime import UTC, datetime
from typing import Any

import psycopg

from app.domain.models import Item, ItemDraft

logger = logging.getLogger(__name__)


class PostgresItemRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._initialize_with_retry()

    def _connect(self) -> psycopg.Connection[Any]:
        return psycopg.connect(self._database_url)

    def _initialize_with_retry(self) -> None:
        attempts = 30

        for attempt in range(1, attempts + 1):
            try:
                self._initialize()
                logger.info("database connection ready")
                return
            except psycopg.OperationalError as exc:
                if attempt == attempts:
                    logger.error("database unavailable after %s attempts", attempts)
                    raise

                logger.warning(
                    "database not ready, retry %s/%s: %s",
                    attempt,
                    attempts,
                    exc,
                )
                time.sleep(1)

    def _initialize(self) -> None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS items (
                        id BIGSERIAL PRIMARY KEY,
                        name VARCHAR(64) NOT NULL,
                        price DOUBLE PRECISION NOT NULL CHECK (price > 0),
                        quantity INTEGER NOT NULL CHECK (quantity >= 0),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
            )

    @staticmethod
    def _created_at_to_text(value: object) -> str:
        if isinstance(value, datetime):
            normalized = value.astimezone(UTC).isoformat()
            return normalized.replace("+00:00", "Z")
        return str(value)

    @classmethod
    def _from_row(cls, row: tuple[Any, ...]) -> Item:
        return Item(
            id=int(row[0]),
            name=str(row[1]),
            price=float(row[2]),
            quantity=int(row[3]),
            created_at=cls._created_at_to_text(row[4]),
        )

    def create(self, draft: ItemDraft) -> Item:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO items (name, price, quantity)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, price, quantity, created_at
                    """,
                (draft.name, draft.price, draft.quantity),
            )
            row = cursor.fetchone()

        if row is None:
            raise RuntimeError("failed to create item")
        return self._from_row(row)

    def get(self, item_id: int) -> Item | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, name, price, quantity, created_at
                    FROM items
                    WHERE id = %s
                    """,
                (item_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None
        return self._from_row(row)

    def ping(self) -> bool:
        try:
            with self._connect() as connection, connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return cursor.fetchone() is not None
        except psycopg.Error:
            return False
