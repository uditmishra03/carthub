/**
 * CartHub - Modern Shopping Cart Application
 * Version: 1.0.0
 * Author: Amazon Q Workshop
 */

console.log('🛒 Shopping Cart Loading...');

// Sample products
const PRODUCTS = [
    {
        id: 'laptop-001',
        name: 'MacBook Pro 16-inch',
        price: 2499.99,
        description: 'Powerful laptop with M2 Pro chip, 16GB RAM, and 512GB SSD. Perfect for developers and creative professionals.',
        emoji: '💻'
    },
    {
        id: 'mouse-001',
        name: 'Magic Mouse',
        price: 79.99,
        description: 'Wireless mouse with multi-touch surface and rechargeable battery. Seamless scrolling and gesture support.',
        emoji: '🖱️'
    },
    {
        id: 'keyboard-001',
        name: 'Mechanical Keyboard',
        price: 129.99,
        description: 'Premium mechanical keyboard with RGB backlighting and tactile switches. Built for gaming and productivity.',
        emoji: '⌨️'
    },
    {
        id: 'monitor-001',
        name: '4K Monitor 27-inch',
        price: 399.99,
        description: 'Ultra HD 4K monitor with IPS panel and USB-C connectivity. Perfect for design work and entertainment.',
        emoji: '🖥️'
    },
    {
        id: 'headphones-001',
        name: 'Noise-Canceling Headphones',
        price: 299.99,
        description: 'Premium wireless headphones with active noise cancellation and 30-hour battery life.',
        emoji: '🎧'
    },
    {
        id: 'tablet-001',
        name: 'iPad Pro 12.9-inch',
        price: 1099.99,
        description: 'Professional tablet with M2 chip, Liquid Retina XDR display, and Apple Pencil support.',
        emoji: '📱'
    }
];

// Global state
let cart = { items: [], total_items: 0, subtotal: 0 };
let currentView = 'products';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing shopping cart...');
    
    renderProducts();
    setupEventListeners();
    updateCartDisplay();
    
    console.log('✅ Shopping cart initialized');
});

// Setup event listeners
function setupEventListeners() {
    console.log('🔧 Setting up event listeners...');
    
    const cartButton = document.getElementById('cartButton');
    const sidePanelOverlay = document.getElementById('sidePanelOverlay');
    const closePanel = document.getElementById('closePanel');
    const checkoutModalOverlay = document.getElementById('checkoutModalOverlay');
    const closeCheckout = document.getElementById('closeCheckout');

    // Cart button click - show side panel with all items
    if (cartButton) {
        cartButton.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('🛒 Cart button clicked - showing side panel');
            showSidePanel();
        });
    }

    // Close panel events
    if (sidePanelOverlay) {
        sidePanelOverlay.addEventListener('click', closeSidePanel);
    }
    if (closePanel) {
        closePanel.addEventListener('click', closeSidePanel);
    }

    // Checkout modal events
    if (checkoutModalOverlay) {
        checkoutModalOverlay.addEventListener('click', (e) => {
            if (e.target === checkoutModalOverlay) {
                closeCheckoutModal();
            }
        });
    }
    if (closeCheckout) {
        closeCheckout.addEventListener('click', closeCheckoutModal);
    }

    // Escape key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (document.getElementById('checkoutModalOverlay').classList.contains('show')) {
                closeCheckoutModal();
            } else if (document.getElementById('sidePanelOverlay').classList.contains('show')) {
                closeSidePanel();
            }
        }
    });

    console.log('✅ Event listeners attached');
}

// Navigation functions
function showCartPage() {
    console.log('📄 Showing cart page');
    currentView = 'cart';
    
    const productsView = document.getElementById('productsView');
    const cartView = document.getElementById('cartView');
    
    if (productsView && cartView) {
        productsView.classList.add('hidden');
        cartView.classList.add('active');
        closeSidePanel();
        updateCartPageDisplay();
        console.log('✅ Cart page displayed');
    }
}

function showProductsPage() {
    console.log('📄 Showing products page');
    currentView = 'products';
    
    const productsView = document.getElementById('productsView');
    const cartView = document.getElementById('cartView');
    
    if (productsView && cartView) {
        productsView.classList.remove('hidden');
        cartView.classList.remove('active');
        console.log('✅ Products page displayed');
    }
}

// Update cart page display
function updateCartPageDisplay() {
    console.log('🔄 Updating cart page display');
    const isEmpty = !cart.items || cart.items.length === 0;

    // Toggle empty state
    document.getElementById('emptyCart').style.display = isEmpty ? 'block' : 'none';
    document.getElementById('cartContent').style.display = isEmpty ? 'none' : 'block';

    if (!isEmpty) {
        // Render cart items
        const cartItemsList = document.getElementById('cartItemsList');
        if (cartItemsList) {
            cartItemsList.innerHTML = cart.items.map(item => `
                <div class="cart-item">
                    <div class="cart-item-image">${item.emoji || '📦'}</div>
                    <div class="cart-item-details">
                        <h3 class="cart-item-name">${item.product_name}</h3>
                        <p class="cart-item-price">$${parseFloat(item.price).toFixed(2)}</p>
                        <div class="cart-item-controls">
                            <div class="cart-item-quantity">
                                <span>Qty:</span>
                                <button class="quantity-btn" onclick="updateQuantityAndRefresh('${item.product_id}', ${item.quantity - 1})" ${item.quantity <= 1 ? 'disabled' : ''}>−</button>
                                <span class="quantity-display">${item.quantity}</span>
                                <button class="quantity-btn" onclick="updateQuantityAndRefresh('${item.product_id}', ${item.quantity + 1})">+</button>
                            </div>
                            <button class="cart-item-remove" onclick="removeItemAndRefresh('${item.product_id}')">Remove</button>
                        </div>
                    </div>
                    <div class="cart-item-total">
                        <div class="cart-item-subtotal">$${parseFloat(item.subtotal).toFixed(2)}</div>
                        <div class="cart-item-calculation">${item.quantity} × $${parseFloat(item.price).toFixed(2)}</div>
                    </div>
                </div>
            `).join('');
        }

        // Calculate pricing
        const subtotal = cart.subtotal || 0;
        const taxes = subtotal * 0.08; // 8% tax
        const shipping = subtotal > 100 ? 0 : 9.99; // Free shipping over $100
        const total = subtotal + taxes + shipping;

        // Update order summary
        document.getElementById('cartPageItemCount').textContent = cart.total_items;
        document.getElementById('cartPageSubtotal').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('cartPageTaxes').textContent = `$${taxes.toFixed(2)}`;
        document.getElementById('cartPageShipping').textContent = shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`;
        document.getElementById('cartPageTotal').textContent = `$${total.toFixed(2)}`;

        console.log('✅ Cart page items rendered:', cart.items.length);
    }
}

// Update quantity and refresh cart page
function updateQuantityAndRefresh(productId, newQuantity) {
    updateQuantity(productId, newQuantity);
    updateCartPageDisplay();
}

// Remove item and refresh cart page
function removeItemAndRefresh(productId) {
    removeItem(productId);
    updateCartPageDisplay();
}

// Process checkout
function processCheckout() {
    console.log('💳 Starting checkout process...');
    
    if (!cart.items || cart.items.length === 0) {
        alert('Your cart is empty');
        return;
    }

    showCheckoutModal();
}

// Show checkout modal
function showCheckoutModal() {
    const overlay = document.getElementById('checkoutModalOverlay');
    const content = document.getElementById('checkoutModalContent');
    
    if (!overlay || !content) return;

    // Calculate totals
    const subtotal = cart.subtotal || 0;
    const taxes = subtotal * 0.08;
    const shipping = subtotal > 100 ? 0 : 9.99;
    const total = subtotal + taxes + shipping;

    // Generate checkout form
    content.innerHTML = `
        <div class="checkout-step">
            <h3>Order Summary</h3>
            <div class="checkout-summary">
                ${cart.items.map(item => `
                    <div class="checkout-item">
                        <div>
                            <div class="checkout-item-name">${item.product_name}</div>
                            <div class="checkout-item-details">Qty: ${item.quantity} × $${parseFloat(item.price).toFixed(2)}</div>
                        </div>
                        <div class="checkout-item-details">$${parseFloat(item.subtotal).toFixed(2)}</div>
                    </div>
                `).join('')}
                
                <div class="checkout-total">
                    <div class="checkout-total-row">
                        <span>Subtotal:</span>
                        <span>$${subtotal.toFixed(2)}</span>
                    </div>
                    <div class="checkout-total-row">
                        <span>Taxes (8%):</span>
                        <span>$${taxes.toFixed(2)}</span>
                    </div>
                    <div class="checkout-total-row">
                        <span>Shipping:</span>
                        <span>${shipping === 0 ? 'FREE' : '$' + shipping.toFixed(2)}</span>
                    </div>
                    <div class="checkout-total-row final">
                        <span>Total:</span>
                        <span>$${total.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="checkout-step">
            <h3>Shipping Information</h3>
            <div class="checkout-form">
                <div class="form-group">
                    <label for="fullName">Full Name</label>
                    <input type="text" id="fullName" placeholder="Enter your full name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" placeholder="Enter your email" required>
                </div>
                <div class="form-group">
                    <label for="address">Address</label>
                    <input type="text" id="address" placeholder="Enter your address" required>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label for="city">City</label>
                        <input type="text" id="city" placeholder="City" required>
                    </div>
                    <div class="form-group">
                        <label for="zipCode">ZIP Code</label>
                        <input type="text" id="zipCode" placeholder="ZIP Code" required>
                    </div>
                </div>
            </div>
        </div>

        <div class="checkout-step">
            <h3>Payment Method</h3>
            <div class="checkout-form">
                <div class="form-group">
                    <label for="paymentMethod">Payment Method</label>
                    <select id="paymentMethod" required>
                        <option value="">Select payment method</option>
                        <option value="credit_card">Credit Card</option>
                        <option value="debit_card">Debit Card</option>
                        <option value="paypal">PayPal</option>
                        <option value="apple_pay">Apple Pay</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="cardNumber">Card Number</label>
                    <input type="text" id="cardNumber" placeholder="1234 5678 9012 3456" maxlength="19">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label for="expiryDate">Expiry Date</label>
                        <input type="text" id="expiryDate" placeholder="MM/YY" maxlength="5">
                    </div>
                    <div class="form-group">
                        <label for="cvv">CVV</label>
                        <input type="text" id="cvv" placeholder="123" maxlength="4">
                    </div>
                </div>
            </div>
        </div>

        <div class="checkout-actions">
            <button class="checkout-btn-secondary" onclick="closeCheckoutModal()">Cancel</button>
            <button class="checkout-btn-primary" onclick="completeCheckout()">Place Order - $${total.toFixed(2)}</button>
        </div>
    `;

    // Show modal
    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';

    // Setup form interactions
    setupCheckoutForm();
}

// Setup checkout form interactions
function setupCheckoutForm() {
    // Format card number input
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            if (formattedValue.length > 19) formattedValue = formattedValue.substr(0, 19);
            e.target.value = formattedValue;
        });
    }

    // Format expiry date input
    const expiryInput = document.getElementById('expiryDate');
    if (expiryInput) {
        expiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }

    // CVV input validation
    const cvvInput = document.getElementById('cvv');
    if (cvvInput) {
        cvvInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    }
}

// Close checkout modal
function closeCheckoutModal() {
    const overlay = document.getElementById('checkoutModalOverlay');
    if (overlay) {
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Complete checkout process
function completeCheckout() {
    console.log('🎯 Completing checkout...');

    // Validate form
    const requiredFields = ['fullName', 'email', 'address', 'city', 'zipCode', 'paymentMethod'];
    const missingFields = [];

    for (const field of requiredFields) {
        const element = document.getElementById(field);
        if (!element || !element.value.trim()) {
            missingFields.push(field);
        }
    }

    if (missingFields.length > 0) {
        alert('Please fill in all required fields');
        return;
    }

    // Calculate final total
    const subtotal = cart.subtotal || 0;
    const taxes = subtotal * 0.08;
    const shipping = subtotal > 100 ? 0 : 9.99;
    const total = subtotal + taxes + shipping;

    // Generate order ID
    const orderId = 'ORD-' + Date.now().toString().slice(-8);

    // Show success animation
    showCheckoutSuccess(orderId, total);
}

// Show checkout success
function showCheckoutSuccess(orderId, total) {
    const content = document.getElementById('checkoutModalContent');
    
    if (!content) return;

    content.innerHTML = `
        <div class="success-animation">
            <div class="success-icon">✅</div>
            <div class="success-message">Order Placed Successfully!</div>
            <div class="success-details">
                <p>Order ID: <strong>${orderId}</strong></p>
                <p>Total: <strong>$${total.toFixed(2)}</strong></p>
                <p>You will receive a confirmation email shortly.</p>
            </div>
            <div class="checkout-actions">
                <button class="checkout-btn-primary" onclick="finishCheckout()">Continue Shopping</button>
            </div>
        </div>
    `;
}

// Finish checkout and clear cart
function finishCheckout() {
    console.log('✅ Checkout completed successfully');

    // Clear cart only after successful checkout
    cart = { items: [], total_items: 0, subtotal: 0 };
    
    // Update all displays
    updateCartDisplay();
    updateSidePanelContentAll();
    updateCartPageDisplay();
    
    // Close modal and return to products
    closeCheckoutModal();
    showProductsPage();
}

// Side panel functions
function showSidePanel() {
    console.log('📱 Showing side panel');
    const overlay = document.getElementById('sidePanelOverlay');
    const panel = document.getElementById('sidePanel');
    
    if (overlay && panel) {
        // Update content before showing
        updateSidePanelContentAll();
        
        overlay.classList.add('show');
        panel.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function closeSidePanel() {
    console.log('📱 Closing side panel');
    const overlay = document.getElementById('sidePanelOverlay');
    const panel = document.getElementById('sidePanel');
    
    if (overlay && panel) {
        overlay.classList.remove('show');
        panel.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Update side panel with all cart items
function updateSidePanelContentAll() {
    const content = document.getElementById('sidePanelContent');
    
    if (!content) return;

    if (cart.items && cart.items.length > 0) {
        content.innerHTML = cart.items.map(item => `
            <div class="added-item">
                <div class="added-item-image">${item.emoji || '📦'}</div>
                <div class="added-item-details">
                    <div class="added-item-name">${item.product_name}</div>
                    <div class="added-item-price">$${parseFloat(item.price).toFixed(2)}</div>
                    <div class="added-item-controls">
                        <div class="quantity-controls">
                            <button class="quantity-btn" onclick="updateQuantity('${item.product_id}', ${item.quantity - 1})" ${item.quantity <= 1 ? 'disabled' : ''}>−</button>
                            <span class="quantity-display">${item.quantity}</span>
                            <button class="quantity-btn" onclick="updateQuantity('${item.product_id}', ${item.quantity + 1})">+</button>
                        </div>
                        <button class="remove-item-btn" onclick="removeItem('${item.product_id}')">Remove</button>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        content.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #565959;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🛒</div>
                <p>Your cart is empty</p>
            </div>
        `;
    }

    // Update summary
    document.getElementById('summaryItemCount').textContent = cart.total_items;
    document.getElementById('summarySubtotal').textContent = cart.subtotal.toFixed(2);
    document.getElementById('summaryTotal').textContent = cart.subtotal.toFixed(2);
}

// Update quantity in cart
function updateQuantity(productId, newQuantity) {
    console.log(`🔄 Updating quantity for ${productId} to ${newQuantity}`);
    
    if (newQuantity < 1) return;

    const item = cart.items.find(item => item.product_id === productId);
    if (!item) {
        console.error('❌ Item not found in cart');
        return;
    }

    // Update item quantity and subtotal
    item.quantity = newQuantity;
    item.subtotal = (newQuantity * parseFloat(item.price)).toFixed(2);

    // Update cart totals
    cart.total_items = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    cart.subtotal = cart.items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0);

    // Update all displays
    updateCartDisplay();
    updateSidePanelContentAll();
    
    console.log('✅ Quantity updated');
}

// Remove item from cart
function removeItem(productId) {
    console.log(`🗑️ Removing item ${productId} from cart`);
    
    const item = cart.items.find(item => item.product_id === productId);
    if (!item) {
        console.error('❌ Item not found in cart');
        return;
    }

    // Remove item from cart
    cart.items = cart.items.filter(item => item.product_id !== productId);
    
    // Update cart totals
    cart.total_items = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    cart.subtotal = cart.items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0);
    
    // Update all displays
    updateCartDisplay();
    updateSidePanelContentAll();
    
    console.log('✅ Item removed');
}

// Render products
function renderProducts() {
    console.log('🎨 Rendering products...');
    const productsGrid = document.getElementById('productsGrid');
    
    if (!productsGrid) {
        console.error('❌ Products grid not found');
        return;
    }

    productsGrid.innerHTML = '';

    PRODUCTS.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        productCard.innerHTML = `
            <div class="product-image">${product.emoji}</div>
            <div class="product-name">${product.name}</div>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <div class="product-description">${product.description}</div>
            <div class="product-controls">
                <label>Qty:</label>
                <input type="number" class="quantity-input" id="qty-${product.id}" value="1" min="1" max="10">
            </div>
            <button class="add-to-cart-btn" onclick="addToCart('${product.id}')" id="btn-${product.id}">
                Add to Cart
            </button>
        `;
        productsGrid.appendChild(productCard);
    });
    
    console.log('✅ Products rendered');
}

// Add to cart function
function addToCart(productId) {
    console.log(`🛒 Adding product ${productId} to cart`);
    
    const product = PRODUCTS.find(p => p.id === productId);
    const quantityInput = document.getElementById(`qty-${productId}`);
    const quantity = parseInt(quantityInput.value);

    if (!product) {
        console.error('❌ Product not found');
        return;
    }

    // Check if item already exists in cart
    const existingItem = cart.items.find(item => item.product_id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
        existingItem.subtotal = (existingItem.quantity * parseFloat(existingItem.price)).toFixed(2);
    } else {
        cart.items.push({
            product_id: productId,
            product_name: product.name,
            price: product.price.toFixed(2),
            quantity: quantity,
            subtotal: (quantity * product.price).toFixed(2),
            emoji: product.emoji
        });
    }

    // Update cart totals
    cart.total_items = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    cart.subtotal = cart.items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0);

    updateCartDisplay();
    updateSidePanelContent(product, quantity);
    showSidePanel();
    
    console.log('✅ Item added to cart', cart);
}

// Update side panel content - Show all cart items
function updateSidePanelContent(addedProduct, addedQuantity) {
    const content = document.getElementById('sidePanelContent');
    
    if (!content) return;

    // Show all items in cart, not just the recently added one
    if (cart.items && cart.items.length > 0) {
        content.innerHTML = cart.items.map(item => `
            <div class="added-item">
                <div class="added-item-image">${item.emoji || '📦'}</div>
                <div class="added-item-details">
                    <div class="added-item-name">${item.product_name}</div>
                    <div class="added-item-price">$${parseFloat(item.price).toFixed(2)}</div>
                    <div class="added-item-quantity">Quantity: ${item.quantity}</div>
                </div>
            </div>
        `).join('');
    } else {
        content.innerHTML = `
            <div class="added-item">
                <div class="added-item-image">${addedProduct.emoji}</div>
                <div class="added-item-details">
                    <div class="added-item-name">${addedProduct.name}</div>
                    <div class="added-item-price">$${addedProduct.price.toFixed(2)}</div>
                    <div class="added-item-quantity">Quantity: ${addedQuantity}</div>
                </div>
            </div>
        `;
    }

    // Update summary
    document.getElementById('summaryItemCount').textContent = cart.total_items;
    document.getElementById('summarySubtotal').textContent = cart.subtotal.toFixed(2);
    document.getElementById('summaryTotal').textContent = cart.subtotal.toFixed(2);
}

// Update cart display
function updateCartDisplay() {
    const cartItemCount = cart.total_items || 0;
    const cartSubtotal = cart.subtotal || 0;
    
    // Update header - badge always shows, even 0
    document.getElementById('cartBadge').textContent = cartItemCount;
    document.getElementById('cartTotal').textContent = cartSubtotal.toFixed(2);
    
    console.log('🔄 Cart display updated');
}

// Logo click handler for home navigation
function goToHome(event) {
    event.preventDefault();
    console.log('🏠 Logo clicked - navigating to home');
    
    // Close any open modals or panels
    closeSidePanel();
    closeCheckoutModal();
    
    // Show products page (home)
    showProductsPage();
    
    // Scroll to top smoothly
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    
    // Add visual feedback
    const logoIcon = document.querySelector('.logo-icon');
    if (logoIcon) {
        logoIcon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            logoIcon.style.transform = '';
        }, 200);
    }
}

console.log('✅ Shopping Cart Script Loaded');
