from fastapi import APIRouter, HTTPException, Request, status

from app.api.schemas import ErrorResponse, ItemCreate, ItemRead
from app.domain.errors import ItemNotFoundError, NeighborUnavailableError
from app.domain.models import ItemDraft
from app.domain.services import CatalogService


router = APIRouter()


def _service(request: Request) -> CatalogService:
    return request.app.state.catalog_service


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    if not _service(request).health():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="storage service unavailable",
        )
    return {"status": "ok"}


@router.post(
    "/items",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    responses={503: {"model": ErrorResponse}},
)
def create_item(payload: ItemCreate, request: Request) -> ItemRead:
    try:
        item = _service(request).create_item(
            ItemDraft(
                name=payload.name,
                price=payload.price,
                quantity=payload.quantity,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except NeighborUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="storage service unavailable",
        ) from exc

    return ItemRead(
        id=item.id,
        name=item.name,
        price=item.price,
        quantity=item.quantity,
        created_at=item.created_at,
    )


@router.get(
    "/items/{item_id}",
    response_model=ItemRead,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def get_item(item_id: int, request: Request) -> ItemRead:
    try:
        item = _service(request).get_item(item_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=404, detail="item not found") from exc
    except NeighborUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="storage service unavailable",
        ) from exc

    return ItemRead(
        id=item.id,
        name=item.name,
        price=item.price,
        quantity=item.quantity,
        created_at=item.created_at,
    )
