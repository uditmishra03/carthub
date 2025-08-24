import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || 'Server error';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error('Request failed');
    }
  }
);

export const cartService = {
  // Get cart for customer
  async getCart(customerId) {
    const response = await api.get(`/cart/${customerId}`);
    return response.cart;
  },

  // Add item to cart
  async addItem(item) {
    return await api.post('/cart/items', item);
  },

  // Update item quantity
  async updateItemQuantity(customerId, productId, quantity) {
    return await api.put(`/cart/${customerId}/items/${productId}?quantity=${quantity}`);
  },

  // Remove item from cart
  async removeItem(customerId, productId) {
    return await api.delete(`/cart/${customerId}/items/${productId}`);
  },

  // Clear cart
  async clearCart(customerId) {
    return await api.delete(`/cart/${customerId}`);
  },

  // Checkout
  async checkout(checkoutData) {
    return await api.post('/cart/checkout', checkoutData);
  },

  // Health check
  async healthCheck() {
    return await api.get('/health');
  }
};
