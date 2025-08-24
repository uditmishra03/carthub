import React, { useState } from 'react';
import { useCart } from './CartContext';

const Cart = () => {
  const { 
    cart, 
    updateItemQuantity, 
    removeItemFromCart, 
    clearCart, 
    loading, 
    error, 
    clearError 
  } = useCart();
  
  const [updatingItems, setUpdatingItems] = useState(new Set());

  const handleQuantityChange = async (productId, newQuantity) => {
    if (newQuantity < 0) return;
    
    try {
      clearError();
      setUpdatingItems(prev => new Set(prev).add(productId));
      
      if (newQuantity === 0) {
        await removeItemFromCart(productId);
      } else {
        await updateItemQuantity(productId, newQuantity);
      }
      
    } catch (error) {
      console.error('Failed to update item:', error);
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  const handleRemoveItem = async (productId) => {
    try {
      clearError();
      setUpdatingItems(prev => new Set(prev).add(productId));
      await removeItemFromCart(productId);
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      try {
        clearError();
        await clearCart();
      } catch (error) {
        console.error('Failed to clear cart:', error);
      }
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="cart">
        <h2>Your Cart</h2>
        <div className="empty-cart">
          <p>Your cart is empty</p>
          <p>Add some products to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="cart">
      <div className="cart-header">
        <h2>Your Cart ({cart.total_items} items)</h2>
        <button 
          className="clear-cart-button"
          onClick={handleClearCart}
          disabled={loading}
        >
          Clear Cart
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      <div className="cart-items">
        {cart.items.map((item) => (
          <div key={item.product_id} className="cart-item">
            <div className="item-info">
              <h3 className="item-name">{item.product_name}</h3>
              <p className="item-price">${item.price} each</p>
            </div>
            
            <div className="item-controls">
              <div className="quantity-controls">
                <button
                  className="quantity-button"
                  onClick={() => handleQuantityChange(item.product_id, item.quantity - 1)}
                  disabled={loading || updatingItems.has(item.product_id)}
                >
                  -
                </button>
                <span className="quantity">{item.quantity}</span>
                <button
                  className="quantity-button"
                  onClick={() => handleQuantityChange(item.product_id, item.quantity + 1)}
                  disabled={loading || updatingItems.has(item.product_id)}
                >
                  +
                </button>
              </div>
              
              <div className="item-subtotal">
                ${item.subtotal}
              </div>
              
              <button
                className="remove-button"
                onClick={() => handleRemoveItem(item.product_id)}
                disabled={loading || updatingItems.has(item.product_id)}
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <div className="summary-row">
          <span>Total Items:</span>
          <span>{cart.total_items}</span>
        </div>
        <div className="summary-row total">
          <span>Subtotal:</span>
          <span>${cart.subtotal}</span>
        </div>
      </div>
    </div>
  );
};

export default Cart;
