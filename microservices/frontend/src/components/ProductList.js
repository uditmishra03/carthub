import React, { useState } from 'react';
import { useCart } from './CartContext';

// Mock product data - in real app this would come from an API
const mockProducts = [
  {
    product_id: 'prod-001',
    product_name: 'Gaming Laptop',
    price: 1299.99,
    description: 'High-performance gaming laptop with RTX 4060',
    image: '💻'
  },
  {
    product_id: 'prod-002',
    product_name: 'Wireless Mouse',
    price: 79.99,
    description: 'Ergonomic wireless gaming mouse',
    image: '🖱️'
  },
  {
    product_id: 'prod-003',
    product_name: 'Mechanical Keyboard',
    price: 149.99,
    description: 'RGB mechanical keyboard with blue switches',
    image: '⌨️'
  },
  {
    product_id: 'prod-004',
    product_name: 'Gaming Headset',
    price: 199.99,
    description: 'Surround sound gaming headset with microphone',
    image: '🎧'
  },
  {
    product_id: 'prod-005',
    product_name: 'Monitor',
    price: 399.99,
    description: '27" 4K gaming monitor with 144Hz refresh rate',
    image: '🖥️'
  },
  {
    product_id: 'prod-006',
    product_name: 'Gaming Chair',
    price: 299.99,
    description: 'Ergonomic gaming chair with lumbar support',
    image: '🪑'
  }
];

const ProductList = () => {
  const { addItemToCart, loading, error, clearError } = useCart();
  const [addingItems, setAddingItems] = useState(new Set());

  const handleAddToCart = async (product) => {
    try {
      clearError();
      setAddingItems(prev => new Set(prev).add(product.product_id));
      
      await addItemToCart({
        product_id: product.product_id,
        product_name: product.product_name,
        price: product.price,
        quantity: 1
      });
      
      // Show success feedback
      setTimeout(() => {
        setAddingItems(prev => {
          const newSet = new Set(prev);
          newSet.delete(product.product_id);
          return newSet;
        });
      }, 1000);
      
    } catch (error) {
      console.error('Failed to add item to cart:', error);
      setAddingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(product.product_id);
        return newSet;
      });
    }
  };

  return (
    <div className="product-list">
      <h2>Products</h2>
      
      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}
      
      <div className="products-grid">
        {mockProducts.map((product) => (
          <div key={product.product_id} className="product-card">
            <div className="product-image">{product.image}</div>
            <div className="product-info">
              <h3 className="product-name">{product.product_name}</h3>
              <p className="product-description">{product.description}</p>
              <div className="product-footer">
                <span className="product-price">${product.price}</span>
                <button
                  className="add-to-cart-button"
                  onClick={() => handleAddToCart(product)}
                  disabled={loading || addingItems.has(product.product_id)}
                >
                  {addingItems.has(product.product_id) ? 'Adding...' : 'Add to Cart'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductList;
