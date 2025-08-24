import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { cartService } from '../services/cartService';

const CartContext = createContext();

const cartReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CART':
      return {
        ...state,
        cart: action.payload,
        loading: false,
        error: null
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      };
    default:
      return state;
  }
};

const initialState = {
  cart: {
    customer_id: 'customer-123', // In real app, this would come from auth
    total_items: 0,
    subtotal: 0,
    items: []
  },
  loading: false,
  error: null
};

export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  const loadCart = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const cart = await cartService.getCart(state.cart.customer_id);
      dispatch({ type: 'SET_CART', payload: cart });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const addItemToCart = async (item) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await cartService.addItem({
        ...item,
        customer_id: state.cart.customer_id
      });
      dispatch({ type: 'SET_CART', payload: response.cart });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateItemQuantity = async (productId, quantity) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await cartService.updateItemQuantity(
        state.cart.customer_id,
        productId,
        quantity
      );
      dispatch({ type: 'SET_CART', payload: response.cart });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const removeItemFromCart = async (productId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await cartService.removeItem(state.cart.customer_id, productId);
      dispatch({ type: 'SET_CART', payload: response.cart });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const clearCart = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      await cartService.clearCart(state.cart.customer_id);
      dispatch({ type: 'SET_CART', payload: initialState.cart });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const checkout = async (checkoutData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await cartService.checkout({
        ...checkoutData,
        customer_id: state.cart.customer_id
      });
      if (response.success) {
        dispatch({ type: 'SET_CART', payload: initialState.cart });
      }
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  useEffect(() => {
    loadCart();
  }, []);

  const value = {
    ...state,
    addItemToCart,
    updateItemQuantity,
    removeItemFromCart,
    clearCart,
    checkout,
    clearError,
    loadCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
