from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.cart_service import CartService
from app.models.schemas import (
    CartItemRequest, 
    CartOperationResponse, 
    CheckoutRequest, 
    CheckoutResponse
)
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/items", response_model=CartOperationResponse)
async def add_item_to_cart(
    request: CartItemRequest,
    db: Session = Depends(get_db)
):
    """Add item to shopping cart."""
    try:
        cart_service = CartService(db)
        cart = cart_service.add_item_to_cart(request)
        
        return CartOperationResponse(
            success=True,
            message="Item added to cart successfully",
            cart=cart
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding item to cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.get("/{customer_id}", response_model=CartOperationResponse)
async def get_cart(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get customer's cart."""
    try:
        cart_service = CartService(db)
        cart = cart_service.get_cart(customer_id)
        
        return CartOperationResponse(
            success=True,
            message="Cart retrieved successfully",
            cart=cart
        )
        
    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )


@router.put("/{customer_id}/items/{product_id}")
async def update_item_quantity(
    customer_id: str,
    product_id: str,
    quantity: int,
    db: Session = Depends(get_db)
):
    """Update item quantity in cart."""
    try:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        cart_service = CartService(db)
        cart = cart_service.update_item_quantity(customer_id, product_id, quantity)
        
        return CartOperationResponse(
            success=True,
            message="Item quantity updated successfully",
            cart=cart
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating item quantity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update item quantity"
        )


@router.delete("/{customer_id}/items/{product_id}")
async def remove_item_from_cart(
    customer_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    """Remove item from cart."""
    try:
        cart_service = CartService(db)
        cart = cart_service.remove_item_from_cart(customer_id, product_id)
        
        return CartOperationResponse(
            success=True,
            message="Item removed from cart successfully",
            cart=cart
        )
        
    except Exception as e:
        logger.error(f"Error removing item from cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart"
        )


@router.delete("/{customer_id}")
async def clear_cart(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Clear all items from cart."""
    try:
        cart_service = CartService(db)
        success = cart_service.clear_cart(customer_id)
        
        if success:
            return CartOperationResponse(
                success=True,
                message="Cart cleared successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear cart"
            )
        
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart"
        )


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Process cart checkout."""
    try:
        cart_service = CartService(db)
        cart = cart_service.get_cart(request.customer_id)
        
        if not cart.items:
            raise ValueError("Cannot checkout empty cart")
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # In a real implementation, you would:
        # 1. Process payment
        # 2. Create order record
        # 3. Update inventory
        # 4. Send confirmation email
        # 5. Clear cart
        
        # For now, just clear the cart
        cart_service.clear_cart(request.customer_id)
        
        return CheckoutResponse(
            success=True,
            order_id=order_id,
            total_amount=cart.subtotal,
            message="Checkout completed successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Checkout validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Checkout failed"
        )
