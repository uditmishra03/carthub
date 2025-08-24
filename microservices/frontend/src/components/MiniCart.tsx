import React, { useState } from 'react';
import { MiniCartProps } from '../types';
import { formatCurrency } from '../utils';
import LoadingSpinner from './LoadingSpinner';

const MiniCart: React.FC<MiniCartProps> = ({
  cart,
  isVisible,
  onClose,
  onViewCart,
  onUpdateQuantity,
  onRemoveItem,
  isLoading
}) => {
  const [updatingItems, setUpdatingItems] = useState<Set<string>>(new Set());

  if (!isVisible) return null;

  const handleQuantityChange = async (productId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    setUpdatingItems(prev => new Set(prev).add(productId));
    try {
      await onUpdateQuantity(productId, newQuantity);
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  const handleRemoveItem = async (productId: string) => {
    setUpdatingItems(prev => new Set(prev).add(productId));
    try {
      await onRemoveItem(productId);
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  const calculatePricing = () => {
    const subtotal = cart?.subtotal ? parseFloat(cart.subtotal) : 0;
    const taxes = subtotal * 0.08; // 8% tax
    const shipping = subtotal > 100 ? 0 : 9.99; // Free shipping over $100
    const total = subtotal + taxes + shipping;

    return { subtotal, taxes, shipping, total };
  };

  const pricing = calculatePricing();
  const isEmpty = !cart || cart.items.length === 0;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-xl w-96 max-h-96 overflow-hidden animate-fadeIn">
      {/* Header */}
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Shopping Cart</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-h-64 overflow-y-auto">
        {isEmpty ? (
          /* Empty State */
          <div className="p-8 text-center">
            <div className="text-6xl mb-4">🛒</div>
            <p className="text-gray-500 mb-2">Your cart is empty</p>
            <p className="text-sm text-gray-400">Add some products to get started</p>
          </div>
        ) : (
          /* Cart Items */
          <div className="p-4 space-y-3">
            {cart!.items.map((item) => {
              const isUpdating = updatingItems.has(item.product_id);
              
              return (
                <div 
                  key={item.product_id} 
                  className={`flex items-center gap-3 p-3 bg-gray-50 rounded-lg transition-opacity ${
                    isUpdating ? 'opacity-50' : ''
                  }`}
                >
                  {/* Product Image Placeholder */}
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-lg">📦</span>
                  </div>

                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm text-gray-900 truncate">
                      {item.product_name}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {formatCurrency(parseFloat(item.price))}
                    </p>
                  </div>

                  {/* Quantity Controls */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleQuantityChange(item.product_id, item.quantity - 1)}
                      disabled={isUpdating || item.quantity <= 1}
                      className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-sm font-medium transition-colors"
                    >
                      −
                    </button>
                    
                    <span className="w-8 text-center text-sm font-medium">
                      {isUpdating ? <LoadingSpinner size="sm" /> : item.quantity}
                    </span>
                    
                    <button
                      onClick={() => handleQuantityChange(item.product_id, item.quantity + 1)}
                      disabled={isUpdating}
                      className="w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-sm font-medium transition-colors"
                    >
                      +
                    </button>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => handleRemoveItem(item.product_id)}
                    disabled={isUpdating}
                    className="text-red-400 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Remove item"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      {!isEmpty && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          {/* Pricing Summary */}
          <div className="space-y-1 mb-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal:</span>
              <span className="font-medium">{formatCurrency(pricing.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Taxes:</span>
              <span className="font-medium">{formatCurrency(pricing.taxes)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Shipping:</span>
              <span className="font-medium">
                {pricing.shipping === 0 ? 'FREE' : formatCurrency(pricing.shipping)}
              </span>
            </div>
            <div className="flex justify-between pt-2 border-t border-gray-300 font-semibold">
              <span>Total:</span>
              <span className="text-blue-600">{formatCurrency(pricing.total)}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-2">
            <button
              onClick={onViewCart}
              className="w-full bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              View Cart
            </button>
            <button
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? <LoadingSpinner size="sm" /> : 'Checkout'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiniCart;
