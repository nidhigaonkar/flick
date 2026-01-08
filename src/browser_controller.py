"""
Browser Controller
Automates YouDJ website controls using Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from typing import Optional


class YouDJController:
    """Controls YouDJ website through browser automation"""
    
    def __init__(self):
        """Initialize the browser controller"""
        self.driver = None
        self.wait = None
        self.actions = None
        self.is_initialized = False
        
        # Store current values to avoid redundant updates
        self.current_values = {
            'crossfader': 0.5,
            'volume_left': 0.7,
            'volume_right': 0.7,
            'filter': 0.5
        }
        
        # Minimum change threshold to trigger update
        self.update_threshold = 0.02
    
    def start(self, headless: bool = False) -> bool:
        """
        Start the browser and navigate to YouDJ
        
        Args:
            headless: Run browser in headless mode (no GUI)
            
        Returns:
            True if successful
        """
        try:
            options = webdriver.ChromeOptions()
            
            if headless:
                options.add_argument('--headless')
            
            # Additional options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Allow audio playback
            options.add_argument('--autoplay-policy=no-user-gesture-required')
            
            # Start browser
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            self.actions = ActionChains(self.driver)
            
            # Navigate to YouDJ
            print("Loading YouDJ...")
            self.driver.get("https://youdj.online/")
            
            # Wait for page to load
            time.sleep(3)
            
            # Handle any welcome popups/dialogs
            self._handle_initial_dialogs()
            
            self.is_initialized = True
            print("YouDJ loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error starting browser: {e}")
            return False
    
    def _handle_initial_dialogs(self):
        """Close any initial welcome dialogs or popups"""
        try:
            # Try to find and click welcome dialog close button
            # Common selectors for YouDJ popups
            close_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'OK')]",
                "//button[contains(text(), 'Close')]",
                "//*[contains(@class, 'close')]",
                "//div[contains(@class, 'modal')]//button"
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.XPATH, selector)
                    if close_btn.is_displayed():
                        close_btn.click()
                        time.sleep(0.5)
                        print("Closed welcome dialog")
                except:
                    continue
                    
        except Exception as e:
            # It's okay if we can't find/close dialogs
            pass
    
    def stop(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_initialized = False
    
    def set_crossfader(self, value: float):
        """
        Set the crossfader position
        
        Args:
            value: Position from 0 (left) to 1 (right), 0.5 is center
        """
        if not self._should_update('crossfader', value):
            return
        
        try:
            # Find the crossfader element
            # YouDJ typically uses a slider input or draggable element
            crossfader = self._find_crossfader_element()
            
            if crossfader:
                self._drag_slider_to_position(crossfader, value)
                self.current_values['crossfader'] = value
                print(f"✓ Crossfader set to {value:.2f}")
            else:
                print("⚠ Crossfader element not found on page")
                
        except Exception as e:
            print(f"✗ Error setting crossfader: {e}")
    
    def set_volume(self, deck: str, value: float):
        """
        Set volume for a deck
        
        Args:
            deck: 'left' or 'right'
            value: Volume from 0 (silent) to 1 (max)
        """
        control_key = f'volume_{deck}'
        
        if not self._should_update(control_key, value):
            return
        
        try:
            volume_slider = self._find_volume_slider(deck)
            
            if volume_slider:
                self._drag_slider_to_position(volume_slider, value, vertical=True)
                self.current_values[control_key] = value
                
        except Exception as e:
            print(f"Error setting {deck} volume: {e}")
    
    def play_deck(self, deck: str):
        """
        Press play button for a deck
        
        Args:
            deck: 'left' or 'right'
        """
        try:
            play_button = self._find_play_button(deck)
            if play_button and play_button.is_displayed():
                play_button.click()
                print(f"Playing {deck} deck")
        except Exception as e:
            print(f"Error playing {deck} deck: {e}")
    
    def pause_deck(self, deck: str):
        """
        Press pause/cue button for a deck
        
        Args:
            deck: 'left' or 'right'
        """
        try:
            # Try to click the play button again to pause, or find cue button
            play_button = self._find_play_button(deck)
            if play_button and play_button.is_displayed():
                play_button.click()
                print(f"Pausing {deck} deck")
        except Exception as e:
            print(f"Error pausing {deck} deck: {e}")
    
    def set_filter(self, value: float):
        """
        Set filter amount
        
        Args:
            value: Filter from 0 to 1
        """
        if not self._should_update('filter', value):
            return
        
        try:
            # Find filter knobs (there's one for each deck)
            # We'll control the left deck filter for simplicity
            filter_knob = self._find_filter_knob('left')
            
            if filter_knob:
                self._rotate_knob(filter_knob, value)
                self.current_values['filter'] = value
                
        except Exception as e:
            print(f"Error setting filter: {e}")
    
    def toggle_effect(self):
        """Toggle an effect (e.g., slicer, echo)"""
        try:
            # Find and click an effect button
            effect_button = self.driver.find_element(By.XPATH, 
                "//button[contains(@class, 'fx') or contains(text(), 'fx')]")
            if effect_button.is_displayed():
                effect_button.click()
                print("Toggled effect")
        except Exception as e:
            print(f"Error toggling effect: {e}")
    
    def click_at_position(self, x: float, y: float):
        """
        Click at a specific position on the page (normalized 0-1 coordinates)
        
        Args:
            x: Horizontal position (0 = left, 1 = right)
            y: Vertical position (0 = top, 1 = bottom)
        """
        try:
            # Get viewport dimensions
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Convert normalized coords to pixel coords
            pixel_x = int(x * viewport_width)
            pixel_y = int(y * viewport_height)
            
            # Use JavaScript to click at position
            self.driver.execute_script(f"""
                var element = document.elementFromPoint({pixel_x}, {pixel_y});
                if (element) {{
                    element.click();
                    console.log('Clicked element:', element);
                }}
            """)
            
            print(f"Clicked at position ({x:.2f}, {y:.2f})")
            
        except Exception as e:
            print(f"Error clicking at position: {e}")
    
    # Helper methods for finding elements
    
    def _find_crossfader_element(self):
        """Find the crossfader slider element"""
        try:
            # Try different possible selectors
            selectors = [
                "//input[@type='range' and contains(@class, 'crossfader')]",
                "//div[contains(@class, 'crossfader')]//input",
                "//input[contains(@id, 'crossfader')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return element
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return None
    
    def _find_volume_slider(self, deck: str):
        """Find volume slider for a deck"""
        try:
            # Volume sliders are typically vertical on each side
            # Left deck is usually on the left side, right on right
            deck_class = 'left' if deck == 'left' else 'right'
            
            selectors = [
                f"//div[contains(@class, '{deck_class}')]//input[@type='range']",
                f"//input[contains(@id, 'volume') and contains(@class, '{deck_class}')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return element
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return None
    
    def _find_play_button(self, deck: str):
        """Find play button for a deck"""
        try:
            # Play buttons typically have a play icon or text
            deck_indicators = ['left', 'right'] if deck == 'left' else ['right', 'left']
            
            selectors = [
                f"//div[contains(@class, '{deck}')]//button[contains(@class, 'play')]",
                f"//button[contains(@aria-label, 'play') and contains(@class, '{deck}')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return element
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return None
    
    def _find_filter_knob(self, deck: str):
        """Find filter knob for a deck"""
        try:
            selectors = [
                f"//div[contains(@class, '{deck}')]//div[contains(@class, 'filter')]//input",
                f"//input[contains(@id, 'filter') and contains(@class, '{deck}')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return element
                except:
                    continue
                    
        except Exception as e:
            pass
        
        return None
    
    def _drag_slider_to_position(self, element, value: float, vertical: bool = False):
        """
        Drag a slider to a specific position
        
        Args:
            element: Slider element
            value: Target value (0-1)
            vertical: True if slider is vertical
        """
        try:
            # Get slider dimensions
            size = element.size
            location = element.location
            
            # Calculate target position
            if vertical:
                # For vertical sliders: 0 at bottom, 1 at top (inverted)
                target_y = location['y'] + size['height'] * (1 - value)
                target_x = location['x'] + size['width'] / 2
            else:
                # For horizontal sliders: 0 at left, 1 at right
                target_x = location['x'] + size['width'] * value
                target_y = location['y'] + size['height'] / 2
            
            # Move to element and drag
            self.actions.move_to_element(element).click_and_hold().perform()
            self.actions.move_by_offset(
                target_x - location['x'] - size['width'] / 2,
                target_y - location['y'] - size['height'] / 2
            ).perform()
            self.actions.release().perform()
            
        except Exception as e:
            # Alternative: Use JavaScript to set value directly
            try:
                self.driver.execute_script(
                    f"arguments[0].value = {value}; arguments[0].dispatchEvent(new Event('input'));",
                    element
                )
            except:
                pass
    
    def _rotate_knob(self, element, value: float):
        """
        Rotate a knob control to a specific position
        
        Args:
            element: Knob element
            value: Target value (0-1)
        """
        # Similar to slider, but might need different approach
        self._drag_slider_to_position(element, value, vertical=False)
    
    def _should_update(self, control: str, new_value: float) -> bool:
        """
        Check if control value has changed enough to warrant an update
        
        Args:
            control: Control name
            new_value: New value
            
        Returns:
            True if should update
        """
        if control not in self.current_values:
            return True
        
        diff = abs(self.current_values[control] - new_value)
        return diff >= self.update_threshold


if __name__ == "__main__":
    # Test the browser controller
    print("Testing YouDJ Browser Controller...")
    print("This will open a browser window with YouDJ")
    
    controller = YouDJController()
    
    if controller.start(headless=False):
        print("Browser started! Testing controls...")
        
        time.sleep(2)
        
        # Test crossfader
        print("Moving crossfader left...")
        controller.set_crossfader(0.2)
        time.sleep(1)
        
        print("Centering crossfader...")
        controller.set_crossfader(0.5)
        time.sleep(1)
        
        print("Moving crossfader right...")
        controller.set_crossfader(0.8)
        time.sleep(1)
        
        print("\nTest complete! Browser will close in 3 seconds...")
        time.sleep(3)
        
        controller.stop()
    else:
        print("Failed to start browser")

