import pytest

from app.domain.errors import ItemNotFoundError
from app.domain.models import Item, ItemDraft
from app.domain.services import ItemService


class FakeRepository:
    def __init__(self) -> None:
        self.items: dict[int, Item] = {}
        self.next_id = 1

    def create(self, draft: ItemDraft) -> Item:
        item = Item(
            id=self.next_id,
            name=draft.name,
            price=draft.price,
            quantity=draft.quantity,
            created_at="2026-01-01T00:00:00Z",
        )
        self.items[item.id] = item
        self.next_id += 1
        return item

    def get(self, item_id: int) -> Item | None:
        return self.items.get(item_id)

    def ping(self) -> bool:
        return True


def test_create_item_saves_normalized_item() -> None:
    repo = FakeRepository()
    service = ItemService(repo)

    item = service.create_item(ItemDraft("  SSD  ", 100.0, 2))

    assert item.name == "SSD"
    assert repo.items[item.id] == item


def test_create_item_rejects_negative_quantity() -> None:
    service = ItemService(FakeRepository())

    with pytest.raises(ValueError, match="quantity must be non-negative"):
        service.create_item(ItemDraft("SSD", 100.0, -1))


def test_get_item_returns_existing_item() -> None:
    service = ItemService(FakeRepository())
    created = service.create_item(ItemDraft("RAM", 80.0, 4))

    assert service.get_item(created.id) == created


def test_get_item_raises_for_missing_item() -> None:
    service = ItemService(FakeRepository())

    with pytest.raises(ItemNotFoundError, match="item not found"):
        service.get_item(999)


def test_health_uses_repository_ping() -> None:
    service = ItemService(FakeRepository())

    assert service.health() is True
