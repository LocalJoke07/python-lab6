import logging

import httpx

from app.domain.errors import ItemNotFoundError, NeighborUnavailableError
from app.domain.models import Item, ItemDraft


logger = logging.getLogger(__name__)


class StorageHttpClient:
    def __init__(self, base_url: str, timeout_s: float) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout_s,
        )

    def close(self) -> None:
        self._client.close()

    def _request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise ItemNotFoundError("item not found") from exc
            logger.error(
                "storage_http_error status=%s",
                exc.response.status_code,
            )
            raise NeighborUnavailableError("storage service error") from exc
        except httpx.RequestError as exc:
            logger.error("storage_request_error type=%s", exc.__class__.__name__)
            raise NeighborUnavailableError("storage service unavailable") from exc

    @staticmethod
    def _parse_item(data: dict[str, object]) -> Item:
        return Item(
            id=int(data["id"]),
            name=str(data["name"]),
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            created_at=str(data["created_at"]),
        )

    def create_item(self, draft: ItemDraft) -> Item:
        response = self._request(
            "POST",
            "/items",
            json={
                "name": draft.name,
                "price": draft.price,
                "quantity": draft.quantity,
            },
        )
        return self._parse_item(response.json())

    def get_item(self, item_id: int) -> Item:
        response = self._request("GET", f"/items/{item_id}")
        return self._parse_item(response.json())

    def health(self) -> bool:
        try:
            self._request("GET", "/health")
            return True
        except NeighborUnavailableError:
            return False
