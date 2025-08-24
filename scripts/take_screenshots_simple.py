#!/usr/bin/env python3
"""
Simple Automated Screenshot Generator for Carthub Documentation
Includes 5-second wait for proper page loading
"""

import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Setup Chrome WebDriver with proper configuration."""
    print("🔧 Setting up Chrome WebDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--high-dpi-support=1")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(1920, 1080)
        print("✅ Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize Chrome WebDriver: {e}")
        return None

def take_screenshot_with_wait(driver, url, filename, description="", full_page=True):
    """Take screenshot with proper wait times for page loading."""
    output_dir = Path("docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    
    try:
        print(f"📄 Loading: {url}")
        driver.get(url)
        
        # Wait for initial page load
        print("⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Additional wait for JavaScript and CSS
        print("⏳ Waiting for resources to load...")
        time.sleep(2)
        
        # Final wait before screenshot (as requested)
        print("⏳ Final 5-second wait before screenshot...")
        time.sleep(5)
        
        if full_page:
            # Get full page height and adjust window
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            if total_height > viewport_height:
                driver.set_window_size(1920, total_height + 100)
                time.sleep(2)  # Wait after resizing
        
        # Take the screenshot
        success = driver.save_screenshot(str(filepath))
        
        if success:
            print(f"📸 Screenshot saved: {filename}")
            if description:
                print(f"   📝 {description}")
        else:
            print(f"❌ Failed to save screenshot: {filename}")
        
        # Reset window size if needed
        if full_page:
            driver.set_window_size(1920, 1080)
            time.sleep(1)
        
        return success
        
    except Exception as e:
        print(f"❌ Error taking screenshot {filename}: {e}")
        return False

def main():
    """Main function to generate all screenshots."""
    print("🎯 Carthub Simple Screenshot Generator")
    print("=" * 50)
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        base_path = Path("/Workshop/carthub")
        
        # Define files to screenshot
        html_files = [
            {
                "path": "frontend/cart/main/shopping-cart-amazon-style.html",
                "screenshot": "amazon-style-cart-main.png",
                "description": "Amazon-style shopping cart main interface"
            },
            {
                "path": "frontend/cart/demos/amazon-vs-old-demo.html", 
                "screenshot": "amazon-vs-old-comparison.png",
                "description": "Comparison between Amazon-style and old cart designs"
            },
            {
                "path": "frontend/cart/tests/test-checkout-modal.html",
                "screenshot": "checkout-modal-interface.png", 
                "description": "Checkout modal testing interface"
            },
            {
                "path": "frontend/cart/tests/test-cart-functionality.html",
                "screenshot": "cart-functionality-test.png",
                "description": "Cart functionality testing interface"
            },
            {
                "path": "enhanced-shopping-cart.html",
                "screenshot": "enhanced-shopping-cart.png",
                "description": "Enhanced shopping cart implementation"
            },
            {
                "path": "index.html",
                "screenshot": "carthub-landing-page.png",
                "description": "Carthub main landing page"
            }
        ]
        
        screenshots_taken = 0
        
        for file_info in html_files:
            file_path = base_path / file_info["path"]
            if file_path.exists():
                file_url = f"file://{file_path.absolute()}"
                
                # Take full page screenshot
                if take_screenshot_with_wait(
                    driver, 
                    file_url, 
                    file_info["screenshot"], 
                    file_info["description"], 
                    full_page=True
                ):
                    screenshots_taken += 1
                
                # Take viewport screenshot
                viewport_name = file_info["screenshot"].replace(".png", "-viewport.png")
                if take_screenshot_with_wait(
                    driver, 
                    file_url, 
                    viewport_name, 
                    f"{file_info['description']} (viewport)", 
                    full_page=False
                ):
                    screenshots_taken += 1
                    
            else:
                print(f"⚠️  File not found: {file_info['path']}")
        
        print(f"\n✅ Screenshot generation completed!")
        print(f"📸 Total screenshots taken: {screenshots_taken}")
        print(f"📁 Screenshots saved to: docs/images/")
        
    except Exception as e:
        print(f"❌ Error during screenshot generation: {e}")
    finally:
        driver.quit()
        print("🧹 WebDriver cleaned up")

if __name__ == "__main__":
    main()
