from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, allow_inf_nan=False)

    name: str = Field(min_length=1, max_length=64, pattern=r"^[\x20-\x7E]+$")
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class ItemRead(ItemCreate):
    id: int = Field(gt=0)
    created_at: str = Field(min_length=1)


class ErrorResponse(BaseModel):
    detail: str
