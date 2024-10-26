import time
import platform
import ctypes
import winsound
import threading
import json
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

screen_interval_seconds = 1200  # seconds
away_interval_seconds = 20  # seconds
sound_frequency_hz = 1000  # Hz
sound_duration_ms = 125  # ms
logging = False


def log_message(message):
    if logging:
        debug_path = "debug_log.txt"
        with open(debug_path, "a") as log_file:
            log_file.write(message + "\n")


def initialize_variables():
    global screen_interval_seconds, away_interval_seconds, sound_frequency_hz, sound_duration_ms
    try:
        config_path = "config.json"
        with open(config_path, 'r') as file:
            config = json.load(file)
            screen_interval_seconds = config.get('screen_interval_seconds', screen_interval_seconds)
            away_interval_seconds = config.get('away_interval_seconds', away_interval_seconds)
            sound_frequency_hz = config.get('sound_frequency_hz', sound_frequency_hz)
            sound_duration_ms = config.get('sound_duration_ms', sound_duration_ms)
        log_message("Variables correctly initialized.")

    except FileNotFoundError:
        log_message("Config file not found. Using default values.")
        ctypes.windll.user32.MessageBoxW(0, f"Config file not found at {config_path}.\nUsing default values.", "Eye care reminder", 0x00000000 | 0x00001000)  # MB_OK | MB_TOPMOST
    except json.JSONDecodeError:
        log_message("Error decoding config file. Using default values.")
        ctypes.windll.user32.MessageBoxW(0, f"Error decoding config file at {config_path}. Using default values.", "Eye care reminder", 0x00000000 | 0x00001000)  # MB_OK | MB_TOPMOST
    except Exception as e:
        log_message(f"Error initializing variables: {e}")
        ctypes.windll.user32.MessageBoxW(0, f"Error initializing variables: {e}. \nUsing default values.", "Eye care reminder", 0x00000000 | 0x00001000)  # MB_OK | MB_TOPMOST


def play_sound():
    try:
        winsound.Beep(sound_frequency_hz, sound_duration_ms)
    except Exception as e:
        log_message(f"Error playing sound: {e}")


def wait_for_acknowledgement():
    previous_window = ctypes.windll.user32.GetForegroundWindow()

    def show_message_box():
        ctypes.windll.user32.MessageBoxW(0, f"Press OK once you are ready to look away\nand I'll ring a bell after {str(away_interval_seconds)} seconds", "Eye care reminder", 0x00000000 | 0x00001000)  # MB_OK | MB_TOPMOST

    message_thread = threading.Thread(target=show_message_box)
    message_thread.start()
    time.sleep(0.1)
    ctypes.windll.user32.SetForegroundWindow(previous_window)
    message_thread.join()


def show_reminder():
    ctypes.windll.user32.MessageBoxW(0, "Please continue to look away for the remainder of the break.", "Look Away Reminder", 0x00000000 | 0x00040000 | 0x00001000)  # MB_OK with no button | MB_SYSTEMMODAL | MB_TOPMOST


def create_icon():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 16, 56, 48), outline=(0, 0, 0), width=3)  # Outer eye
    draw.ellipse((24, 24, 40, 40), fill=(0, 0, 0))  # Pupil
    draw.line((8, 10, 16, 16), fill=(0, 0, 0), width=2)  # Top-left eyelash
    draw.line((28, 8, 32, 16), fill=(0, 0, 0), width=2)  # Top-center eyelash
    draw.line((48, 10, 56, 16), fill=(0, 0, 0), width=2)  # Top-right eyelash
    draw.line((8, 54, 16, 48), fill=(0, 0, 0), width=2)  # Bottom-left eyelash
    draw.line((28, 56, 32, 48), fill=(0, 0, 0), width=2)  # Bottom-center eyelash
    draw.line((48, 54, 56, 48), fill=(0, 0, 0), width=2)  # Bottom-right eyelash
    return image


def on_exit(icon, item):
    icon.stop()

def launch_icon():
    icon_image = create_icon()
    menu = Menu(MenuItem("Exit Eye Care Reminder", on_exit))
    icon = Icon("Eye care reminder", icon_image, menu=menu, tooltip="Eye Care Reminder", left_click=menu)
    icon.run()

def main():
    log_message(f"Application started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if platform.system() == "Windows":
        initialize_variables()

        def run_reminder():
            while True:
                time.sleep(screen_interval_seconds)
                wait_for_acknowledgement()
                time.sleep(away_interval_seconds)
                play_sound()

        reminder_thread = threading.Thread(target=run_reminder, daemon=True)
        reminder_thread.start()

        launch_icon()

    else:
        log_message("This script is intended to run on Windows.")


if __name__ == "__main__":
    main()
