import React from 'react';
import { CartSummaryProps } from '../types';
import { formatCurrency, calculateCartStats } from '../utils';
import LoadingSpinner from './LoadingSpinner';

const CartSummary: React.FC<CartSummaryProps> = ({ cart, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card p-6">
        <LoadingSpinner size="md" message="Loading cart..." />
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="card p-6 text-center">
        <div className="text-gray-400 text-4xl mb-4">🛒</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Your cart is empty
        </h3>
        <p className="text-gray-600">
          Add some products to get started!
        </p>
      </div>
    );
  }

  const stats = calculateCartStats(cart.items);

  return (
    <div className="space-y-6">
      {/* Cart Header */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            🛒 Shopping Cart
          </h2>
          <span className="bg-primary-100 text-primary-600 px-3 py-1 rounded-full text-sm font-medium">
            {cart.total_items} {cart.total_items === 1 ? 'item' : 'items'}
          </span>
        </div>

        {/* Cart Statistics */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Unique Products</div>
            <div className="text-lg font-semibold text-gray-900">
              {stats.uniqueProducts}
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Total Items</div>
            <div className="text-lg font-semibold text-gray-900">
              {stats.totalItems}
            </div>
          </div>
        </div>

        {/* Total */}
        <div className="border-t pt-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold text-gray-900">
              Total:
            </span>
            <span className="text-2xl font-bold text-primary-600">
              {formatCurrency(cart.subtotal)}
            </span>
          </div>
        </div>
      </div>

      {/* Cart Items */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Cart Items
        </h3>
        
        <div className="space-y-4">
          {cart.items.map((item, index) => (
            <div 
              key={`${item.product_id}-${index}`}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg animate-fade-in"
            >
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-1">
                  {item.product_name}
                </h4>
                <div className="text-sm text-gray-600">
                  {formatCurrency(item.price)} × {item.quantity}
                </div>
              </div>
              
              <div className="text-right">
                <div className="font-semibold text-gray-900">
                  {formatCurrency(item.subtotal)}
                </div>
                <div className="text-xs text-gray-500">
                  Qty: {item.quantity}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Checkout Button */}
        <div className="mt-6 pt-4 border-t">
          <button className="btn btn-primary w-full btn-lg">
            🚀 Proceed to Checkout
          </button>
          <p className="text-xs text-gray-500 text-center mt-2">
            * Checkout functionality coming soon
          </p>
        </div>
      </div>

      {/* Customer Info */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Customer Information
        </h3>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Customer ID:</span>
            <span className="font-mono text-xs text-gray-900">
              {cart.customer_id}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Average Item Price:</span>
            <span className="text-gray-900">
              {formatCurrency(stats.averageItemPrice)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartSummary;
