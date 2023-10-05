import uuid

from datetime import date
from sqlalchemy.orm import Session

from ..db import models
from ..entities import schemas
from ..helpers.exceptions import NotFound, InsufficientCapacity, InsufficientQuantity


def create_pallet(db: Session, pallet: schemas.ReceivedPalletSchema) -> models.Pallet:
    today = date.today().isoformat()
    db_pallet = models.Pallet(
        pallet_id=pallet.pallet_id, pallet_type=pallet.pallet_type, arrival_date=today
    )
    db.add(db_pallet)
    db.commit()
    db.refresh(db_pallet)

    # Increment pallet_count in buffer area
    buffer_storage_place = db.query(models.StoragePlace).filter_by(storage_place_id="BUFFER_AREA").first()
    if not buffer_storage_place:
        raise NotFound(message="Buffer storage place not found")

    buffer_storage_place.pallet_count += 1

    # Assign buffer area to pallet
    db_pallet.storage_place = buffer_storage_place

    # Create pallet items and associate them with pallet
    for item in pallet.pallet_items:
        product = db.query(models.Product).filter_by(sku=item.sku).first()
        if not product:
            raise NotFound(message=f"Product with SKU {item.sku} not found")

        pallet_item = models.PalletItem(
            pallet_item_id=str(uuid.uuid4()),
            pallet_id=db_pallet.pallet_id,
            product_sku=product.sku,
            quantity=item.quantity,
        )
        db.add(pallet_item)

    db.commit()
    db.refresh(db_pallet)

    # Calculate and set pallet item count
    db_pallet.pallet_item_count = len(db_pallet.pallet_items)

    return db_pallet



def move_pallet(db: Session, request: schemas.MoveRequest) -> models.Pallet:
    # Get pallet from the database
    pallet = db.query(models.Pallet).filter_by(pallet_id=request.pallet_id).first()

    if not pallet:
        raise NotFound(message="Pallet not found")

    # Get source storage place (buffer area)
    source_storage_place = db.query(models.StoragePlace).filter_by(storage_place_id=pallet.storage_place_id).first()

    if not source_storage_place:
        raise NotFound(message="Source storage place not found")

    # Decrement pallet_count in the source storage area (buffer area)
    source_storage_place.pallet_count -= 1

    # Get destination storage place
    destination_storage_place = db.query(models.StoragePlace).filter_by(storage_place_id=request.storage_place_id).first()

    if not destination_storage_place:
        raise NotFound(message="Destination storage place not found")

    # Increment pallet_count in destination storage area
    if destination_storage_place.pallet_count is None:
        destination_storage_place.pallet_count = 1
    else:
        destination_storage_place.pallet_count += 1

    # Update pallet's storage_place to new destination
    pallet.storage_place = destination_storage_place

    db.commit()
    return pallet


def move_products_to_picking_area(db: Session, request: schemas.MoveRequest):
    pallet = db.query(models.Pallet).filter_by(pallet_id=request.pallet_id).first()
    if not pallet:
        raise NotFound(message="Pallet not found")

    source_storage_place = db.query(models.StoragePlace).filter_by(storage_place_id=pallet.storage_place_id).first()
    if not source_storage_place:
        raise NotFound(message="Source storage place not found")

    destination_picking_area = db.query(models.PickingArea).filter_by(picking_area_id=request.picking_area_id).first()
    if not destination_picking_area:
        raise NotFound(message="Destination picking area not found")

    product = db.query(models.Product).filter_by(sku=request.product_sku).first()
    if not product:
        raise NotFound(message=f"Product with SKU {request.product_sku} not found")

    if source_storage_place.pallet_count > 0:
        # Decrement pallet_count in the source storage area
        source_storage_place.pallet_count -= 1

    pallet_item = db.query(models.PalletItem).filter_by(pallet_id=request.pallet_id, product_sku=request.product_sku).first()
    if not pallet_item:
        raise NotFound(message=f"Pallet item with SKU {request.product_sku} not found in the pallet")

    if pallet_item.quantity < request.quantity:
        raise InsufficientQuantity(message="Insufficient quantity in the pallet item")

    # Create new picking item
    picking_item = models.PickingItem(
        picking_item_id=str(uuid.uuid4()),
        picking_area_id=destination_picking_area.picking_area_id,
        product_sku=request.product_sku,
        quantity=request.quantity,
    )
    db.add(picking_item)

    # Update pallet item's quantity
    pallet_item.quantity -= request.quantity
    if pallet_item.quantity == 0:
        # If pallet item becomes empty, delete it
        db.delete(pallet_item)

        # Check if all pallet items are moved and the pallet is empty
        if len(pallet.pallet_items) == 0:
            # Decrement pallet count in the buffer area since the pallet is empty
            source_storage_place.pallet_count -= 1

            # Update pallet's storage place to new destination
            pallet.storage_place = destination_picking_area

    db.commit()
    return picking_item
