import threading
import time

import evdev
from evdev import InputDevice, UInput, ecodes

# --- CONFIG MACRO ---
KEY_TO_PRESS = ecodes.KEY_D  # Keyboard key to repeat
TOGGLE_KEY = ecodes.KEY_GRAVE  # Toggle macro keyboard ON/OFF (`)
DELAY = 0.5  # Delay between key presses

# --- CONFIG HOLD CLICK ---
HOLD_TOGGLE_KEY = ecodes.KEY_HOME  # Toggle hold click ON/OFF
HOLD_BUTTON = ecodes.BTN_LEFT  # BTN_LEFT / BTN_RIGHT / BTN_MIDDLE
# -------------------------

is_running = False
is_holding = False
hold_lock = threading.Lock()

# Virtual keyboard
ui = UInput()

# Virtual mouse (requires EV_REL to be recognized as a mouse by the compositor)
mouse = UInput(
    {
        ecodes.EV_KEY: [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE],
        ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y, ecodes.REL_WHEEL],
    },
    name="macro-virtual-mouse",
)


def find_keyboard():
    """Auto find physical keyboard"""
    devices = [InputDevice(path) for path in evdev.list_devices()]
    keyboards = []
    for dev in devices:
        caps = dev.capabilities()
        if ecodes.EV_KEY in caps and ecodes.KEY_A in caps[ecodes.EV_KEY]:
            keyboards.append(dev)
    return keyboards


def set_hold(state: bool):
    """Hold (True) or release (False) the mouse button."""
    global is_holding
    with hold_lock:
        if state == is_holding:
            return
        is_holding = state
        mouse.write(ecodes.EV_KEY, HOLD_BUTTON, 1 if state else 0)
        mouse.syn()


def macro_loop():
    """Background process for executing automated typing."""
    while True:
        if is_running:
            ui.write(ecodes.EV_KEY, KEY_TO_PRESS, 1)  # press
            ui.write(ecodes.EV_KEY, KEY_TO_PRESS, 0)  # release
            ui.syn()
            time.sleep(DELAY)
        else:
            time.sleep(0.5)


def listen_device(dev):
    """Capture keyboard events from one device."""
    global is_running
    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:  # 1 = key down
                if event.code == TOGGLE_KEY:
                    is_running = not is_running
                    status = "ON (ACTIVE)" if is_running else "OFF (INACTIVE)"
                    print(f"[{time.strftime('%H:%M:%S')}] Macro Status: {status}")

                elif event.code == HOLD_TOGGLE_KEY:
                    set_hold(not is_holding)
                    status = "ON (HELD)" if is_holding else "OFF (RELEASED)"
                    print(f"[{time.strftime('%H:%M:%S')}] Hold Click: {status}")
    except OSError:
        pass


def main():
    print("=============================================")
    print("    ARCH LINUX (HYPRLAND) AUTO KEYBOARD MACRO  ")
    print("    (evdev version - Wayland compatible)      ")
    print("=============================================")
    print(f" Macro Key      : '{ecodes.KEY[KEY_TO_PRESS]}'")
    print(f" Toggle Macro   : [{ecodes.KEY[TOGGLE_KEY]}]")
    print(
        f" Toggle Hold    : [{ecodes.KEY[HOLD_TOGGLE_KEY]}] ({ecodes.BTN[HOLD_BUTTON]})"
    )
    print(f" Delay Interval : {DELAY} seconds")
    print("=============================================")

    keyboards = find_keyboard()
    if not keyboards:
        print("ERROR: No keyboards detected in /dev/input/.")
        print(
            "Ensure your user is added to the 'input' group, then log out and log back in."
        )
        return

    print("Keyboards detected:")
    for kb in keyboards:
        print(f"  - {kb.path} ({kb.name})")
    print("=============================================")
    print("Press Ctrl+C in the terminal to stop the program.\n")

    threading.Thread(target=macro_loop, daemon=True).start()

    for kb in keyboards:
        threading.Thread(target=listen_device, args=(kb,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMacro program stopped.")
    finally:
        # IMPORTANT: ensure the mouse button is released when the program exits
        set_hold(False)
        mouse.close()
        ui.close()


if __name__ == "__main__":
    main()
