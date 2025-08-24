#!/usr/bin/env python3
"""
Automated Screenshot Generator for Carthub Documentation
Uses Selenium WebDriver to capture screenshots of all major features
"""

import os
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import argparse


class CarthubScreenshotGenerator:
    """Automated screenshot generator for Carthub application."""
    
    def __init__(self, base_url="http://localhost:3000", output_dir="docs/images", headless=True):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimal settings for screenshots."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Optimize for screenshots
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--high-dpi-support=1")
        
        # Disable notifications and popups
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            print("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("💡 Make sure ChromeDriver is installed and in PATH")
            raise
    
    def wait_for_element(self, selector, timeout=10, by=By.CSS_SELECTOR):
        """Wait for element to be present and visible."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            print(f"⚠️  Element not found: {selector}")
            return None
    
    def take_screenshot(self, filename, full_page=False):
        """Take screenshot and save to output directory."""
        filepath = self.output_dir / filename
        
        if full_page:
            # Get full page height
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.set_window_size(1920, total_height)
            time.sleep(1)
        
        success = self.driver.save_screenshot(str(filepath))
        
        if success:
            print(f"📸 Screenshot saved: {filepath}")
        else:
            print(f"❌ Failed to save screenshot: {filepath}")
        
        # Reset window size
        if full_page:
            self.driver.set_window_size(1920, 1080)
        
        return success
    
    def screenshot_homepage(self):
        """Take screenshot of the homepage."""
        print("\n📸 Taking homepage screenshots...")
        
        # Navigate to homepage
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Wait for page to load
        self.wait_for_element("body")
        
        # Take full page screenshot
        self.take_screenshot("homepage-first-visit.png", full_page=True)
        
        # Take viewport screenshot
        self.take_screenshot("homepage-viewport.png")
    
    def screenshot_product_catalog(self):
        """Take screenshots of product catalog."""
        print("\n📸 Taking product catalog screenshots...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Wait for products to load
        products = self.wait_for_element(".product-grid, .products, [data-testid='product-list']")
        if products:
            self.take_screenshot("product-catalog.png")
            
            # Take screenshot of individual product card
            product_card = self.wait_for_element(".product-card, .product-item, [data-testid='product-card']")
            if product_card:
                # Scroll to product card
                self.driver.execute_script("arguments[0].scrollIntoView(true);", product_card)
                time.sleep(1)
                self.take_screenshot("product-card-detail.png")
    
    def screenshot_cart_functionality(self):
        """Take screenshots of cart functionality."""
        print("\n📸 Taking cart functionality screenshots...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Add item to cart
        add_button = self.wait_for_element("button[data-testid='add-to-cart'], .add-to-cart, button:contains('Add to Cart')")
        if add_button:
            add_button.click()
            time.sleep(1)
            self.take_screenshot("add-to-cart-success.png")
        
        # Cart icon hover (mini-cart)
        cart_icon = self.wait_for_element(".cart-icon, [data-testid='cart-icon'], .header-cart")
        if cart_icon:
            # Hover over cart icon
            ActionChains(self.driver).move_to_element(cart_icon).perform()
            time.sleep(1)
            self.take_screenshot("mini-cart-preview.png")
            
            # Click to open full cart
            cart_icon.click()
            time.sleep(2)
            self.take_screenshot("full-cart-page.png")
    
    def screenshot_checkout_process(self):
        """Take screenshots of checkout process."""
        print("\n📸 Taking checkout process screenshots...")
        
        # Ensure we have items in cart first
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Add item to cart
        add_button = self.wait_for_element("button[data-testid='add-to-cart'], .add-to-cart")
        if add_button:
            add_button.click()
            time.sleep(1)
        
        # Navigate to checkout
        checkout_button = self.wait_for_element("button[data-testid='checkout'], .checkout-btn, button:contains('Checkout')")
        if checkout_button:
            checkout_button.click()
            time.sleep(2)
            self.take_screenshot("checkout-workflow.png")
            
            # Fill out checkout form (if present)
            name_field = self.wait_for_element("input[name='name'], #customer-name, [data-testid='customer-name']")
            if name_field:
                name_field.send_keys("John Doe")
                
                email_field = self.wait_for_element("input[name='email'], #customer-email, [data-testid='customer-email']")
                if email_field:
                    email_field.send_keys("john.doe@example.com")
                
                time.sleep(1)
                self.take_screenshot("checkout-form-filled.png")
    
    def screenshot_mobile_responsive(self):
        """Take screenshots of mobile responsive design."""
        print("\n📸 Taking mobile responsive screenshots...")
        
        # Set mobile viewport
        self.driver.set_window_size(375, 812)  # iPhone X size
        time.sleep(1)
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        self.take_screenshot("mobile-homepage.png")
        
        # Mobile cart
        cart_icon = self.wait_for_element(".cart-icon, [data-testid='cart-icon']")
        if cart_icon:
            cart_icon.click()
            time.sleep(2)
            self.take_screenshot("mobile-cart.png")
        
        # Reset to desktop size
        self.driver.set_window_size(1920, 1080)
    
    def screenshot_api_documentation(self, api_url="http://localhost:8000"):
        """Take screenshots of API documentation."""
        print("\n📸 Taking API documentation screenshots...")
        
        try:
            # Swagger UI
            self.driver.get(f"{api_url}/docs")
            time.sleep(3)
            
            # Wait for Swagger UI to load
            swagger_ui = self.wait_for_element(".swagger-ui, #swagger-ui")
            if swagger_ui:
                self.take_screenshot("api-swagger-ui.png", full_page=True)
            
            # ReDoc
            self.driver.get(f"{api_url}/redoc")
            time.sleep(3)
            
            redoc = self.wait_for_element("[data-testid='api-docs'], .redoc-container")
            if redoc:
                self.take_screenshot("api-redoc.png", full_page=True)
                
        except Exception as e:
            print(f"⚠️  Could not access API documentation: {e}")
            print("💡 Make sure the backend server is running on {api_url}")
    
    def screenshot_static_html_files(self):
        """Take screenshots of static HTML files."""
        print("\n📸 Taking static HTML file screenshots...")
        
        html_files = [
            ("frontend/cart/main/shopping-cart-amazon-style.html", "amazon-style-cart.png"),
            ("frontend/cart/demos/amazon-vs-old-demo.html", "amazon-vs-old-demo.png"),
            ("frontend/cart/tests/test-checkout-modal.html", "checkout-modal-test.png"),
            ("frontend/cart/tests/test-cart-functionality.html", "cart-functionality-test.png"),
        ]
        
        base_path = Path("/Workshop/carthub")
        
        for html_file, screenshot_name in html_files:
            file_path = base_path / html_file
            if file_path.exists():
                file_url = f"file://{file_path.absolute()}"
                self.driver.get(file_url)
                time.sleep(3)
                
                # Wait for page to load
                self.wait_for_element("body")
                self.take_screenshot(screenshot_name, full_page=True)
            else:
                print(f"⚠️  HTML file not found: {html_file}")
    
    def generate_all_screenshots(self, include_api=True):
        """Generate all screenshots for documentation."""
        print("🚀 Starting automated screenshot generation...")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🌐 Base URL: {self.base_url}")
        
        try:
            # Static HTML files (always available)
            self.screenshot_static_html_files()
            
            # Try to access the main application
            try:
                self.driver.get(self.base_url)
                time.sleep(2)
                
                # Check if application is accessible
                if "This site can't be reached" in self.driver.page_source:
                    print(f"⚠️  Application not accessible at {self.base_url}")
                    print("💡 Make sure the frontend server is running")
                else:
                    # Take application screenshots
                    self.screenshot_homepage()
                    self.screenshot_product_catalog()
                    self.screenshot_cart_functionality()
                    self.screenshot_checkout_process()
                    self.screenshot_mobile_responsive()
                    
            except Exception as e:
                print(f"⚠️  Could not access main application: {e}")
            
            # API documentation (if requested)
            if include_api:
                self.screenshot_api_documentation()
            
            print("\n✅ Screenshot generation completed!")
            print(f"📸 Screenshots saved to: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ Error during screenshot generation: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up WebDriver resources."""
        if self.driver:
            self.driver.quit()
            print("🧹 WebDriver cleaned up")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Generate screenshots for Carthub documentation")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL of the application")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API documentation URL")
    parser.add_argument("--output", default="docs/images", help="Output directory for screenshots")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in visible mode")
    parser.add_argument("--no-api", action="store_true", help="Skip API documentation screenshots")
    
    args = parser.parse_args()
    
    # Create screenshot generator
    generator = CarthubScreenshotGenerator(
        base_url=args.url,
        output_dir=args.output,
        headless=not args.no_headless
    )
    
    # Generate all screenshots
    generator.generate_all_screenshots(include_api=not args.no_api)


if __name__ == "__main__":
    main()
