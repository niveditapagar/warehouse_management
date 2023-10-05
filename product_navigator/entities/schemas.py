from datetime import date
from enum import Enum
from pydantic import BaseModel
from typing import List, Dict


class PalletType(str, Enum):
    CLEAN = "clean"
    MIXED = "mixed"

class ProductType(str, Enum):
    ONYX = "onyx"
    CAIMANO = "caimano"
    BARESI = "baresi"


class ProductSchema(BaseModel):
    sku: str
    name: str
    description: str
    expiration_date: date
    supplier_id: str

class PalletSchema(BaseModel):
    pallet_id: str
    pallet_type: PalletType
    arrival_date: date
    pallet_item_count: int

    class Config:
        orm_mode = True

class PalletItem(BaseModel):
    sku: str = ""
    quantity: int = 0

class ReceivedPalletSchema(BaseModel):
    pallet_id: str
    pallet_type: str
    pallet_items: List[PalletItem] = [PalletItem(sku="", quantity=0)]

class MoveRequest(BaseModel):
    pallet_id: str
    storage_place_id: str

class MoveProductRequest(BaseModel):
    product_sku: str
    pallet_id: str
    picking_area_id: str
    quantity: int
