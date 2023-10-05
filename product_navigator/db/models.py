from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from .database import Base
from ..entities.schemas import ProductType, PalletType


class Product(Base):
    __tablename__ = "products"

    sku = Column(String(50), primary_key=True)
    name = Column(String(50))
    description = Column(String(250))
    expiration_date = Column(Date)
    supplier_id = Column(String(50))

    pallet_items = relationship("PalletItem", back_populates="product")


class Pallet(Base):
    __tablename__ = "pallets"

    pallet_id = Column(String(50), primary_key=True)
    pallet_type = Column(ChoiceType(PalletType, impl=Integer()))
    arrival_date = Column(Date)

    pallet_items = relationship("PalletItem", back_populates="pallet")
    storage_place_id = Column(String(50), ForeignKey("storage_places.storage_place_id"))
    storage_place = relationship("StoragePlace", back_populates="pallets")



class PalletItem(Base):
    __tablename__ = "pallet_items"

    pallet_item_id = Column(String(50), primary_key=True)
    pallet_id = Column(String(50), ForeignKey("pallets.pallet_id"))
    product_sku = Column(String(50), ForeignKey("products.sku"))
    quantity = Column(Integer)

    product = relationship("Product", back_populates="pallet_items")
    pallet = relationship("Pallet", back_populates="pallet_items")


class StoragePlace(Base):
    __tablename__ = "storage_places"

    storage_place_id = Column(String(50), primary_key=True)
    temperature_range = Column(String(50))
    available = Column(Boolean)
    pallet_count = Column(Integer)  # New field to store the number of pallets

    pallets = relationship("Pallet", back_populates="storage_place")
    picking_areas = relationship("PickingArea", back_populates="storage_place")


class PickingArea(Base):
    __tablename__ = "picking_areas"

    picking_area_id = Column(String(50), primary_key=True)
    product_type = Column(ChoiceType(ProductType, impl=String(50)))

    storage_place_id = Column(Integer, ForeignKey("storage_places.storage_place_id"))
    storage_place = relationship("StoragePlace", back_populates="picking_areas")
