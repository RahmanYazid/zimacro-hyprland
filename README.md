# Arch Linux (Hyprland) Auto Keyboard & Click Macro

A simple Python script for automating repeated key presses (auto-key macro) and holding a mouse button down (auto hold-click), each with its own ON/OFF toggle triggered by a physical key. Built specifically to work on **Wayland/Hyprland**, using `evdev` instead of `pynput`, since `pynput` cannot detect or simulate input globally on Wayland compositors.

## Features

- Automatically repeats a chosen key press with a configurable delay
- **Auto hold-click:** holds a mouse button (left/right/middle) down continuously until you toggle it off
- Separate ON/OFF toggle keys for each feature (default: `Insert` for the key macro, `Home` for hold-click)
- Both features can be used independently
- Auto-detects connected physical keyboards
- Compatible with Hyprland and other Wayland compositors (not blocked by the global-input restrictions that affect `pynput`)

## Requirements

- Arch Linux (or any other Linux distro) with Hyprland / a Wayland compositor
- Python 3.10+
- Access to `/dev/uinput` and `/dev/input/eventX` (via membership in the `input` group)
- Python package: `evdev`

## Project Structure

```
macropython/
├── macro.py            # Main script
├── README.md            # This documentation
├── requirements.txt      # Python dependency list
└── .gitignore            # Ignores venv/ and cache files
```

## Installation

### 1. Clone the repository

```bash
# HTTPS
git clone https://github.com/RahmanYazid/hyprland-keyboard-macro.git

# or via SSH (requires SSH key already set up on your GitHub account)
git clone git@github.com:RahmanYazid/hyprland-keyboard-macro.git

cd hyprland-keyboard-macro
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # bash/zsh
# or for fish shell:
source venv/bin/activate.fish

pip install -r requirements.txt
```

### 3. Add your user to the `input` group

The program needs read access to the keyboard device (`/dev/input/eventX`) and write access to `/dev/uinput` to simulate key presses and mouse clicks. Both are typically owned by the `input` group.

```bash
sudo usermod -aG input $USER
```

> **Important:** after running this command, you **must log out and log back in** (or restart your PC). Group changes do not take effect in your currently running terminal session.

After logging back in, verify the group is active:

```bash
groups
```

Make sure `input` appears in the output.

### 4. Run the program

```bash
cd hyprland-keyboard-macro
source venv/bin/activate        # or activate.fish for fish shell
python macro.py
```

If successful, the program will list the detected keyboards and be ready to use.

## Usage

### Auto key macro

1. Run `macro.py` — keep the terminal running in the background
2. Focus your cursor on the target application/text field
3. Press **Insert** to activate the macro (the terminal will print `ON (ACTIVE)`)
4. Press **Insert** again to deactivate it (`OFF (INACTIVE)`)

### Auto hold-click

1. Run `macro.py` — keep the terminal running in the background
2. Move your mouse cursor to the target location/application
3. Press **Home** to start holding the mouse button (default: left click). The button stays pressed continuously until you toggle it off
4. Press **Home** again to release the button

> **Tip:** always toggle hold-click OFF before closing the terminal, so the mouse button isn't left in a pressed state. If the program exits with Ctrl+C while hold-click is active, make sure the button gets released (a physical click of that button will also release it).

### Exiting

Press **Ctrl+C** in the terminal to fully exit the program.

## Configuration

All settings are at the top of `macro.py`:

```python
# --- CONFIG KEY MACRO ---
KEY_TO_PRESS = ecodes.KEY_D       # Key to auto-type
TOGGLE_KEY = ecodes.KEY_INSERT    # Key used to toggle ON/OFF
DELAY = 0.5                       # Delay between key presses (in seconds)

# --- CONFIG HOLD CLICK ---
HOLD_TOGGLE_KEY = ecodes.KEY_HOME  # Toggle hold click ON/OFF
HOLD_BUTTON = ecodes.BTN_LEFT      # BTN_LEFT / BTN_RIGHT / BTN_MIDDLE
```

| Setting           | Description                                                                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `KEY_TO_PRESS`    | The key that gets pressed repeatedly. Use `ecodes.KEY_<NAME>` constants, e.g. `ecodes.KEY_E`, `ecodes.KEY_SPACE`, `ecodes.KEY_ENTER`. The full list is available in the `evdev.ecodes` module. |
| `TOGGLE_KEY`      | The physical key used to enable/disable the key macro. Can be changed to any rarely-used key, e.g. `ecodes.KEY_END`, `ecodes.KEY_SCROLLLOCK`.                                                  |
| `DELAY`           | Delay between key presses, in seconds. Lower values type faster (e.g. `0.1` = 10x/sec, `0.5` = 2x/sec).                                                                                        |
| `HOLD_TOGGLE_KEY` | The physical key used to enable/disable hold-click. Must be different from `TOGGLE_KEY`. Default: `ecodes.KEY_HOME`.                                                                           |
| `HOLD_BUTTON`     | The mouse button that gets held down: `ecodes.BTN_LEFT`, `ecodes.BTN_RIGHT`, or `ecodes.BTN_MIDDLE`.                                                                                           |

After changing the configuration, save the file and re-run `python macro.py`.

## Troubleshooting

**`ModuleNotFoundError: No module named 'evdev'`**
Make sure the virtual environment is activated (`source venv/bin/activate`) before running `pip install -r requirements.txt` and `python macro.py`.

**`Permission denied` when opening the device**
Make sure your user is in the `input` group (`groups`) and that you've logged out/back in after running `usermod -aG input $USER`.

**The program runs but the Insert / Home toggle isn't detected**
Check whether `macro.py` successfully detected a physical keyboard in the list shown at startup. If the list is empty, `evdev` likely isn't recognizing your device as a keyboard — please open an Issue.

**Hold-click doesn't work / the mouse button isn't pressed**
Make sure the virtual device created via `/dev/uinput` has the mouse button you chose (`HOLD_BUTTON`) registered in its capabilities. Also check that `HOLD_TOGGLE_KEY` isn't the same as `TOGGLE_KEY`, and that the target application accepts input from virtual devices.

**The mouse button stays stuck after exiting**
This can happen if the program was closed while hold-click was ON. Press the physical mouse button once to release it, and always toggle hold-click OFF before exiting.

**Want a shortcut command without `cd` and `activate` every time**
Add an alias to your shell config, e.g. for fish (`~/.config/fish/config.fish`):

```fish
alias macro="~/path/to/repo/venv/bin/python ~/path/to/repo/macro.py"
```

## Disclaimer

This script simulates real keyboard and mouse input at the system level. Use it responsibly, some applications/games prohibit the use of macros/auto-key/auto-click tools and may apply penalties according to their own policies.
