# -*- coding: utf-8 -*- ~

import os
from re import DEBUG
import sys
import math
import time
import signal
import threading
import traceback
from typing import Optional, Tuple
import tkinter as tk
from PIL import Image, ImageTk
import psutil
import types

# Change directory to the folder containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print("Current directory:", os.getcwd())


class Configs:
    """Application-wide configuration"""
    
    class App:
        USER_RESOURCE_MONITOR = True

    class Window:
        BG_COLOR = 'darkblue'
        TRANSPARENT_COLOR = 'darkblue'
        TOPMOST = True
        FULLSCREEN = True
        OVERRIDE_REDIRECT = True

    class Image:
        PATH = "rocket_ai.png"
        ROTATION_OFFSET = -95
        SIZE = (40, 40)
        RESAMPLE_METHOD = Image.BILINEAR

    class RocketPhysics:
        LABEL_BG_COLOR = 'darkblue'
        MAX_SPEED = 6
        ACCELERATION = 0.2
        STEERING_SENSITIVITY = 0.05
        DRAG_FACTOR = 0.95
        FOLLOW_THRESHOLD = 70
        DECELERATION_DISTANCE = 200

    class Animation:
        UPDATE_INTERVAL_MS = 10

    class ResourceMonitor:
        MONITOR_INTERVAL_SEC = 1


class WindowManager:
    """Manages the application window and its properties"""
    
    def __init__(self):
        self.root = tk.Tk()
        self._setup_window()

    def _setup_window(self) -> None:
        """Configure window attributes and geometry"""
        try:
            self.root.config(bg=Configs.Window.BG_COLOR)
            self.root.attributes('-transparentcolor', Configs.Window.TRANSPARENT_COLOR)
            self.root.attributes('-topmost', Configs.Window.TOPMOST)
            self.root.attributes('-fullscreen', Configs.Window.FULLSCREEN)
            self.root.overrideredirect(Configs.Window.OVERRIDE_REDIRECT)
        except tk.TclError as e:
            sys.exit(f"Failed to initialize window: {e}")

    def get_root(self) -> tk.Tk:
        return self.root

    def start_main_loop(self) -> None:
        self.root.mainloop()


class ImageManager:
    """Handles image loading and transformation operations"""
    
    def __init__(self):
        self.base_image = self._load_base_image()
        
    def _load_base_image(self) -> Image.Image:
        """Load and preprocess the base rocket image"""
        try:
            original_img = Image.open(Configs.Image.PATH)
            return original_img.rotate(
                Configs.Image.ROTATION_OFFSET,
                resample=Configs.Image.RESAMPLE_METHOD,
                expand=True
            ).resize(Configs.Image.SIZE)
        except FileNotFoundError:
            sys.exit(f"Error: Image file '{Configs.Image.PATH}' not found")
        except Exception as e:
            sys.exit(f"Error loading image: {str(e)}")

    def get_rotated_image(self, angle: float) -> ImageTk.PhotoImage:
        """Return a rotated version of the base image"""
        return ImageTk.PhotoImage(
            self.base_image.rotate(
                angle,
                resample=Configs.Image.RESAMPLE_METHOD,
                expand=True
            )
        )


class Rocket:
    """Manages rocket physics and visual representation"""
    
    def __init__(self, window_manager: WindowManager, image_manager: ImageManager):
        self.window = window_manager
        self.image_manager = image_manager
        
        # Initialize physics properties
        self.x = self.window.get_root().winfo_screenwidth() // 2
        self.y = self.window.get_root().winfo_screenheight() // 2
        self.angle = 0.0
        self.speed = 0.0

        # Setup UI components
        self.label = tk.Label(
            self.window.get_root(),
            bg=Configs.RocketPhysics.LABEL_BG_COLOR,
            bd=0
        )
        self.label.place(x=self.x, y=self.y, anchor=tk.CENTER)
        # Add right-click binding to exit app
        self.label.bind("<Button-3>", lambda e: self.window.get_root().destroy())
        self.update_display()

    def update(self, target_position: Tuple[int, int]) -> None:
        """Update rocket state based on target position"""
        target_x, target_y = target_position
        dx, dy = target_x - self.x, target_y - self.y

        self._update_angle(dx, dy)
        self._update_speed(dx, dy)
        self._update_position(dx, dy)
        self.update_display()

    def _update_angle(self, dx: float, dy: float) -> None:
        """Adjust rocket's facing angle based on target position"""
        if dx == 0 and dy == 0:
            return
            
        target_angle = math.degrees(math.atan2(-dy, dx))
        angle_diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += angle_diff * Configs.RocketPhysics.STEERING_SENSITIVITY

    def _update_speed(self, dx: float, dy: float) -> None:
        """Adjust rocket's speed based on distance to target"""
        distance = math.hypot(dx, dy)
        if distance > Configs.RocketPhysics.DECELERATION_DISTANCE:
            self.speed = min(
                self.speed + Configs.RocketPhysics.ACCELERATION,
                Configs.RocketPhysics.MAX_SPEED
            )
        else:
            self.speed *= Configs.RocketPhysics.DRAG_FACTOR

    def _update_position(self, dx: float, dy: float) -> None:
        """Update rocket's position based on current speed and angle"""
        distance = math.hypot(dx, dy)
        if distance > Configs.RocketPhysics.FOLLOW_THRESHOLD:
            angle_rad = math.radians(self.angle)
            self.x += math.cos(angle_rad) * self.speed
            self.y -= math.sin(angle_rad) * self.speed

    def update_display(self) -> None:
        """Update the rocket's visual representation"""
        rotated_photo = self.image_manager.get_rotated_image(self.angle)
        self.label.config(image=rotated_photo)
        self.label.image = rotated_photo
        self.label.place_configure(x=self.x, y=self.y)


class ResourceMonitor:
    """Monitors and logs system resource usage"""
    
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._monitor_resources)
        self.process = psutil.Process(os.getpid())

    def start(self) -> None:
        """Start resource monitoring thread"""
        self.stop_event.clear()
        self.thread.start()

    def stop(self) -> None:
        """Stop resource monitoring thread"""
        self.stop_event.set()
        self.thread.join(timeout=1)

    def _monitor_resources(self) -> None:
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            memory = self.process.memory_info().rss / 1024 ** 2
            cpu_percent = self.process.cpu_percent(interval=1)
            num_cores = os.cpu_count() or 1
            print(f"Memory: {memory:.2f} MB | CPU: {cpu_percent/num_cores:.2f}%")
            time.sleep(Configs.ResourceMonitor.MONITOR_INTERVAL_SEC)


class RocketApp:
    """Main application controller"""
    
    def __init__(self):
        self.window_manager = WindowManager()
        self.image_manager = ImageManager()
        self.rocket: Optional[Rocket] = None
        self.resource_monitor = None
        if Configs.App.USER_RESOURCE_MONITOR:
            self.resource_monitor = ResourceMonitor()
        self._setup_signal_handling()
        self._initialize_rocket()

    def _initialize_rocket(self) -> None:
        """Initialize rocket after window is ready"""
        self.window_manager.get_root().update_idletasks()  # Ensure window dimensions are correct
        self.rocket = Rocket(self.window_manager, self.image_manager)

    def _setup_signal_handling(self) -> None:
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig: int, frame: Optional[types.FrameType]) -> None:
        """Handle shutdown signals"""
        print("\nInitiating graceful shutdown...")
        if self.resource_monitor:
            self.resource_monitor.stop()
        self.window_manager.get_root().destroy()
        sys.exit(0)

    def _animate(self) -> None:
        """Main animation loop"""
        if self.rocket:
            target_pos = (
                self.window_manager.get_root().winfo_pointerx(),
                self.window_manager.get_root().winfo_pointery()
            )
            self.rocket.update(target_pos)
            self.window_manager.get_root().after(
                Configs.Animation.UPDATE_INTERVAL_MS,
                self._animate
            )

    def run(self) -> None:
        """Start application execution"""
        try:
            if self.resource_monitor:
                self.resource_monitor.start()
            self._animate()
            self.window_manager.start_main_loop()
        except Exception as e:
            print(f"Critical error: {str(e)}")
            traceback.print_exc()
        finally:
            if self.resource_monitor:
                self.resource_monitor.stop()


if __name__ == "__main__":
    RocketApp().run()