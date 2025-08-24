#!/usr/bin/env python3
"""
Comprehensive Screenshot Generator for Carthub Documentation
Includes 5-second wait for proper page loading as requested
Captures all available frontend implementations
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

def take_screenshot_with_extended_wait(driver, url, filename, description="", full_page=True):
    """Take screenshot with extended wait times for proper page loading."""
    output_dir = Path("docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    
    try:
        print(f"📄 Loading: {url}")
        driver.get(url)
        
        # Extended wait sequence for complete page loading
        print("⏳ Initial page load wait (3 seconds)...")
        time.sleep(3)
        
        print("⏳ Waiting for JavaScript and CSS (2 seconds)...")
        time.sleep(2)
        
        print("⏳ Final 5-second wait before screenshot (as requested)...")
        time.sleep(5)
        
        # Try to inject demo data if possible
        try:
            demo_script = """
            if (typeof window.addDemoProducts === 'function') {
                window.addDemoProducts();
            }
            if (typeof window.addDemoCartItems === 'function') {
                window.addDemoCartItems();
            }
            """
            driver.execute_script(demo_script)
            print("✨ Demo data injected")
            time.sleep(1)  # Wait after demo data injection
        except:
            pass
        
        if full_page:
            # Get full page height and adjust window
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            if total_height > viewport_height:
                print(f"📏 Adjusting window for full page: {total_height}px")
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
    """Main function to generate all screenshots with improved wait times."""
    print("🎯 Carthub Comprehensive Screenshot Generator (Improved)")
    print("=" * 60)
    print("⏳ Now includes 5-second wait for proper page loading")
    print("")
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        base_path = Path("/Workshop/carthub")
        
        # Define all available files to screenshot
        html_files = [
            # Main application files
            {
                "path": "index.html",
                "screenshot": "carthub-landing-page.png",
                "description": "Carthub main landing page"
            },
            {
                "path": "frontend/public/index.html",
                "screenshot": "react-frontend-app.png",
                "description": "React frontend application"
            },
            {
                "path": "frontend/demo.html",
                "screenshot": "frontend-demo.png",
                "description": "Frontend demo application"
            },
            
            # Cart implementations
            {
                "path": "frontend/cart/demos/amazon-vs-old-demo.html",
                "screenshot": "amazon-vs-old-comparison.png",
                "description": "Comparison between Amazon-style and old cart designs"
            },
            
            # Testing interfaces
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
            
            # Check for other cart files
            {
                "path": "frontend/cart/main/index.html",
                "screenshot": "cart-main-interface.png",
                "description": "Main cart interface"
            },
            {
                "path": "frontend/cart/enhanced/index.html",
                "screenshot": "enhanced-cart-interface.png",
                "description": "Enhanced cart interface"
            }
        ]
        
        screenshots_taken = 0
        
        for file_info in html_files:
            file_path = base_path / file_info["path"]
            if file_path.exists():
                file_url = f"file://{file_path.absolute()}"
                
                print(f"\n🎯 Processing: {file_info['path']}")
                
                # Take full page screenshot
                if take_screenshot_with_extended_wait(
                    driver, 
                    file_url, 
                    file_info["screenshot"], 
                    file_info["description"], 
                    full_page=True
                ):
                    screenshots_taken += 1
                
                # Take viewport screenshot
                viewport_name = file_info["screenshot"].replace(".png", "-viewport.png")
                if take_screenshot_with_extended_wait(
                    driver, 
                    file_url, 
                    viewport_name, 
                    f"{file_info['description']} (viewport)", 
                    full_page=False
                ):
                    screenshots_taken += 1
                    
            else:
                print(f"⚠️  File not found: {file_info['path']}")
        
        # Check for additional files in cart directory
        cart_dir = base_path / "frontend/cart"
        if cart_dir.exists():
            print(f"\n🔍 Scanning cart directory for additional files...")
            for html_file in cart_dir.rglob("*.html"):
                if html_file.name not in [f["path"].split("/")[-1] for f in html_files]:
                    rel_path = html_file.relative_to(base_path)
                    file_url = f"file://{html_file.absolute()}"
                    screenshot_name = f"cart-{html_file.stem}.png"
                    
                    print(f"\n🆕 Found additional file: {rel_path}")
                    
                    if take_screenshot_with_extended_wait(
                        driver, 
                        file_url, 
                        screenshot_name, 
                        f"Cart implementation: {html_file.stem}", 
                        full_page=True
                    ):
                        screenshots_taken += 1
        
        print(f"\n" + "=" * 60)
        print(f"✅ Screenshot generation completed with improved loading times!")
        print(f"📸 Total screenshots taken: {screenshots_taken}")
        print(f"📁 Screenshots saved to: docs/images/")
        print(f"⏳ All screenshots included 5-second wait for proper loading")
        
    except Exception as e:
        print(f"❌ Error during screenshot generation: {e}")
    finally:
        driver.quit()
        print("🧹 WebDriver cleaned up")

if __name__ == "__main__":
    main()
