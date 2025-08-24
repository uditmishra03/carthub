#!/usr/bin/env python3
"""
Enhanced Automated Screenshot Generator for Carthub Documentation
Uses webdriver-manager for automatic ChromeDriver management
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import sys


class EnhancedCarthubScreenshotGenerator:
    """Enhanced automated screenshot generator with better driver management."""
    
    def __init__(self, base_url="http://localhost:3000", output_dir="docs/images", headless=True):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
        self.screenshots_taken = []
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver with automatic driver management."""
        print("🔧 Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            print("👻 Running in headless mode")
        else:
            print("🖥️  Running in visible mode")
        
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
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        try:
            # Use webdriver-manager to automatically manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            print("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("💡 Trying alternative setup...")
            
            try:
                # Fallback: try without service
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.set_window_size(1920, 1080)
                print("✅ Chrome WebDriver initialized with fallback method")
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                print("💡 Please ensure Chrome is installed and try running setup script")
                sys.exit(1)
    
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
    
    def take_screenshot(self, filename, description="", full_page=False, element_selector=None):
        """Take screenshot and save to output directory."""
        filepath = self.output_dir / filename
        
        try:
            # Wait 5 seconds for page to fully load before taking screenshot
            print(f"⏳ Waiting 5 seconds for page to fully load...")
            time.sleep(5)
            
            if element_selector:
                # Screenshot specific element
                element = self.wait_for_element(element_selector, timeout=5)
                if element:
                    element.screenshot(str(filepath))
                else:
                    print(f"⚠️  Element not found for screenshot: {element_selector}")
                    return False
            else:
                if full_page:
                    # Get full page height
                    total_height = self.driver.execute_script("return document.body.scrollHeight")
                    viewport_height = self.driver.execute_script("return window.innerHeight")
                    
                    if total_height > viewport_height:
                        self.driver.set_window_size(1920, total_height + 100)
                        time.sleep(2)  # Additional wait after resizing
                
                success = self.driver.save_screenshot(str(filepath))
                
                if not success:
                    print(f"❌ Failed to save screenshot: {filepath}")
                    return False
                
                # Reset window size
                if full_page:
                    self.driver.set_window_size(1920, 1080)
                    time.sleep(1)  # Wait after resizing back
            
            print(f"📸 Screenshot saved: {filename}")
            if description:
                print(f"   📝 {description}")
            
            self.screenshots_taken.append({
                "filename": filename,
                "description": description,
                "path": str(filepath)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error taking screenshot {filename}: {e}")
            return False
    
    def inject_demo_data(self):
        """Inject demo data into the page for better screenshots."""
        demo_script = """
        // Add demo products if not present
        if (typeof window.addDemoProducts === 'function') {
            window.addDemoProducts();
        }
        
        // Add items to cart for demo
        if (typeof window.addDemoCartItems === 'function') {
            window.addDemoCartItems();
        }
        
        // Trigger any demo modes
        if (typeof window.enableDemoMode === 'function') {
            window.enableDemoMode();
        }
        """
        
        try:
            self.driver.execute_script(demo_script)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️  Could not inject demo data: {e}")
    
    def screenshot_static_files(self):
        """Take screenshots of static HTML files."""
        print("\n📸 Taking screenshots of static HTML files...")
        
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
            }
        ]
        
        base_path = Path("/Workshop/carthub")
        
        for file_info in html_files:
            file_path = base_path / file_info["path"]
            if file_path.exists():
                file_url = f"file://{file_path.absolute()}"
                print(f"📄 Loading: {file_info['path']}")
                
                try:
                    self.driver.get(file_url)
                    
                    # Extended wait for page to load completely
                    print(f"⏳ Waiting for page to load completely...")
                    time.sleep(3)
                    
                    # Wait for page to load
                    self.wait_for_element("body", timeout=10)
                    
                    # Additional wait for JavaScript and CSS to load
                    time.sleep(2)
                    
                    # Inject demo data if possible
                    self.inject_demo_data()
                    
                    # Additional wait after demo data injection
                    time.sleep(1)
                    
                    # Take screenshot (includes 5-second wait)
                    self.take_screenshot(
                        file_info["screenshot"], 
                        file_info["description"], 
                        full_page=True
                    )
                    
                    # Take viewport screenshot as well (includes 5-second wait)
                    viewport_name = file_info["screenshot"].replace(".png", "-viewport.png")
                    self.take_screenshot(
                        viewport_name,
                        f"{file_info['description']} (viewport)",
                        full_page=False
                    )
                    
                except Exception as e:
                    print(f"❌ Error processing {file_info['path']}: {e}")
            else:
                print(f"⚠️  File not found: {file_info['path']}")
    
    def screenshot_mobile_views(self):
        """Take mobile responsive screenshots."""
        print("\n📱 Taking mobile responsive screenshots...")
        
        mobile_sizes = [
            {"name": "iPhone SE", "width": 375, "height": 667},
            {"name": "iPhone 12", "width": 390, "height": 844},
            {"name": "iPad", "width": 768, "height": 1024},
        ]
        
        html_files = [
            "frontend/cart/main/shopping-cart-amazon-style.html",
            "enhanced-shopping-cart.html"
        ]
        
        base_path = Path("/Workshop/carthub")
        
        for html_file in html_files:
            file_path = base_path / html_file
            if not file_path.exists():
                continue
                
            file_url = f"file://{file_path.absolute()}"
            
            for size in mobile_sizes:
                try:
                    print(f"📱 Testing {size['name']} ({size['width']}x{size['height']})")
                    
                    # Set mobile viewport
                    self.driver.set_window_size(size['width'], size['height'])
                    self.driver.get(file_url)
                    time.sleep(2)
                    
                    # Wait for page to load
                    self.wait_for_element("body", timeout=5)
                    
                    # Inject demo data
                    self.inject_demo_data()
                    
                    # Take screenshot
                    filename = f"mobile-{size['name'].lower().replace(' ', '-')}-{Path(html_file).stem}.png"
                    self.take_screenshot(
                        filename,
                        f"{Path(html_file).stem} on {size['name']}",
                        full_page=True
                    )
                    
                except Exception as e:
                    print(f"❌ Error with mobile screenshot: {e}")
        
        # Reset to desktop size
        self.driver.set_window_size(1920, 1080)
    
    def screenshot_api_docs(self, api_url="http://localhost:8000"):
        """Take screenshots of API documentation."""
        print("\n📚 Taking API documentation screenshots...")
        
        api_endpoints = [
            {"url": f"{api_url}/docs", "name": "swagger-ui.png", "desc": "Swagger UI API Documentation"},
            {"url": f"{api_url}/redoc", "name": "redoc-ui.png", "desc": "ReDoc API Documentation"},
            {"url": f"{api_url}/health", "name": "health-endpoint.png", "desc": "Health Check Endpoint"}
        ]
        
        for endpoint in api_endpoints:
            try:
                print(f"🌐 Accessing: {endpoint['url']}")
                self.driver.get(endpoint['url'])
                time.sleep(3)
                
                # Wait for content to load
                if "docs" in endpoint['url']:
                    self.wait_for_element(".swagger-ui, #swagger-ui", timeout=10)
                elif "redoc" in endpoint['url']:
                    self.wait_for_element(".redoc-container, [data-testid='api-docs']", timeout=10)
                
                self.take_screenshot(
                    endpoint['name'],
                    endpoint['desc'],
                    full_page=True
                )
                
            except Exception as e:
                print(f"⚠️  Could not access {endpoint['url']}: {e}")
    
    def generate_screenshot_report(self):
        """Generate a report of all screenshots taken."""
        report_path = self.output_dir / "screenshot_report.json"
        
        report = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_screenshots": len(self.screenshots_taken),
            "output_directory": str(self.output_dir),
            "screenshots": self.screenshots_taken
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Screenshot report saved: {report_path}")
        
        # Generate markdown report
        md_report_path = self.output_dir / "screenshot_report.md"
        with open(md_report_path, 'w') as f:
            f.write("# Screenshot Generation Report\n\n")
            f.write(f"Generated: {report['generated_at']}\n")
            f.write(f"Total Screenshots: {report['total_screenshots']}\n\n")
            
            f.write("## Screenshots Taken\n\n")
            for screenshot in self.screenshots_taken:
                f.write(f"### {screenshot['filename']}\n")
                f.write(f"**Description**: {screenshot['description']}\n\n")
                f.write(f"![{screenshot['description']}]({screenshot['filename']})\n\n")
        
        print(f"📝 Markdown report saved: {md_report_path}")
    
    def run_full_screenshot_suite(self, include_api=True, include_mobile=True):
        """Run the complete screenshot generation suite."""
        print("🚀 Starting comprehensive screenshot generation...")
        print(f"📁 Output directory: {self.output_dir}")
        
        try:
            # Always take static file screenshots
            self.screenshot_static_files()
            
            # Mobile screenshots
            if include_mobile:
                self.screenshot_mobile_views()
            
            # API documentation
            if include_api:
                self.screenshot_api_docs()
            
            # Generate report
            self.generate_screenshot_report()
            
            print(f"\n✅ Screenshot generation completed!")
            print(f"📸 Total screenshots taken: {len(self.screenshots_taken)}")
            print(f"📁 Screenshots saved to: {self.output_dir}")
            
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
    """Main function with enhanced command line interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced automated screenshot generator for Carthub documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/take_screenshots_enhanced.py
  python scripts/take_screenshots_enhanced.py --no-headless --output screenshots/
  python scripts/take_screenshots_enhanced.py --no-api --no-mobile
        """
    )
    
    parser.add_argument("--url", default="http://localhost:3000", 
                       help="Base URL of the frontend application")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="Base URL of the API documentation")
    parser.add_argument("--output", default="docs/images", 
                       help="Output directory for screenshots")
    parser.add_argument("--no-headless", action="store_true", 
                       help="Run browser in visible mode (useful for debugging)")
    parser.add_argument("--no-api", action="store_true", 
                       help="Skip API documentation screenshots")
    parser.add_argument("--no-mobile", action="store_true", 
                       help="Skip mobile responsive screenshots")
    
    args = parser.parse_args()
    
    print("🎯 Carthub Automated Screenshot Generator")
    print("=" * 50)
    
    # Create screenshot generator
    generator = EnhancedCarthubScreenshotGenerator(
        base_url=args.url,
        output_dir=args.output,
        headless=not args.no_headless
    )
    
    # Run screenshot suite
    generator.run_full_screenshot_suite(
        include_api=not args.no_api,
        include_mobile=not args.no_mobile
    )


if __name__ == "__main__":
    main()
