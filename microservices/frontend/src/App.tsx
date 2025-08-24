import React, { useState, useEffect, useCallback } from 'react';
import { Cart, Product, AddItemRequest, LoadingState, ErrorState, AppView } from './types';
import { CartService } from './services/cartService';
import { generateCustomerId, generateProductId, formatErrorMessage, storage } from './utils';
import ErrorBoundary from './components/ErrorBoundary';
import Header from './components/Header';
import ProductCard from './components/ProductCard';
import CartSummary from './components/CartSummary';
import CartPage from './components/CartPage';
import LoadingSpinner from './components/LoadingSpinner';
import { ToastManager } from './components/Toast';
import './styles/globals.css';

// Sample Products Data with images
const SAMPLE_PRODUCTS: Product[] = [
  {
    id: 'laptop-001',
    name: 'MacBook Pro 16-inch',
    price: 2499.99,
    description: 'Powerful laptop with M2 Pro chip, 16GB RAM, and 512GB SSD. Perfect for developers and creative professionals.',
    image: '',
    category: 'Electronics',
    inStock: true
  },
  {
    id: 'mouse-001',
    name: 'Magic Mouse',
    price: 79.99,
    description: 'Wireless mouse with multi-touch surface and rechargeable battery. Seamless scrolling and gesture support.',
    image: '',
    category: 'Accessories',
    inStock: true
  },
  {
    id: 'keyboard-001',
    name: 'Mechanical Keyboard',
    price: 129.99,
    description: 'Premium mechanical keyboard with RGB backlighting and tactile switches. Built for gaming and productivity.',
    image: '',
    category: 'Accessories',
    inStock: true
  },
  {
    id: 'monitor-001',
    name: '4K Monitor 27-inch',
    price: 399.99,
    description: 'Ultra HD 4K monitor with IPS panel and USB-C connectivity. Perfect for design work and entertainment.',
    image: '',
    category: 'Electronics',
    inStock: true
  },
  {
    id: 'headphones-001',
    name: 'Noise-Canceling Headphones',
    price: 299.99,
    description: 'Premium wireless headphones with active noise cancellation and 30-hour battery life.',
    image: '',
    category: 'Audio',
    inStock: true
  },
  {
    id: 'tablet-001',
    name: 'iPad Pro 12.9-inch',
    price: 1099.99,
    description: 'Professional tablet with M2 chip, Liquid Retina XDR display, and Apple Pencil support.',
    image: '',
    category: 'Electronics',
    inStock: true
  }
];

const App: React.FC = () => {
  // State Management
  const [currentView, setCurrentView] = useState<AppView>('products');
  const [cart, setCart] = useState<Cart | null>(null);
  const [customerId, setCustomerId] = useState<string>('');
  const [loadingState, setLoadingState] = useState<LoadingState>({ isLoading: false });
  const [errorState, setErrorState] = useState<ErrorState>({ hasError: false });
  const [isApiHealthy, setIsApiHealthy] = useState<boolean>(true);

  // Initialize application
  useEffect(() => {
    initializeApp();
    
    // Check API health periodically
    const healthCheckInterval = setInterval(checkApiHealth, 30000);
    
    return () => clearInterval(healthCheckInterval);
  }, []);

  const initializeApp = useCallback(async () => {
    try {
      // Try to load existing customer ID and cart from storage
      let storedCustomerId = CartService.getStoredCustomerId();
      let storedCart = CartService.loadCartFromStorage();

      if (!storedCustomerId) {
        storedCustomerId = generateCustomerId();
      }

      setCustomerId(storedCustomerId);

      if (storedCart && storedCart.customerId === storedCustomerId) {
        // Reconstruct cart object from stored data
        const reconstructedCart: Cart = {
          customer_id: storedCart.customerId,
          items: storedCart.items,
          total_items: storedCart.items.reduce((sum, item) => sum + item.quantity, 0),
          subtotal: storedCart.items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0).toFixed(2)
        };
        setCart(reconstructedCart);
      }

      // Initial API health check
      await checkApiHealth();
    } catch (error) {
      console.error('Failed to initialize app:', error);
      setErrorState({
        hasError: true,
        message: 'Failed to initialize application',
        code: 'INIT_ERROR'
      });
    }
  }, []);

  const checkApiHealth = useCallback(async () => {
    try {
      const isHealthy = await CartService.healthCheck();
      setIsApiHealthy(isHealthy);
    } catch (error) {
      setIsApiHealthy(false);
    }
  }, []);

  // Navigation handlers
  const handleCartClick = useCallback(() => {
    setCurrentView('cart');
  }, []);

  const handleBackToShopping = useCallback(() => {
    setCurrentView('products');
  }, []);

  // Cart operations
  const handleAddToCart = useCallback(async (product: Product, quantity: number) => {
    if (!customerId) {
      ToastManager.showError('Customer ID not available');
      return;
    }

    setLoadingState({ isLoading: true, operation: 'add_item' });
    setErrorState({ hasError: false });

    try {
      const request: AddItemRequest = {
        customer_id: customerId,
        product_id: product.id,
        product_name: product.name,
        price: product.price.toString(),
        quantity: quantity
      };

      // Validate request
      const validationErrors = CartService.validateAddItemRequest(request);
      if (validationErrors.length > 0) {
        throw new Error(validationErrors.join(', '));
      }

      const response = await CartService.addItemToCartWithRetry(request, 3);

      if (response.success && response.cart) {
        setCart(response.cart);
        ToastManager.showSuccess(`Added ${quantity}x ${product.name} to cart!`);
      } else {
        throw new Error(response.error || 'Failed to add item to cart');
      }
    } catch (error) {
      const errorMessage = formatErrorMessage(error);
      setErrorState({
        hasError: true,
        message: errorMessage,
        code: 'ADD_ITEM_ERROR'
      });
      ToastManager.showError(`Error: ${errorMessage}`);
    } finally {
      setLoadingState({ isLoading: false });
    }
  }, [customerId]);

  const handleUpdateQuantity = useCallback(async (productId: string, quantity: number) => {
    if (!customerId || !cart) return;

    const item = cart.items.find(item => item.product_id === productId);
    if (!item) return;

    try {
      const response = await CartService.updateItemQuantity(
        customerId,
        productId,
        item.product_name,
        item.price,
        quantity
      );

      if (response.success && response.cart) {
        setCart(response.cart);
        ToastManager.showSuccess('Cart updated successfully!');
      } else {
        throw new Error(response.error || 'Failed to update cart');
      }
    } catch (error) {
      const errorMessage = formatErrorMessage(error);
      ToastManager.showError(`Error: ${errorMessage}`);
    }
  }, [customerId, cart]);

  const handleRemoveItem = useCallback(async (productId: string) => {
    if (!customerId) return;

    try {
      const response = await CartService.removeItemFromCart(customerId, productId);

      if (response.success && response.cart) {
        setCart(response.cart);
        ToastManager.showSuccess('Item removed from cart');
      } else {
        throw new Error(response.error || 'Failed to remove item');
      }
    } catch (error) {
      const errorMessage = formatErrorMessage(error);
      ToastManager.showError(`Error: ${errorMessage}`);
    }
  }, [customerId]);

  // Error boundary fallback
  if (errorState.hasError && errorState.code === 'INIT_ERROR') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Application Error</h1>
          <p className="text-gray-600 mb-4">{errorState.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Reload Application
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <Header
          cart={cart}
          isApiHealthy={isApiHealthy}
          onCartClick={handleCartClick}
          onUpdateQuantity={handleUpdateQuantity}
          onRemoveItem={handleRemoveItem}
          isLoading={loadingState.isLoading}
        />

        {/* Main Content */}
        <main>
          {currentView === 'products' ? (
            /* Products View */
            <div className="container mx-auto px-4 py-8">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Products Grid */}
                <div className="lg:col-span-3">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Featured Products</h2>
                    <p className="text-gray-600">Discover our latest collection of premium tech products</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {SAMPLE_PRODUCTS.map((product) => (
                      <ProductCard
                        key={product.id}
                        product={product}
                        onAddToCart={handleAddToCart}
                        isLoading={loadingState.isLoading && loadingState.operation === 'add_item'}
                      />
                    ))}
                  </div>
                </div>

                {/* Cart Summary Sidebar */}
                <div className="lg:col-span-1">
                  <div className="sticky top-24">
                    <CartSummary
                      cart={cart}
                      isLoading={loadingState.isLoading}
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Cart View */
            <CartPage
              cart={cart}
              onUpdateQuantity={handleUpdateQuantity}
              onRemoveItem={handleRemoveItem}
              onBackToShopping={handleBackToShopping}
              isLoading={loadingState.isLoading}
            />
          )}
        </main>

        {/* Loading Overlay */}
        {loadingState.isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 flex items-center gap-4">
              <LoadingSpinner size="md" />
              <span className="text-gray-700">
                {loadingState.operation === 'add_item' ? 'Adding to cart...' : 'Processing...'}
              </span>
            </div>
          </div>
        )}

        {/* Customer Info (Development) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="fixed bottom-4 left-4 bg-black bg-opacity-75 text-white p-2 rounded text-xs font-mono">
            Customer: {customerId}
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default App;
    inStock: true
  },
  {
    id: 'keyboard-001',
    name: 'Mechanical Keyboard',
    price: 129.99,
    description: 'Premium mechanical keyboard with RGB backlighting and tactile switches. Built for gaming and productivity.',
    image: '',
    category: 'Accessories',
    inStock: true
  },
  {
    id: 'monitor-001',
    name: '4K Monitor 27-inch',
    price: 399.99,
    description: 'Ultra HD 4K monitor with IPS panel and USB-C connectivity. Perfect for design work and entertainment.',
    image: '',
    category: 'Electronics',
    inStock: true
  },
  {
    id: 'headphones-001',
    name: 'Wireless Headphones',
    price: 199.99,
    description: 'Premium noise-canceling headphones with 30-hour battery life and superior sound quality.',
    image: '',
    category: 'Audio',
    inStock: true
  },
  {
    id: 'tablet-001',
    name: 'iPad Pro 12.9-inch',
    price: 1099.99,
    description: 'Professional tablet with M2 chip, Liquid Retina display, and Apple Pencil support.',
    image: '',
    category: 'Electronics',
    inStock: false
  }
];

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

const App: React.FC = () => {
  // State Management
  const [cart, setCart] = useState<Cart | null>(null);
  const [customerId] = useState<string>(() => 
    storage.get('customerId', generateCustomerId())
  );
  const [loading, setLoading] = useState<LoadingState>({ isLoading: false });
  const [error, setError] = useState<ErrorState>({ hasError: false });
  const [isApiHealthy, setIsApiHealthy] = useState<boolean>(true);
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Toast Management
  const addToast = useCallback((message: string, type: Toast['type'], duration?: number) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast: Toast = { id, message, type, duration };
    setToasts(prev => [...prev, newToast]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  // API Health Check
  const checkApiHealth = useCallback(async () => {
    try {
      const isHealthy = await CartService.healthCheck();
      setIsApiHealthy(isHealthy);
      
      if (!isHealthy) {
        addToast('API is currently unavailable. Some features may not work.', 'warning');
      }
    } catch (error) {
      setIsApiHealthy(false);
      console.error('Health check failed:', error);
    }
  }, [addToast]);

  // Initialize App
  useEffect(() => {
    // Store customer ID
    storage.set('customerId', customerId);
    
    // Check API health
    checkApiHealth();
    
    // Set up periodic health checks
    const healthCheckInterval = setInterval(checkApiHealth, 30000); // Every 30 seconds
    
    return () => clearInterval(healthCheckInterval);
  }, [customerId, checkApiHealth]);

  // Add Item to Cart
  const handleAddToCart = useCallback(async (product: Product, quantity: number) => {
    if (!isApiHealthy) {
      addToast('API is currently unavailable. Please try again later.', 'error');
      return;
    }

    setLoading({ isLoading: true, operation: `Adding ${product.name} to cart` });
    setError({ hasError: false });

    try {
      const request: AddItemRequest = {
        customer_id: customerId,
        product_id: generateProductId(product.name),
        product_name: product.name,
        price: product.price.toString(),
        quantity
      };

      // Validate request
      const validationErrors = CartService.validateAddItemRequest(request);
      if (validationErrors.length > 0) {
        throw new Error(validationErrors.join(', '));
      }

      console.log('🛒 Adding to cart:', request);

      // Add item with retry logic
      const response = await CartService.addItemToCartWithRetry(request, 3);

      if (response.success && response.cart) {
        setCart(response.cart);
        addToast(
          `✅ Added ${quantity} ${product.name}${quantity > 1 ? 's' : ''} to cart!`, 
          'success'
        );
        
        console.log('✅ Cart updated:', response.cart);
      } else {
        throw new Error(response.error || 'Failed to add item to cart');
      }
    } catch (error) {
      const errorMessage = formatErrorMessage(error);
      console.error('❌ Failed to add to cart:', error);
      
      setError({ 
        hasError: true, 
        message: errorMessage 
      });
      
      addToast(`❌ Failed to add ${product.name}: ${errorMessage}`, 'error');
    } finally {
      setLoading({ isLoading: false });
    }
  }, [customerId, isApiHealthy, addToast]);

  // Clear Error
  const clearError = useCallback(() => {
    setError({ hasError: false });
  }, []);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <Header cart={cart} isApiHealthy={isApiHealthy} />

        {/* Main Content */}
        <main className="container py-8">
          {/* Error Banner */}
          {error.hasError && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 animate-fade-in">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <span className="text-red-500 text-xl">⚠️</span>
                  <div>
                    <h3 className="font-medium text-red-800">Error</h3>
                    <p className="text-red-700 text-sm mt-1">{error.message}</p>
                  </div>
                </div>
                <button
                  onClick={clearError}
                  className="text-red-500 hover:text-red-700 transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Loading Overlay */}
          {loading.isLoading && (
            <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 animate-fade-in">
              <div className="flex items-center gap-3">
                <LoadingSpinner size="sm" />
                <span className="text-blue-700 font-medium">
                  {loading.operation || 'Processing...'}
                </span>
              </div>
            </div>
          )}

          {/* Welcome Section */}
          <div className="mb-8 text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to Our Store! 🛍️
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Discover amazing products and add them to your cart. 
              This demo showcases our robust shopping cart API with real-time updates, 
              error handling, and seamless user experience.
            </p>
            <div className="mt-4 text-sm text-gray-500">
              Customer ID: <code className="bg-gray-100 px-2 py-1 rounded font-mono">
                {customerId}
              </code>
            </div>
          </div>

          {/* Main Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Products Grid */}
            <div className="lg:col-span-2">
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Featured Products
                </h3>
                <p className="text-gray-600">
                  Choose from our selection of premium products
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {SAMPLE_PRODUCTS.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={handleAddToCart}
                    isLoading={loading.isLoading}
                  />
                ))}
              </div>
            </div>

            {/* Cart Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-24">
                <CartSummary 
                  cart={cart} 
                  isLoading={loading.isLoading} 
                />
              </div>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-16 pt-8 border-t text-center text-gray-500">
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">
                🚀 Powered by Modern Technology
              </h4>
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <span>React + TypeScript</span>
                <span>•</span>
                <span>AWS Lambda</span>
                <span>•</span>
                <span>DynamoDB</span>
                <span>•</span>
                <span>API Gateway</span>
              </div>
            </div>
            <p className="text-sm">
              Built with ❤️ using Clean Architecture and Test-Driven Development
            </p>
          </footer>
        </main>

        {/* Toast Notifications */}
        <ToastManager toasts={toasts} removeToast={removeToast} />
      </div>
    </ErrorBoundary>
  );
};

export default App;
