from app.domain.errors import ItemNotFoundError
from app.domain.models import Item, ItemDraft
from app.domain.ports import ItemRepository


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

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
        return self._repository.create(normalized)

    def get_item(self, item_id: int) -> Item:
        if item_id <= 0:
            raise ValueError("item_id must be positive")
        item = self._repository.get(item_id)
        if item is None:
            raise ItemNotFoundError("item not found")
        return item

    def health(self) -> bool:
        return self._repository.ping()
