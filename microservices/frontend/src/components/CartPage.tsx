import React, { useState } from 'react';
import { CartPageProps } from '../types';
import { formatCurrency } from '../utils';
import LoadingSpinner from './LoadingSpinner';

const CartPage: React.FC<CartPageProps> = ({
  cart,
  onUpdateQuantity,
  onRemoveItem,
  onBackToShopping,
  isLoading
}) => {
  const [updatingItems, setUpdatingItems] = useState<Set<string>>(new Set());

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
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Shopping Cart</h1>
            <p className="text-gray-600">
              {isEmpty ? 'Your cart is empty' : `${cart!.total_items} item${cart!.total_items !== 1 ? 's' : ''} in your cart`}
            </p>
          </div>
          
          <button
            onClick={onBackToShopping}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Continue Shopping
          </button>
        </div>

        {isEmpty ? (
          /* Empty State */
          <div className="text-center py-16">
            <div className="text-8xl mb-6">🛒</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-8">Looks like you haven't added any items to your cart yet.</p>
            <button
              onClick={onBackToShopping}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium"
            >
              Start Shopping
            </button>
          </div>
        ) : (
          /* Cart Content */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Cart Items</h2>
                </div>
                
                <div className="divide-y divide-gray-200">
                  {cart!.items.map((item) => {
                    const isUpdating = updatingItems.has(item.product_id);
                    
                    return (
                      <div 
                        key={item.product_id} 
                        className={`p-6 transition-opacity ${isUpdating ? 'opacity-50' : ''}`}
                      >
                        <div className="flex items-start gap-4">
                          {/* Product Image */}
                          <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <span className="text-2xl">📦</span>
                          </div>

                          {/* Product Details */}
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {item.product_name}
                            </h3>
                            <p className="text-gray-600 mb-4">
                              Price: {formatCurrency(parseFloat(item.price))}
                            </p>

                            {/* Quantity and Remove Controls */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <span className="text-sm font-medium text-gray-700">Quantity:</span>
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => handleQuantityChange(item.product_id, item.quantity - 1)}
                                    disabled={isUpdating || item.quantity <= 1}
                                    className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center font-medium transition-colors"
                                  >
                                    −
                                  </button>
                                  
                                  <span className="w-12 text-center font-medium">
                                    {isUpdating ? <LoadingSpinner size="sm" /> : item.quantity}
                                  </span>
                                  
                                  <button
                                    onClick={() => handleQuantityChange(item.product_id, item.quantity + 1)}
                                    disabled={isUpdating}
                                    className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center font-medium transition-colors"
                                  >
                                    +
                                  </button>
                                </div>
                              </div>

                              <button
                                onClick={() => handleRemoveItem(item.product_id)}
                                disabled={isUpdating}
                                className="flex items-center gap-2 text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                Remove
                              </button>
                            </div>
                          </div>

                          {/* Item Total */}
                          <div className="text-right">
                            <p className="text-lg font-semibold text-gray-900">
                              {formatCurrency(parseFloat(item.subtotal))}
                            </p>
                            <p className="text-sm text-gray-600">
                              {item.quantity} × {formatCurrency(parseFloat(item.price))}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 sticky top-8">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Order Summary</h2>
                </div>
                
                <div className="p-6">
                  {/* Pricing Breakdown */}
                  <div className="space-y-4 mb-6">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Subtotal ({cart!.total_items} items):</span>
                      <span className="font-medium">{formatCurrency(pricing.subtotal)}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Taxes (8%):</span>
                      <span className="font-medium">{formatCurrency(pricing.taxes)}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Shipping:</span>
                      <span className="font-medium">
                        {pricing.shipping === 0 ? (
                          <span className="text-green-600 font-semibold">FREE</span>
                        ) : (
                          formatCurrency(pricing.shipping)
                        )}
                      </span>
                    </div>
                    
                    {pricing.shipping === 0 && pricing.subtotal < 100 && (
                      <p className="text-sm text-green-600">
                        🎉 You saved {formatCurrency(9.99)} on shipping!
                      </p>
                    )}
                    
                    {pricing.shipping > 0 && (
                      <p className="text-sm text-gray-600">
                        Add {formatCurrency(100 - pricing.subtotal)} more for free shipping
                      </p>
                    )}
                    
                    <div className="border-t border-gray-200 pt-4">
                      <div className="flex justify-between text-lg font-semibold">
                        <span>Total:</span>
                        <span className="text-blue-600">{formatCurrency(pricing.total)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Checkout Button */}
                  <button
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    {isLoading ? <LoadingSpinner size="sm" /> : 'Proceed to Checkout'}
                  </button>

                  {/* Security Badge */}
                  <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    Secure Checkout
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;
