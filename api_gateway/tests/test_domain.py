import pytest

from app.domain.errors import ItemNotFoundError
from app.domain.models import Item, ItemDraft
from app.domain.services import CatalogService


class FakeStorage:
    def __init__(self) -> None:
        self.items: dict[int, Item] = {}
        self.next_id = 1

    def create_item(self, draft: ItemDraft) -> Item:
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

    def get_item(self, item_id: int) -> Item:
        try:
            return self.items[item_id]
        except KeyError as exc:
            raise ItemNotFoundError("item not found") from exc

    def health(self) -> bool:
        return True

    def close(self) -> None:
        pass


def test_create_item_normalizes_name_and_uses_port() -> None:
    fake = FakeStorage()
    service = CatalogService(fake)

    item = service.create_item(ItemDraft("  CPU  ", 199.0, 3))

    assert item.id == 1
    assert item.name == "CPU"
    assert fake.items[1] == item


def test_create_item_rejects_non_positive_price() -> None:
    service = CatalogService(FakeStorage())

    with pytest.raises(ValueError, match="price must be positive"):
        service.create_item(ItemDraft("CPU", 0.0, 1))


def test_get_item_uses_storage_port() -> None:
    fake = FakeStorage()
    service = CatalogService(fake)
    created = service.create_item(ItemDraft("SSD", 100.0, 2))

    loaded = service.get_item(created.id)

    assert loaded == created


def test_get_item_rejects_non_positive_id() -> None:
    service = CatalogService(FakeStorage())

    with pytest.raises(ValueError, match="item_id must be positive"):
        service.get_item(0)


def test_health_uses_storage_port() -> None:
    service = CatalogService(FakeStorage())

    assert service.health() is True
