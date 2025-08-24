import React from 'react';
import { useCart } from './CartContext';

const Header = ({ currentView, setCurrentView }) => {
  const { cart } = useCart();

  return (
    <header className="header">
      <div className="header-content">
        <h1 className="logo">🛒 Shopping Cart</h1>
        <nav className="nav">
          <button
            className={`nav-button ${currentView === 'products' ? 'active' : ''}`}
            onClick={() => setCurrentView('products')}
          >
            Products
          </button>
          <button
            className={`nav-button ${currentView === 'cart' ? 'active' : ''}`}
            onClick={() => setCurrentView('cart')}
          >
            Cart ({cart.total_items})
          </button>
          {cart.total_items > 0 && (
            <button
              className={`nav-button checkout-button ${currentView === 'checkout' ? 'active' : ''}`}
              onClick={() => setCurrentView('checkout')}
            >
              Checkout
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
