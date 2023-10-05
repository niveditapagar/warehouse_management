
from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session
from typing import Dict

from ..helpers.exceptions import NotEnoughInfo, CreationError
from ..entities import schemas
from ..db.database import SessionLocal
from ..helpers import crud


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"root": "Welcome to the Product Navigator API"}


@app.post("/pallets", response_model=schemas.PalletSchema, status_code=status.HTTP_201_CREATED)
def create_pallet(pallet: schemas.ReceivedPalletSchema, db: Session = Depends(get_db)):
    if not pallet.pallet_id or not pallet.pallet_type or len(pallet.pallet_items) == 0:
        raise NotEnoughInfo(message="Please enter values for all fields")
    db_pallet = crud.create_pallet(db=db, pallet=pallet)
    print("pallet item count: ", db_pallet.pallet_item_count)
    return schemas.PalletSchema(
        pallet_id=db_pallet.pallet_id,
        pallet_type=db_pallet.pallet_type,
        arrival_date=db_pallet.arrival_date,
        pallet_item_count=db_pallet.pallet_item_count, 
    )


@app.post("/api/storage/move")
def move_pallets(request: schemas.MoveRequest, db: Session = Depends(get_db)):
    if not request.pallet_id or not request.storage_place_id:
        raise NotEnoughInfo(message="Please enter values for all fields")
    moved_pallet = crud.move_pallet(db=db, request=request)
    
    if not moved_pallet:
        raise CreationError(message="Something went wrong while moving the pallet from buffer area to storage area!")
    
    return {"message": "Pallet moved successfully"}


@app.post("/api/picking/move", status_code=status.HTTP_200_OK)
def move_products_to_picking(request: schemas.MoveProductRequest, db: Session = Depends(get_db)):
    if not request.product_sku or not request.pallet_id or not request.picking_area_id or not request.quantity:
        raise NotEnoughInfo(message="Please provide all the required information")

    moved_products = crud.move_products_to_picking_area(db=db, request=request)
    if not moved_products:
        raise CreationError("Something went wrong while moving the products from storage area to picking area")
    
    return {"message": "Products moved to picking area successfully"}
