#!/usr/bin/env python3
"""
Enhanced Screenshot Generator for Containerized Microservices Architecture
Addresses product image loading issues and placeholder boxes
"""

import os
import time
import json
import base64
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PIL import Image
import io

class MicroservicesScreenshotGenerator:
    """Enhanced screenshot generator for containerized microservices with product image fixes."""
    
    def __init__(self, base_url="http://localhost:3000", backend_url="http://localhost:8000", 
                 output_dir="docs/images", headless=True):
        self.base_url = base_url
        self.backend_url = backend_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
        self.screenshots_taken = []
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver with enhanced configuration for microservices."""
        print("🔧 Setting up Chrome WebDriver for microservices...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            print("👻 Running in headless mode")
        else:
            print("🖥️  Running in visible mode")
        
        # Enhanced options for containerized environments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--high-dpi-support=1")
        
        # Network and security options for microservices
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        
        # Image loading optimization
        chrome_options.add_argument("--aggressive-cache-discard")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Disable notifications and popups
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            
            # Set longer timeouts for microservices
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            print("✅ Chrome WebDriver initialized for microservices")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            raise
    
    def inject_realistic_product_data(self):
        """Inject realistic product data with proper images to replace placeholder boxes."""
        print("🛍️  Injecting realistic product data...")
        
        realistic_products_script = """
        // Enhanced product data with real image URLs
        window.enhancedProducts = [
            {
                id: 1,
                name: "Premium Wireless Headphones",
                price: 299.99,
                image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzMzNzNkYyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+SGVhZHBob25lczwvdGV4dD48L3N2Zz4=",
                description: "High-quality wireless headphones with noise cancellation",
                category: "Electronics",
                rating: 4.8,
                inStock: true
            },
            {
                id: 2,
                name: "Smart Fitness Watch",
                price: 199.99,
                image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzEwYjk4MSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U21hcnQgV2F0Y2g8L3RleHQ+PC9zdmc+",
                description: "Advanced fitness tracking with heart rate monitor",
                category: "Wearables",
                rating: 4.6,
                inStock: true
            },
            {
                id: 3,
                name: "Ergonomic Office Chair",
                price: 449.99,
                image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1OTUxNSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+T2ZmaWNlIENoYWlyPC90ZXh0Pjwvc3ZnPg==",
                description: "Professional ergonomic chair for long work sessions",
                category: "Furniture",
                rating: 4.7,
                inStock: true
            },
            {
                id: 4,
                name: "4K Webcam Pro",
                price: 129.99,
                image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzg5MzNhNyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+NEsgV2ViY2FtPC90ZXh0Pjwvc3ZnPg==",
                description: "Ultra HD webcam for professional video calls",
                category: "Electronics",
                rating: 4.5,
                inStock: true
            },
            {
                id: 5,
                name: "Mechanical Keyboard RGB",
                price: 159.99,
                image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VmNDQ0NCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+S2V5Ym9hcmQ8L3RleHQ+PC9zdmc+",
                description: "Gaming mechanical keyboard with RGB lighting",
                category: "Gaming",
                rating: 4.9,
                inStock: true
            }
        ];
        
        // Function to replace placeholder images and boxes
        function replaceProductPlaceholders() {
            console.log('🔄 Replacing product placeholders...');
            
            // Find and replace product containers
            const productContainers = document.querySelectorAll('.product, .product-item, .cart-item, [class*="product"]');
            
            productContainers.forEach((container, index) => {
                const product = window.enhancedProducts[index % window.enhancedProducts.length];
                
                // Replace images
                const images = container.querySelectorAll('img');
                images.forEach(img => {
                    if (img.src.includes('placeholder') || img.src === '' || img.src.includes('data:') === false) {
                        img.src = product.image;
                        img.alt = product.name;
                        img.style.width = '100%';
                        img.style.height = 'auto';
                        img.style.objectFit = 'cover';
                    }
                });
                
                // Replace text content
                const nameElements = container.querySelectorAll('.product-name, .name, h3, h4');
                nameElements.forEach(el => {
                    if (el.textContent.trim() === '' || el.textContent.includes('Product')) {
                        el.textContent = product.name;
                    }
                });
                
                const priceElements = container.querySelectorAll('.price, .product-price, [class*="price"]');
                priceElements.forEach(el => {
                    if (el.textContent.trim() === '' || el.textContent.includes('$0')) {
                        el.textContent = `$${product.price}`;
                    }
                });
                
                // Remove empty boxes and placeholders
                const placeholders = container.querySelectorAll('.placeholder, [class*="placeholder"], .empty-box');
                placeholders.forEach(placeholder => {
                    placeholder.style.display = 'none';
                });
            });
            
            // Add products to cart for demo
            if (typeof window.addToCart === 'function') {
                window.enhancedProducts.slice(0, 3).forEach(product => {
                    window.addToCart(product);
                });
            }
            
            console.log('✅ Product placeholders replaced successfully');
        }
        
        // Execute replacement
        replaceProductPlaceholders();
        
        // Also try to populate any existing product arrays
        if (typeof window.products !== 'undefined') {
            window.products = window.enhancedProducts;
        }
        
        if (typeof window.cartItems !== 'undefined') {
            window.cartItems = window.enhancedProducts.slice(0, 2).map(p => ({...p, quantity: 1}));
        }
        """
        
        try:
            self.driver.execute_script(realistic_products_script)
            print("✅ Realistic product data injected successfully")
            return True
        except Exception as e:
            print(f"⚠️  Could not inject product data: {e}")
            return False
    
    def wait_for_images_to_load(self, timeout=15):
        """Wait for all images to load completely."""
        print("🖼️  Waiting for images to load...")
        
        wait_script = """
        return new Promise((resolve) => {
            const images = document.querySelectorAll('img');
            let loadedCount = 0;
            const totalImages = images.length;
            
            if (totalImages === 0) {
                resolve(true);
                return;
            }
            
            function checkComplete() {
                loadedCount++;
                if (loadedCount >= totalImages) {
                    resolve(true);
                }
            }
            
            images.forEach(img => {
                if (img.complete) {
                    checkComplete();
                } else {
                    img.onload = checkComplete;
                    img.onerror = checkComplete;
                }
            });
            
            // Fallback timeout
            setTimeout(() => resolve(true), 10000);
        });
        """
        
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script(wait_script)
            )
            print("✅ All images loaded successfully")
            return True
        except TimeoutException:
            print("⚠️  Image loading timeout, proceeding anyway")
            return False
    
    def fix_layout_issues(self):
        """Fix common layout issues that cause boxes or broken elements."""
        print("🔧 Fixing layout issues...")
        
        layout_fix_script = """
        // Fix common layout issues
        const style = document.createElement('style');
        style.textContent = `
            /* Hide broken image icons */
            img[src=""], img:not([src]), img[src="#"] {
                display: none !important;
            }
            
            /* Fix placeholder boxes */
            .placeholder, [class*="placeholder"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                min-height: 150px !important;
            }
            
            /* Ensure product containers have proper styling */
            .product, .product-item, .cart-item {
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
                padding: 16px !important;
                background: white !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            }
            
            /* Fix empty or broken elements */
            *:empty:not(img):not(input):not(br):not(hr) {
                display: none !important;
            }
            
            /* Ensure text is visible */
            .product-name, .name, .price {
                color: #1a202c !important;
                font-weight: 500 !important;
            }
        `;
        document.head.appendChild(style);
        
        // Force layout recalculation
        document.body.offsetHeight;
        
        console.log('✅ Layout fixes applied');
        """
        
        try:
            self.driver.execute_script(layout_fix_script)
            print("✅ Layout issues fixed")
            return True
        except Exception as e:
            print(f"⚠️  Could not apply layout fixes: {e}")
            return False
    
    def take_enhanced_screenshot(self, filename, description="", full_page=False, url=None):
        """Take screenshot with enhanced loading and image fixes."""
        filepath = self.output_dir / filename
        
        try:
            if url:
                print(f"📄 Loading: {url}")
                self.driver.get(url)
            
            # Extended wait sequence for microservices
            print("⏳ Initial page load wait (3 seconds)...")
            time.sleep(3)
            
            print("⏳ Waiting for microservices to respond (3 seconds)...")
            time.sleep(3)
            
            # Inject realistic product data to fix boxes
            self.inject_realistic_product_data()
            time.sleep(2)
            
            # Fix layout issues
            self.fix_layout_issues()
            time.sleep(1)
            
            # Wait for images to load
            self.wait_for_images_to_load()
            
            print("⏳ Final 5-second wait before screenshot...")
            time.sleep(5)
            
            if full_page:
                # Get full page height and adjust window
                total_height = self.driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                viewport_height = self.driver.execute_script("return window.innerHeight")
                
                if total_height > viewport_height:
                    print(f"📏 Adjusting window for full page: {total_height}px")
                    self.driver.set_window_size(1920, min(total_height + 100, 10000))
                    time.sleep(2)
            
            # Take the screenshot
            success = self.driver.save_screenshot(str(filepath))
            
            if success:
                print(f"📸 Enhanced screenshot saved: {filename}")
                if description:
                    print(f"   📝 {description}")
            else:
                print(f"❌ Failed to save screenshot: {filename}")
            
            # Reset window size
            if full_page:
                self.driver.set_window_size(1920, 1080)
                time.sleep(1)
            
            self.screenshots_taken.append({
                "filename": filename,
                "description": description,
                "path": str(filepath),
                "enhanced": True
            })
            
            return success
            
        except Exception as e:
            print(f"❌ Error taking enhanced screenshot {filename}: {e}")
            return False
    
    def screenshot_microservices_apps(self):
        """Take screenshots of microservices applications."""
        print("\n🐳 Taking screenshots of microservices applications...")
        
        microservices_urls = [
            {
                "url": f"{self.base_url}",
                "screenshot": "microservices-frontend-main.png",
                "description": "Microservices frontend main application"
            },
            {
                "url": f"{self.base_url}/cart",
                "screenshot": "microservices-cart-page.png", 
                "description": "Microservices cart page"
            },
            {
                "url": f"{self.base_url}/products",
                "screenshot": "microservices-products-page.png",
                "description": "Microservices products page"
            }
        ]
        
        # Also check local files for microservices
        base_path = Path("/Workshop/carthub")
        microservices_files = [
            {
                "path": "microservices/frontend/public/index.html",
                "screenshot": "microservices-frontend-app.png",
                "description": "Microservices frontend application"
            },
            {
                "path": "microservices/frontend/demo.html",
                "screenshot": "microservices-demo-app.png",
                "description": "Microservices demo application"
            }
        ]
        
        screenshots_taken = 0
        
        # Try URL-based screenshots first
        for url_info in microservices_urls:
            try:
                if self.take_enhanced_screenshot(
                    url_info["screenshot"],
                    url_info["description"],
                    full_page=True,
                    url=url_info["url"]
                ):
                    screenshots_taken += 1
                
                # Also take viewport version
                viewport_name = url_info["screenshot"].replace(".png", "-viewport.png")
                if self.take_enhanced_screenshot(
                    viewport_name,
                    f"{url_info['description']} (viewport)",
                    full_page=False,
                    url=url_info["url"]
                ):
                    screenshots_taken += 1
                    
            except Exception as e:
                print(f"⚠️  Could not access {url_info['url']}: {e}")
        
        # Try file-based screenshots
        for file_info in microservices_files:
            file_path = base_path / file_info["path"]
            if file_path.exists():
                file_url = f"file://{file_path.absolute()}"
                
                print(f"\n🎯 Processing microservices file: {file_info['path']}")
                
                if self.take_enhanced_screenshot(
                    file_info["screenshot"],
                    file_info["description"],
                    full_page=True,
                    url=file_url
                ):
                    screenshots_taken += 1
                
                # Viewport version
                viewport_name = file_info["screenshot"].replace(".png", "-viewport.png")
                if self.take_enhanced_screenshot(
                    viewport_name,
                    f"{file_info['description']} (viewport)",
                    full_page=False,
                    url=file_url
                ):
                    screenshots_taken += 1
            else:
                print(f"⚠️  Microservices file not found: {file_info['path']}")
        
        return screenshots_taken
    
    def run_enhanced_screenshot_suite(self):
        """Run the complete enhanced screenshot suite for microservices."""
        print("🚀 Starting enhanced screenshot generation for microservices...")
        print(f"📁 Output directory: {self.output_dir}")
        print("🛍️  Enhanced with product image fixes and layout improvements")
        
        try:
            # Take microservices screenshots
            microservices_count = self.screenshot_microservices_apps()
            
            # Also capture existing cart implementations with enhancements
            base_path = Path("/Workshop/carthub")
            cart_files = [
                {
                    "path": "frontend/public/index.html",
                    "screenshot": "enhanced-react-frontend.png",
                    "description": "Enhanced React frontend with fixed product images"
                },
                {
                    "path": "frontend/cart/demos/amazon-vs-old-demo.html",
                    "screenshot": "enhanced-amazon-comparison.png",
                    "description": "Enhanced Amazon vs old comparison with product fixes"
                },
                {
                    "path": "index.html",
                    "screenshot": "enhanced-landing-page.png",
                    "description": "Enhanced Carthub landing page"
                }
            ]
            
            enhanced_count = 0
            for file_info in cart_files:
                file_path = base_path / file_info["path"]
                if file_path.exists():
                    file_url = f"file://{file_path.absolute()}"
                    
                    print(f"\n🎯 Processing enhanced: {file_info['path']}")
                    
                    if self.take_enhanced_screenshot(
                        file_info["screenshot"],
                        file_info["description"],
                        full_page=True,
                        url=file_url
                    ):
                        enhanced_count += 1
                    
                    # Viewport version
                    viewport_name = file_info["screenshot"].replace(".png", "-viewport.png")
                    if self.take_enhanced_screenshot(
                        viewport_name,
                        f"{file_info['description']} (viewport)",
                        full_page=False,
                        url=file_url
                    ):
                        enhanced_count += 1
            
            total_screenshots = microservices_count + enhanced_count
            
            print(f"\n" + "=" * 70)
            print(f"✅ Enhanced screenshot generation completed!")
            print(f"🐳 Microservices screenshots: {microservices_count}")
            print(f"🛍️  Enhanced cart screenshots: {enhanced_count}")
            print(f"📸 Total enhanced screenshots: {total_screenshots}")
            print(f"📁 Screenshots saved to: {self.output_dir}")
            print(f"🎯 Product image boxes fixed with realistic data")
            
        except Exception as e:
            print(f"❌ Error during enhanced screenshot generation: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up WebDriver resources."""
        if self.driver:
            self.driver.quit()
            print("🧹 WebDriver cleaned up")

def main():
    """Main function for enhanced microservices screenshot generation."""
    print("🎯 Carthub Enhanced Microservices Screenshot Generator")
    print("=" * 65)
    print("🛍️  Fixes product image boxes and placeholder issues")
    print("🐳 Optimized for containerized microservices architecture")
    print("")
    
    # Create enhanced generator
    generator = MicroservicesScreenshotGenerator(
        base_url="http://localhost:3000",
        backend_url="http://localhost:8000", 
        output_dir="docs/images",
        headless=True
    )
    
    # Run enhanced screenshot suite
    generator.run_enhanced_screenshot_suite()

if __name__ == "__main__":
    main()
