from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class CartItemRequest(BaseModel):
    """Request model for adding items to cart."""
    customer_id: str = Field(..., min_length=1, max_length=100)
    product_id: str = Field(..., min_length=1, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=200)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    quantity: int = Field(..., gt=0)
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class CartItemResponse(BaseModel):
    """Response model for cart items."""
    product_id: str
    product_name: str
    price: Decimal
    quantity: int
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Response model for cart."""
    customer_id: str
    total_items: int
    subtotal: Decimal
    items: List[CartItemResponse]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CartOperationResponse(BaseModel):
    """Response model for cart operations."""
    success: bool
    message: str
    cart: Optional[CartResponse] = None
    error: Optional[str] = None


class CheckoutRequest(BaseModel):
    """Request model for checkout."""
    customer_id: str = Field(..., min_length=1, max_length=100)
    payment_method: str = Field(..., min_length=1)
    shipping_address: dict = Field(...)


class CheckoutResponse(BaseModel):
    """Response model for checkout."""
    success: bool
    order_id: Optional[str] = None
    total_amount: Optional[Decimal] = None
    message: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime
    version: str
    database: str
