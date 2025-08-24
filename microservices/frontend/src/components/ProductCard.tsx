import React, { useState } from 'react';
import { ProductCardProps } from '../types';
import { formatCurrency } from '../utils';
import LoadingSpinner from './LoadingSpinner';

const ProductCard: React.FC<ProductCardProps> = ({ 
  product, 
  onAddToCart, 
  isLoading 
}) => {
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);

  const handleAddToCart = async () => {
    if (isAdding || !product.inStock) return;
    
    setIsAdding(true);
    try {
      await onAddToCart(product, quantity);
      // Reset quantity after successful add
      setQuantity(1);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    } finally {
      setIsAdding(false);
    }
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setQuantity(parseInt(e.target.value));
  };

  return (
    <div className="card p-6 animate-fade-in">
      {/* Product Image */}
      <div className="mb-4 bg-gray-100 rounded-lg aspect-square flex items-center justify-center">
        {product.image ? (
          <img 
            src={product.image} 
            alt={product.name}
            className="w-full h-full object-cover rounded-lg"
          />
        ) : (
          <div className="text-gray-400 text-4xl">
            📦
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {product.name}
        </h3>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {product.description}
        </p>
        
        <div className="flex items-center justify-between mb-3">
          <span className="text-2xl font-bold text-primary-600">
            {formatCurrency(product.price)}
          </span>
          
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            product.inStock 
              ? 'bg-green-100 text-green-600' 
              : 'bg-red-100 text-red-600'
          }`}>
            {product.inStock ? 'In Stock' : 'Out of Stock'}
          </span>
        </div>

        <div className="text-xs text-gray-500 mb-4">
          Category: {product.category}
        </div>
      </div>

      {/* Add to Cart Section */}
      <div className="space-y-3">
        {/* Quantity Selector */}
        <div className="flex items-center gap-2">
          <label htmlFor={`quantity-${product.id}`} className="text-sm font-medium text-gray-700">
            Qty:
          </label>
          <select
            id={`quantity-${product.id}`}
            value={quantity}
            onChange={handleQuantityChange}
            disabled={!product.inStock || isAdding}
            className="input w-20 text-center"
          >
            {[...Array(10)].map((_, i) => (
              <option key={i + 1} value={i + 1}>
                {i + 1}
              </option>
            ))}
          </select>
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={handleAddToCart}
          disabled={!product.inStock || isAdding || isLoading}
          className={`btn w-full ${
            product.inStock 
              ? 'btn-primary' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isAdding ? (
            <div className="flex items-center gap-2">
              <LoadingSpinner size="sm" />
              <span>Adding...</span>
            </div>
          ) : (
            <>
              🛒 Add to Cart
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
