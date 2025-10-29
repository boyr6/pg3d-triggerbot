import numpy as np
import pyautogui
import time
import cv2
from PIL import Image
import win32api
import win32con
import win32gui
import keyboard

class ToggleableRedClicker:
    def __init__(self):
        # Target color #FE0000 in RGB (254, 0, 0)
        self.target_color = np.array([254, 0, 0])
        self.color_tolerance = 10
        
        # Screen info
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Detection area - 50x50
        self.detection_width = 50
        self.detection_height = 50
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Fixed pixel threshold - 4 pixels required (EXTREMELY SENSITIVE)
        self.required_pixels = 4
        self.click_delay = 0.08
        self.last_click_time = 0
        
        # Toggle state
        self.enabled = True
        self.toggle_key = 'v'
        
        # Window management
        self.always_on_top = False
        self.window_handle = None
        
        # Credits
        self.author = "Vex"
        self.discord = "undertakerc"
        
        self.running = False
        
    def show_credits(self):
        """Display credits"""
        print("╔══════════════════════════════════════════════╗")
        print("║              RED CLICKER v2.0               ║")
        print("║                                              ║")
        print("║           Created by: Vex                   ║")
        print("║       Discord: undertakerc                  ║")
        print("║                                              ║")
        print("║   50x50 Detection | 4 Pixel Threshold       ║")
        print("║         Toggle with V Key                   ║")
        print("╚══════════════════════════════════════════════╝")
        print()
        
    def set_always_on_top(self, enable=True):
        """Set window always on top"""
        self.always_on_top = enable
        if enable and self.window_handle:
            try:
                win32gui.SetWindowPos(self.window_handle, win32con.HWND_TOPMOST, 
                                    0, 0, 0, 0, 
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                print("✅ Always on top: ENABLED")
            except:
                print("❌ Could not set always on top")
        else:
            try:
                win32gui.SetWindowPos(self.window_handle, win32con.HWND_NOTOPMOST, 
                                    0, 0, 0, 0, 
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                print("✅ Always on top: DISABLED")
            except:
                pass

    def toggle_clicker(self):
        """Toggle the clicker on/off"""
        self.enabled = not self.enabled
        status = "ENABLED" if self.enabled else "DISABLED"
        print(f"🔘 Clicker {status} (Press V to toggle)")
        return self.enabled

    def show_position_info(self):
        """Show where we're detecting"""
        print(f"\n=== DETECTION SETTINGS ===")
        print(f"Center: ({self.center_x}, {self.center_y})")
        print(f"Detection area: {self.detection_width}x{self.detection_height} pixels")
        print(f"Required Pixels: {self.required_pixels} out of {self.detection_width * self.detection_height}")
        print(f"Sensitivity: EXTREMELY HIGH (4 pixels)")
        print(f"Toggle Key: {self.toggle_key.upper()}")
        print(f"Current State: {'ENABLED' if self.enabled else 'DISABLED'}")
        print(f"Click delay: {self.click_delay}s")
        print(f"Target FPS: 80")
        print(f"Fullscreen: SUPPORTED")
        print(f"Always on top: {'ENABLED' if self.always_on_top else 'DISABLED'}\n")
    
    def capture_centered_area(self):
        """Capture centered area - optimized for fullscreen"""
        left = self.center_x - self.detection_width // 2
        top = self.center_y - self.detection_height // 2
        width = self.detection_width
        height = self.detection_height
        
        try:
            # Method 1: Direct screenshot (works with most fullscreen games)
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            return np.array(screenshot)
        except Exception as e:
            print(f"Capture error: {e}")
            return None
    
    def check_red_color(self, image):
        """Check for #FE0000 red color - fixed pixel count"""
        if image is None:
            return False, 0
        
        # Calculate color distance from #FE0000
        color_diff = np.abs(image.astype(np.int16) - self.target_color)
        color_distance = np.sum(color_diff, axis=2)
        
        # Count matching pixels
        matching_pixels = np.sum(color_distance <= self.color_tolerance)
        
        return matching_pixels >= self.required_pixels, matching_pixels
    
    def alternative_click_method(self):
        """Use alternative click method (win32api)"""
        try:
            # Method 1: win32api (most reliable for games)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            return True
        except:
            try:
                # Method 2: pyautogui fallback
                pyautogui.click(duration=0.01)
                return True
            except:
                return False
    
    def create_status_window(self):
        """Create a small status window"""
        cv2.namedWindow("RedClicker - by Vex", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("RedClicker - by Vex", 400, 220)  # Increased height for credits
        
        # Store window handle for always on top
        self.window_handle = win32gui.FindWindow(None, "RedClicker - by Vex")
        
        if self.always_on_top:
            self.set_always_on_top(True)
    
    def update_status_window(self, red_pixels, click_count, fps):
        """Update the status window"""
        status_img = np.zeros((220, 400, 3), dtype=np.uint8)  # Increased height
        
        # Background color based on enabled state
        if not self.enabled:
            status_img[:, :] = [50, 50, 50]  # Gray when disabled
        else:
            status_img[:, :] = [0, 0, 0]  # Black when enabled
        
        # Title with state indicator
        title_color = (100, 100, 255) if self.enabled else (100, 100, 100)
        status_text = "RED CLICKER - ENABLED" if self.enabled else "RED CLICKER - DISABLED"
        
        cv2.putText(status_img, status_text, (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, title_color, 2)
        
        # Author credit
        cv2.putText(status_img, f"by {self.author}", (300, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        # Detection info
        if self.enabled and red_pixels >= self.required_pixels:
            status = "RED DETECTED - CLICKING!"
            color = (0, 0, 255)
        elif self.enabled:
            status = "Monitoring..."
            color = (0, 255, 0)
        else:
            status = "DISABLED - Press V to enable"
            color = (100, 100, 100)
        
        cv2.putText(status_img, f"Status: {status}", (10, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.putText(status_img, f"Red Pixels: {red_pixels}/{self.required_pixels}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(status_img, f"Clicks: {click_count}", (10, 105), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(status_img, f"FPS: {fps:.1f}", (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(status_img, f"Toggle: {self.toggle_key.upper()} key", (10, 155), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Credits in status window
        cv2.putText(status_img, f"Created by: {self.author}", (10, 185), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
        cv2.putText(status_img, f"Discord: {self.discord}", (10, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
        
        cv2.putText(status_img, "Press 'Q' to quit", (10, 215), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow("RedClicker - by Vex", status_img)
    
    def run_clicker(self):
        """Main clicker loop with toggle support"""
        self.show_credits()
        print("Starting #FE0000 Auto-Clicker (50x50 - 4 pixels)")
        print(f"🔘 Toggle Key: {self.toggle_key.upper()} - Currently {'ENABLED' if self.enabled else 'DISABLED'}")
        print("⚠️  EXTREMELY SENSITIVE - May click on small red artifacts")
        print("Fullscreen support: ENABLED")
        print("Press 'Q' in status window to stop\n")
        
        # Create status window
        self.create_status_window()
        
        self.running = True
        click_count = 0
        frame_count = 0
        last_fps_time = time.time()
        last_toggle_check = time.time()
        
        try:
            while self.running:
                start_time = time.time()
                
                # Check for toggle key (limit to 10 times per second to avoid spam)
                current_time = time.time()
                if current_time - last_toggle_check > 0.1:  # 10 times per second max
                    if keyboard.is_pressed(self.toggle_key):
                        self.toggle_clicker()
                        time.sleep(0.2)  # Debounce
                        last_toggle_check = current_time
                
                # Capture the centered area
                img = self.capture_centered_area()
                
                if img is not None:
                    is_red, red_pixels = self.check_red_color(img)
                    current_time = time.time()
                    
                    # Only click if enabled AND red detected
                    if self.enabled and is_red and (current_time - self.last_click_time) >= self.click_delay:
                        if self.alternative_click_method():
                            self.last_click_time = current_time
                            click_count += 1
                            print(f"CLICK #{click_count}! {red_pixels} red pixels")
                
                # FPS management
                frame_count += 1
                current_time = time.time()
                
                # Update status window every frame
                fps = frame_count / (current_time - last_fps_time) if frame_count > 0 else 0
                self.update_status_window(red_pixels if 'red_pixels' in locals() else 0, click_count, fps)
                
                # Reset FPS counter every second
                if current_time - last_fps_time >= 1.0:
                    frame_count = 0
                    last_fps_time = current_time
                
                # Target 80 FPS
                elapsed = time.time() - start_time
                target_frame_time = 0.0125
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)
                
                # Check for exit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print(f"\nStopped by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.running = False
            cv2.destroyAllWindows()
            print(f"\n╔══════════════════════════════════════════════╗")
            print(f"║                 SESSION ENDED                 ║")
            print(f"║           Total Clicks: {click_count:6}           ║")
            print(f"║                                              ║")
            print(f"║           Thanks for using!                  ║")
            print(f"║           Created by Vex                     ║")
            print(f"║           Discord: undertakerc               ║")
            print(f"╚══════════════════════════════════════════════╝")

# SIMPLE VERSION WITHOUT WINDOW BUT WITH TOGGLE AND CREDITS
def simple_toggle_clicker():
    """Simple version without status window but with toggle and credits"""
    print("╔══════════════════════════════════════════════╗")
    print("║              RED CLICKER v2.0               ║")
    print("║                                              ║")
    print("║           Created by: Vex                   ║")
    print("║       Discord: undertakerc                  ║")
    print("║                                              ║")
    print("║   50x50 Detection | 4 Pixel Threshold       ║")
    print("║         Toggle with V Key                   ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    
    # Configuration
    TARGET_COLOR = np.array([254, 0, 0])
    TOLERANCE = 10
    WIDTH = 50
    HEIGHT = 50
    REQUIRED_PIXELS = 4
    
    # Screen info
    screen_w, screen_h = pyautogui.size()
    center_x = screen_w // 2
    center_y = screen_h // 2
    
    # Toggle state
    enabled = True
    toggle_key = 'v'
    
    # Credits
    author = "Vex"
    discord = "undertakerc"
    
    click_delay = 0.08
    last_click = 0
    click_count = 0
    frame_count = 0
    last_fps_time = time.time()
    last_toggle_check = time.time()
    
    print(f"Detection: {WIDTH}x{HEIGHT} area")
    print(f"Required: {REQUIRED_PIXELS} red pixels (EXTREMELY SENSITIVE)")
    print(f"Current State: {'ENABLED' if enabled else 'DISABLED'}")
    print(f"Fullscreen: SUPPORTED")
    print("Starting in 3 seconds...")
    time.sleep(3)
    print("RUNNING! Press V to toggle, Ctrl+C to stop\n")
    
    try:
        while True:
            frame_start = time.time()
            
            # Check for toggle key
            current_time = time.time()
            if current_time - last_toggle_check > 0.1:
                if keyboard.is_pressed(toggle_key):
                    enabled = not enabled
                    status = "ENABLED" if enabled else "DISABLED"
                    print(f"🔘 Clicker {status}")
                    time.sleep(0.2)  # Debounce
                    last_toggle_check = current_time
            
            # Capture area
            screenshot = pyautogui.screenshot(
                region=(
                    center_x - WIDTH // 2,
                    center_y - HEIGHT // 2,
                    WIDTH,
                    HEIGHT
                )
            )
            img = np.array(screenshot)
            
            # Check for #FE0000
            color_diff = np.abs(img.astype(np.int16) - TARGET_COLOR)
            color_distance = np.sum(color_diff, axis=2)
            matching_pixels = np.sum(color_distance <= TOLERANCE)
            
            current_time = time.time()
            
            # Click if enabled AND detected
            if enabled and matching_pixels >= REQUIRED_PIXELS and (current_time - last_click) >= click_delay:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.005)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                
                last_click = current_time
                click_count += 1
                print(f"CLICK #{click_count}! {matching_pixels} red pixels")
            
            # FPS management
            frame_count += 1
            elapsed = time.time() - frame_start
            target_time = 0.0125
            
            if elapsed < target_time:
                time.sleep(target_time - elapsed)
            
            # FPS counter with state indicator
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:
                fps = frame_count / (current_time - last_fps_time)
                state_indicator = "[ON] " if enabled else "[OFF]"
                print(f"{state_indicator} FPS: {fps:.1f} | Clicks: {click_count} | by Vex", end='\r')
                frame_count = 0
                last_fps_time = current_time
            
    except KeyboardInterrupt:
        print(f"\n\n╔══════════════════════════════════════════════╗")
        print(f"║                 SESSION ENDED                 ║")
        print(f"║           Total Clicks: {click_count:6}           ║")
        print(f"║                                              ║")
        print(f"║           Thanks for using!                  ║")
        print(f"║           Created by Vex                     ║")
        print(f"║           Discord: undertakerc               ║")
        print(f"╚══════════════════════════════════════════════╝")

if __name__ == "__main__":
    print("RED CLICKER - 50x50 Detection (4 pixels required)")
    print("🔘 TOGGLEABLE - Press V to enable/disable")
    print("⚠️  EXTREMELY SENSITIVE - Will click on very small red elements")
    print("Fullscreen & Always On Top Support")
    print("\nChoose mode:")
    print("1. Advanced (with status window + toggle + always on top)")
    print("2. Simple (no window, but with toggle)")
    
    choice = input("Select (1/2): ").strip()
    
    if choice == "1":
        clicker = ToggleableRedClicker()
        
        # Ask about always on top
        always_top = input("Enable always on top? (y/n): ").strip().lower()
        if always_top == 'y':
            clicker.always_on_top = True
        
        clicker.show_position_info()
        clicker.run_clicker()
        
    else:
        simple_toggle_clicker()
