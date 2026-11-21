from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ItemDraft:
    name: str
    price: float
    quantity: int


@dataclass(frozen=True, slots=True)
class Item:
    id: int
    name: str
    price: float
    quantity: int
    created_at: str
