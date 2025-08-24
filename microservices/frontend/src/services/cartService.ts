import axios, { AxiosResponse } from 'axios';
import { AddItemRequest, AddItemResponse, Cart, StoredCart } from '../types';

// API Configuration
const API_BASE_URL = 'https://mk8ppghx0d.execute-api.us-east-1.amazonaws.com/prod';
const CART_ITEMS_ENDPOINT = `${API_BASE_URL}/cart/items`;

// Local Storage Keys
const CART_STORAGE_KEY = 'shopping_cart';
const CUSTOMER_ID_KEY = 'customer_id';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message);
    
    // Enhanced error handling
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.error || `Server Error: ${error.response.status}`;
      throw new Error(errorMessage);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network Error: Unable to reach the server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(`Request Error: ${error.message}`);
    }
  }
);

export class CartService {
  // Local Storage Management
  static saveCartToStorage(cart: Cart): void {
    try {
      const storedCart: StoredCart = {
        items: cart.items,
        timestamp: Date.now(),
        customerId: cart.customer_id
      };
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(storedCart));
      localStorage.setItem(CUSTOMER_ID_KEY, cart.customer_id);
    } catch (error) {
      console.warn('Failed to save cart to localStorage:', error);
    }
  }

  static loadCartFromStorage(): StoredCart | null {
    try {
      const stored = localStorage.getItem(CART_STORAGE_KEY);
      if (!stored) return null;
      
      const cart: StoredCart = JSON.parse(stored);
      
      // Check if cart is not too old (24 hours)
      const isExpired = Date.now() - cart.timestamp > 24 * 60 * 60 * 1000;
      if (isExpired) {
        this.clearCartFromStorage();
        return null;
      }
      
      return cart;
    } catch (error) {
      console.warn('Failed to load cart from localStorage:', error);
      return null;
    }
  }

  static clearCartFromStorage(): void {
    try {
      localStorage.removeItem(CART_STORAGE_KEY);
    } catch (error) {
      console.warn('Failed to clear cart from localStorage:', error);
    }
  }

  static getStoredCustomerId(): string | null {
    try {
      return localStorage.getItem(CUSTOMER_ID_KEY);
    } catch (error) {
      console.warn('Failed to get customer ID from localStorage:', error);
      return null;
    }
  }

  // API Methods
  static async addItemToCart(request: AddItemRequest): Promise<AddItemResponse> {
    try {
      const response = await apiClient.post<AddItemResponse>(CART_ITEMS_ENDPOINT, request);
      
      // Save to localStorage on success
      if (response.data.success && response.data.cart) {
        this.saveCartToStorage(response.data.cart);
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  static async updateItemQuantity(customerId: string, productId: string, productName: string, price: string, quantity: number): Promise<AddItemResponse> {
    const request: AddItemRequest = {
      customer_id: customerId,
      product_id: productId,
      product_name: productName,
      price: price,
      quantity: quantity
    };

    return this.addItemToCart(request);
  }

  static async removeItemFromCart(customerId: string, productId: string): Promise<AddItemResponse> {
    // Since the API doesn't have a delete endpoint, we simulate removal by setting quantity to 0
    // In a real implementation, you'd have a DELETE endpoint
    const request: AddItemRequest = {
      customer_id: customerId,
      product_id: productId,
      product_name: 'Remove Item',
      price: '0',
      quantity: 0
    };

    try {
      // For now, we'll simulate removal by updating localStorage directly
      const storedCart = this.loadCartFromStorage();
      if (storedCart) {
        const updatedItems = storedCart.items.filter(item => item.product_id !== productId);
        const updatedCart: Cart = {
          customer_id: customerId,
          items: updatedItems,
          total_items: updatedItems.reduce((sum, item) => sum + item.quantity, 0),
          subtotal: updatedItems.reduce((sum, item) => sum + parseFloat(item.subtotal), 0).toFixed(2)
        };
        
        this.saveCartToStorage(updatedCart);
        
        return {
          success: true,
          cart: updatedCart
        };
      }
      
      throw new Error('Cart not found');
    } catch (error) {
      throw error;
    }
  }

  // Retry logic for network resilience
  static async addItemToCartWithRetry(request: AddItemRequest, maxRetries: number = 3): Promise<AddItemResponse> {
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.addItemToCart(request);
      } catch (error) {
        lastError = error as Error;
        console.warn(`Attempt ${attempt} failed:`, error);
        
        if (attempt < maxRetries) {
          // Exponential backoff: wait 1s, 2s, 4s
          const delay = Math.pow(2, attempt - 1) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError!;
  }

  // Health check
  static async healthCheck(): Promise<boolean> {
    try {
      const testRequest: AddItemRequest = {
        customer_id: 'health-check',
        product_id: 'health-check',
        product_name: 'Health Check',
        price: '0.01',
        quantity: 1
      };
      
      await apiClient.post(CART_ITEMS_ENDPOINT, testRequest);
      return true;
    } catch (error) {
      console.warn('Health check failed:', error);
      return false;
    }
  }

  // Validation
  static validateAddItemRequest(request: AddItemRequest): string[] {
    const errors: string[] = [];
    
    if (!request.customer_id?.trim()) {
      errors.push('Customer ID is required');
    }
    
    if (!request.product_id?.trim()) {
      errors.push('Product ID is required');
    }
    
    if (!request.product_name?.trim()) {
      errors.push('Product name is required');
    }
    
    if (!request.price || isNaN(parseFloat(request.price)) || parseFloat(request.price) <= 0) {
      errors.push('Valid price is required');
    }
    
    if (!request.quantity || request.quantity <= 0 || !Number.isInteger(request.quantity)) {
      errors.push('Quantity must be a positive integer');
    }
    
    return errors;
  }
}
);

export class CartService {
  /**
   * Add an item to the shopping cart
   */
  static async addItemToCart(request: AddItemRequest): Promise<AddItemResponse> {
    try {
      const response = await apiClient.post<AddItemResponse>('/cart/items', request);
      return response.data;
    } catch (error) {
      console.error('Failed to add item to cart:', error);
      throw error;
    }
  }

  /**
   * Add item with retry logic for resilience
   */
  static async addItemToCartWithRetry(
    request: AddItemRequest, 
    maxRetries: number = 3
  ): Promise<AddItemResponse> {
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`🔄 Attempt ${attempt}/${maxRetries} to add item to cart`);
        return await this.addItemToCart(request);
      } catch (error) {
        lastError = error as Error;
        console.warn(`⚠️ Attempt ${attempt} failed:`, error);
        
        if (attempt < maxRetries) {
          // Exponential backoff: wait 1s, 2s, 4s...
          const delay = Math.pow(2, attempt - 1) * 1000;
          console.log(`⏳ Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw new Error(`Failed after ${maxRetries} attempts: ${lastError!.message}`);
  }

  /**
   * Validate request data before sending
   */
  static validateAddItemRequest(request: AddItemRequest): string[] {
    const errors: string[] = [];
    
    if (!request.customer_id?.trim()) {
      errors.push('Customer ID is required');
    }
    
    if (!request.product_id?.trim()) {
      errors.push('Product ID is required');
    }
    
    if (!request.product_name?.trim()) {
      errors.push('Product name is required');
    }
    
    if (!request.price || parseFloat(request.price) <= 0) {
      errors.push('Price must be greater than 0');
    }
    
    if (!request.quantity || request.quantity <= 0) {
      errors.push('Quantity must be greater than 0');
    }
    
    if (request.quantity > 99) {
      errors.push('Quantity cannot exceed 99');
    }
    
    return errors;
  }

  /**
   * Health check for the API
   */
  static async healthCheck(): Promise<boolean> {
    try {
      // Try to add a test item to validate API is working
      const testRequest: AddItemRequest = {
        customer_id: 'health-check',
        product_id: 'health-check-product',
        product_name: 'Health Check Product',
        price: '0.01',
        quantity: 1
      };
      
      await this.addItemToCart(testRequest);
      return true;
    } catch (error) {
      console.error('API Health Check Failed:', error);
      return false;
    }
  }
}

export default CartService;
