from sqlalchemy.orm import Session
from app.models.cart_models import Cart, CartItem
from app.models.schemas import CartItemRequest, CartResponse, CartItemResponse
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CartService:
    """Service class for cart operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_item_to_cart(self, request: CartItemRequest) -> CartResponse:
        """Add item to cart or update quantity if item exists."""
        try:
            # Get or create cart
            cart = self.db.query(Cart).filter(Cart.customer_id == request.customer_id).first()
            if not cart:
                cart = Cart(customer_id=request.customer_id)
                self.db.add(cart)
                self.db.flush()  # Flush to get the cart in the session
            
            # Check if item already exists in cart
            existing_item = self.db.query(CartItem).filter(
                CartItem.customer_id == request.customer_id,
                CartItem.product_id == request.product_id
            ).first()
            
            if existing_item:
                # Update existing item quantity
                existing_item.quantity += request.quantity
                existing_item.price = request.price  # Update price in case it changed
                existing_item.product_name = request.product_name  # Update name in case it changed
                logger.info(f"Updated item {request.product_id} quantity to {existing_item.quantity}")
            else:
                # Add new item to cart
                new_item = CartItem(
                    customer_id=request.customer_id,
                    product_id=request.product_id,
                    product_name=request.product_name,
                    price=request.price,
                    quantity=request.quantity
                )
                self.db.add(new_item)
                logger.info(f"Added new item {request.product_id} to cart")
            
            self.db.commit()
            
            # Refresh cart to get updated items
            self.db.refresh(cart)
            
            return self._cart_to_response(cart)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding item to cart: {e}")
            raise
    
    def get_cart(self, customer_id: str) -> CartResponse:
        """Get cart for customer."""
        try:
            cart = self.db.query(Cart).filter(Cart.customer_id == customer_id).first()
            if not cart:
                # Return empty cart
                return CartResponse(
                    customer_id=customer_id,
                    total_items=0,
                    subtotal=Decimal('0.00'),
                    items=[]
                )
            
            return self._cart_to_response(cart)
            
        except Exception as e:
            logger.error(f"Error getting cart: {e}")
            raise
    
    def update_item_quantity(self, customer_id: str, product_id: str, quantity: int) -> CartResponse:
        """Update item quantity in cart."""
        try:
            if quantity <= 0:
                return self.remove_item_from_cart(customer_id, product_id)
            
            item = self.db.query(CartItem).filter(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            ).first()
            
            if not item:
                raise ValueError(f"Item {product_id} not found in cart")
            
            item.quantity = quantity
            self.db.commit()
            
            # Get updated cart
            cart = self.db.query(Cart).filter(Cart.customer_id == customer_id).first()
            return self._cart_to_response(cart)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating item quantity: {e}")
            raise
    
    def remove_item_from_cart(self, customer_id: str, product_id: str) -> CartResponse:
        """Remove item from cart."""
        try:
            item = self.db.query(CartItem).filter(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            ).first()
            
            if item:
                self.db.delete(item)
                self.db.commit()
                logger.info(f"Removed item {product_id} from cart")
            
            # Get updated cart
            cart = self.db.query(Cart).filter(Cart.customer_id == customer_id).first()
            if cart:
                return self._cart_to_response(cart)
            else:
                return CartResponse(
                    customer_id=customer_id,
                    total_items=0,
                    subtotal=Decimal('0.00'),
                    items=[]
                )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing item from cart: {e}")
            raise
    
    def clear_cart(self, customer_id: str) -> bool:
        """Clear all items from cart."""
        try:
            # Delete all cart items
            self.db.query(CartItem).filter(CartItem.customer_id == customer_id).delete()
            
            # Delete cart
            self.db.query(Cart).filter(Cart.customer_id == customer_id).delete()
            
            self.db.commit()
            logger.info(f"Cleared cart for customer {customer_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing cart: {e}")
            raise
    
    def _cart_to_response(self, cart: Cart) -> CartResponse:
        """Convert cart model to response."""
        items = []
        for item in cart.items:
            items.append(CartItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                subtotal=item.subtotal
            ))
        
        return CartResponse(
            customer_id=cart.customer_id,
            total_items=cart.total_items,
            subtotal=cart.subtotal,
            items=items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )
