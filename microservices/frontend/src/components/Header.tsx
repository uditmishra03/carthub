import React, { useState, useRef, useEffect } from 'react';
import { HeaderProps } from '../types';
import { formatCurrency } from '../utils';
import MiniCart from './MiniCart';

const Header: React.FC<HeaderProps & {
  onUpdateQuantity: (productId: string, quantity: number) => Promise<void>;
  onRemoveItem: (productId: string) => Promise<void>;
  isLoading: boolean;
}> = ({ 
  cart, 
  isApiHealthy, 
  onCartClick, 
  onUpdateQuantity, 
  onRemoveItem, 
  isLoading 
}) => {
  const [showMiniCart, setShowMiniCart] = useState(false);
  const cartButtonRef = useRef<HTMLButtonElement>(null);
  const miniCartRef = useRef<HTMLDivElement>(null);
  const hoverTimeoutRef = useRef<NodeJS.Timeout>();

  const handleMouseEnter = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    setShowMiniCart(true);
  };

  const handleMouseLeave = () => {
    hoverTimeoutRef.current = setTimeout(() => {
      setShowMiniCart(false);
    }, 300); // 300ms delay before hiding
  };

  const handleMiniCartMouseEnter = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
  };

  const handleMiniCartMouseLeave = () => {
    hoverTimeoutRef.current = setTimeout(() => {
      setShowMiniCart(false);
    }, 300);
  };

  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

  const cartItemCount = cart?.total_items || 0;
  const cartSubtotal = cart?.subtotal ? parseFloat(cart.subtotal) : 0;

  return (
    <header className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="text-3xl">🛒</div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Shopping Cart
              </h1>
              <p className="text-sm text-gray-600">
                Modern E-commerce Experience
              </p>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-6">
            {/* API Status */}
            <div className="flex items-center gap-2">
              <div 
                className={`w-2 h-2 rounded-full ${
                  isApiHealthy ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                {isApiHealthy ? 'API Online' : 'API Offline'}
              </span>
            </div>

            {/* Cart Button */}
            <div className="relative">
              <button
                ref={cartButtonRef}
                onClick={onCartClick}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                className="relative flex items-center gap-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                {/* Cart Icon */}
                <div className="relative">
                  <svg 
                    className="w-6 h-6" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 11-4 0v-6m4 0V9a2 2 0 10-4 0v4.01" 
                    />
                  </svg>
                  
                  {/* Cart Badge */}
                  {cartItemCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold animate-pulse">
                      {cartItemCount > 99 ? '99+' : cartItemCount}
                    </span>
                  )}
                </div>

                {/* Cart Info */}
                <div className="text-left">
                  <div className="text-sm font-semibold">
                    {cartItemCount} {cartItemCount === 1 ? 'Item' : 'Items'}
                  </div>
                  <div className="text-xs opacity-90">
                    {formatCurrency(cartSubtotal)}
                  </div>
                </div>
              </button>

              {/* Mini Cart */}
              {showMiniCart && (
                <div
                  ref={miniCartRef}
                  onMouseEnter={handleMiniCartMouseEnter}
                  onMouseLeave={handleMiniCartMouseLeave}
                  className="absolute right-0 top-full mt-2 z-50"
                >
                  <MiniCart
                    cart={cart}
                    isVisible={showMiniCart}
                    onClose={() => setShowMiniCart(false)}
                    onViewCart={onCartClick}
                    onUpdateQuantity={onUpdateQuantity}
                    onRemoveItem={onRemoveItem}
                    isLoading={isLoading}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                isApiHealthy ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-xs text-gray-600">
                API {isApiHealthy ? 'Online' : 'Offline'}
              </span>
            </div>

            {/* Cart Info */}
            {cart && cart.items.length > 0 ? (
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {cart.total_items} {cart.total_items === 1 ? 'item' : 'items'}
                  </div>
                  <div className="text-lg font-bold text-primary-600">
                    {formatCurrency(cart.subtotal)}
                  </div>
                </div>
                
                <div className="relative">
                  <div className="text-2xl">🛒</div>
                  <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cart.total_items > 99 ? '99+' : cart.total_items}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-500">
                <div className="text-2xl">🛒</div>
                <span className="text-sm">Empty Cart</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
