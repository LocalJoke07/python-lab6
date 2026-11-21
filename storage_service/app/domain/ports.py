from typing import Protocol

from app.domain.models import Item, ItemDraft


class ItemRepository(Protocol):
    def create(self, draft: ItemDraft) -> Item: ...

    def get(self, item_id: int) -> Item | None: ...

    def ping(self) -> bool: ...
