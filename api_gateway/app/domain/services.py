from app.domain.models import Item, ItemDraft
from app.domain.ports import ItemStoragePort


class CatalogService:
    def __init__(self, storage: ItemStoragePort) -> None:
        self._storage = storage

    def create_item(self, draft: ItemDraft) -> Item:
        name = draft.name.strip()
        if not name:
            raise ValueError("name must not be empty")
        if draft.price <= 0:
            raise ValueError("price must be positive")
        if draft.quantity < 0:
            raise ValueError("quantity must be non-negative")

        normalized = ItemDraft(
            name=name,
            price=draft.price,
            quantity=draft.quantity,
        )
        return self._storage.create_item(normalized)

    def get_item(self, item_id: int) -> Item:
        if item_id <= 0:
            raise ValueError("item_id must be positive")
        return self._storage.get_item(item_id)

    def health(self) -> bool:
        return self._storage.health()

    def close(self) -> None:
        self._storage.close()
