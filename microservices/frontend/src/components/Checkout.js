import React, { useState } from 'react';
import { useCart } from './CartContext';

const Checkout = () => {
  const { cart, checkout, loading, error, clearError } = useCart();
  const [checkoutData, setCheckoutData] = useState({
    payment_method: 'credit_card',
    shipping_address: {
      street: '',
      city: '',
      state: '',
      zip: '',
      country: 'US'
    }
  });
  const [checkoutResult, setCheckoutResult] = useState(null);

  const handleInputChange = (field, value) => {
    if (field.startsWith('shipping_address.')) {
      const addressField = field.split('.')[1];
      setCheckoutData(prev => ({
        ...prev,
        shipping_address: {
          ...prev.shipping_address,
          [addressField]: value
        }
      }));
    } else {
      setCheckoutData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    const { shipping_address } = checkoutData;
    if (!shipping_address.street || !shipping_address.city || 
        !shipping_address.state || !shipping_address.zip) {
      alert('Please fill in all shipping address fields');
      return;
    }

    try {
      clearError();
      const result = await checkout(checkoutData);
      setCheckoutResult(result);
    } catch (error) {
      console.error('Checkout failed:', error);
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="checkout">
        <h2>Checkout</h2>
        <div className="empty-cart">
          <p>Your cart is empty</p>
          <p>Add some products before checking out!</p>
        </div>
      </div>
    );
  }

  if (checkoutResult && checkoutResult.success) {
    return (
      <div className="checkout">
        <div className="checkout-success">
          <h2>✅ Order Successful!</h2>
          <div className="success-details">
            <p><strong>Order ID:</strong> {checkoutResult.order_id}</p>
            <p><strong>Total Amount:</strong> ${checkoutResult.total_amount}</p>
            <p><strong>Message:</strong> {checkoutResult.message}</p>
          </div>
          <button 
            className="continue-shopping-button"
            onClick={() => {
              setCheckoutResult(null);
              window.location.reload(); // Simple way to reset the app
            }}
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="checkout">
      <h2>Checkout</h2>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      <div className="checkout-content">
        <div className="order-summary">
          <h3>Order Summary</h3>
          <div className="summary-items">
            {cart.items.map((item) => (
              <div key={item.product_id} className="summary-item">
                <span className="item-name">{item.product_name}</span>
                <span className="item-quantity">x{item.quantity}</span>
                <span className="item-total">${item.subtotal}</span>
              </div>
            ))}
          </div>
          <div className="summary-total">
            <strong>Total: ${cart.subtotal}</strong>
          </div>
        </div>

        <form className="checkout-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <h3>Payment Method</h3>
            <div className="form-group">
              <label>
                <input
                  type="radio"
                  name="payment_method"
                  value="credit_card"
                  checked={checkoutData.payment_method === 'credit_card'}
                  onChange={(e) => handleInputChange('payment_method', e.target.value)}
                />
                Credit Card
              </label>
              <label>
                <input
                  type="radio"
                  name="payment_method"
                  value="paypal"
                  checked={checkoutData.payment_method === 'paypal'}
                  onChange={(e) => handleInputChange('payment_method', e.target.value)}
                />
                PayPal
              </label>
            </div>
          </div>

          <div className="form-section">
            <h3>Shipping Address</h3>
            <div className="form-group">
              <label>Street Address</label>
              <input
                type="text"
                value={checkoutData.shipping_address.street}
                onChange={(e) => handleInputChange('shipping_address.street', e.target.value)}
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>City</label>
                <input
                  type="text"
                  value={checkoutData.shipping_address.city}
                  onChange={(e) => handleInputChange('shipping_address.city', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>State</label>
                <input
                  type="text"
                  value={checkoutData.shipping_address.state}
                  onChange={(e) => handleInputChange('shipping_address.state', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>ZIP Code</label>
                <input
                  type="text"
                  value={checkoutData.shipping_address.zip}
                  onChange={(e) => handleInputChange('shipping_address.zip', e.target.value)}
                  required
                />
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            className="checkout-button"
            disabled={loading}
          >
            {loading ? 'Processing...' : `Place Order - $${cart.subtotal}`}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Checkout;
