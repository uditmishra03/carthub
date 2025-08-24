from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
from decimal import Decimal
from typing import List


class Cart(Base):
    """Cart model for database."""
    __tablename__ = "carts"
    
    customer_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to cart items
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    @property
    def total_items(self) -> int:
        """Calculate total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate cart subtotal."""
        return sum(item.subtotal for item in self.items)


class CartItem(Base):
    """Cart item model for database."""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("carts.customer_id"), nullable=False)
    product_id = Column(String, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to cart
    cart = relationship("Cart", back_populates="items")
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate item subtotal."""
        return Decimal(str(self.price)) * self.quantity
