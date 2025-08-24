import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ProductList from './components/ProductList';
import Cart from './components/Cart';
import Checkout from './components/Checkout';
import { CartProvider } from './components/CartContext';
import './styles/App.css';

function App() {
  const [currentView, setCurrentView] = useState('products');

  return (
    <CartProvider>
      <div className="App">
        <Header currentView={currentView} setCurrentView={setCurrentView} />
        <main className="main-content">
          {currentView === 'products' && <ProductList />}
          {currentView === 'cart' && <Cart />}
          {currentView === 'checkout' && <Checkout />}
        </main>
      </div>
    </CartProvider>
  );
}

export default App;
