// API Types
export interface CartItem {
  product_id: string;
  product_name: string;
  price: string;
  quantity: number;
  subtotal: string;
  image?: string;
}

export interface Cart {
  customer_id: string;
  total_items: number;
  subtotal: string;
  items: CartItem[];
  taxes?: string;
  shipping?: string;
  total?: string;
}

export interface CartPricing {
  subtotal: number;
  taxes: number;
  shipping: number;
  total: number;
}

export interface AddItemRequest {
  customer_id: string;
  product_id: string;
  product_name: string;
  price: string;
  quantity: number;
}

export interface AddItemResponse {
  success: boolean;
  cart?: Cart;
  error?: string;
}

// UI Types
export interface Product {
  id: string;
  name: string;
  price: number;
  description: string;
  image: string;
  category: string;
  inStock: boolean;
}

export interface LoadingState {
  isLoading: boolean;
  operation?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}

// Form Types
export interface AddToCartForm {
  quantity: number;
}

// Component Props
export interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product, quantity: number) => Promise<void>;
  isLoading: boolean;
}

export interface CartSummaryProps {
  cart: Cart | null;
  isLoading: boolean;
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export interface HeaderProps {
  cart: Cart | null;
  isApiHealthy: boolean;
  onCartClick: () => void;
}

export interface MiniCartProps {
  cart: Cart | null;
  isVisible: boolean;
  onClose: () => void;
  onViewCart: () => void;
  onUpdateQuantity: (productId: string, quantity: number) => Promise<void>;
  onRemoveItem: (productId: string) => Promise<void>;
  isLoading: boolean;
}

export interface CartPageProps {
  cart: Cart | null;
  onUpdateQuantity: (productId: string, quantity: number) => Promise<void>;
  onRemoveItem: (productId: string) => Promise<void>;
  onBackToShopping: () => void;
  isLoading: boolean;
}

// Navigation Types
export type AppView = 'products' | 'cart';

// Local Storage Types
export interface StoredCart {
  items: CartItem[];
  timestamp: number;
  customerId: string;
}
