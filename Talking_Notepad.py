import pyautogui
import time
import pyperclip
import re
import subprocess
import keyboard
from llama_cpp import Llama
import os
import importlib.util

import sys
# Check if torch is available and import it if yes
torch_spec = importlib.util.find_spec("torch")
torch = importlib.util.module_from_spec(torch_spec) if torch_spec else None
if torch_spec:
    torch_spec.loader.exec_module(torch)
    
if torch and torch.cuda.is_available():
    n_gpu_layers = torch.cuda.device_count() * 35
else:
    n_gpu_layers = 0

# Determine the base path for accessing data files in the bundle
if getattr(sys, 'frozen', False):
    # If the application is frozen (packaged by PyInstaller), use the temporary folder
    base_path = sys._MEIPASS
else:
    # If running in a normal Python environment, use the current directory
    base_path = "."

model_path = os.path.join(base_path, "model", "tinyllama-1.1b-chat-v1.0.Q8_0.gguf")



# Initialize the Llama model with the adjusted path
llm = Llama(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    n_ctx=2048
)

def exit_application():
    print("Exiting application.")
    keyboard.unhook_all()  # This will unhook all keyboard listeners
    os._exit(0)  # Forcefully exit the program

# Set up the hotkey for the ESC key
keyboard.add_hotkey('esc', exit_application)



import threading
import pyautogui
import time


def show_thinking_animation(stop_event):
    while not stop_event.is_set():
        pyautogui.typewrite('Thinking...', 0.2)
        time.sleep(0.5)  # Adjust timing as needed
        pyautogui.hotkey('ctrl', 'shift', 'left')
        pyautogui.hotkey('ctrl', 'shift', 'left')
        pyautogui.press('backspace')
        if stop_event.is_set():
            break

def standardize_text(prompt_text):
    pyautogui.press('right')
    # Variable to control the thinking animation
    thinking = True
    # Create an event to signal the thread to stop
    stop_event = threading.Event()

    # Start the thinking animation in a separate thread
    animation_thread = threading.Thread(target=show_thinking_animation, args=(stop_event,))
    animation_thread.start()

    # Keep only the last 20 lines of the input text
    lines = prompt_text.split('\n')
    last_20_lines = lines[-20:]
    # Reconstruct the last 20 lines into a single string (previously done)
    adjusted_prompt_text = '\n'.join(last_20_lines)

    # Maximum number of words allowed
    max_words = 1000

    # Split the adjusted text into lines, then into words to check the total count
    lines = adjusted_prompt_text.split('\n')
    final_lines = []
    word_count = 0

    # Iterate through the lines in reverse order, accumulating words until the max limit
    for line in reversed(lines):
        line_word_count = len(line.split())
        if word_count + line_word_count <= max_words:
            final_lines.append(line)
            word_count += line_word_count
        else:
            break  # Stop if adding another line would exceed the word limit

    # Since we iterated in reverse and appended to final_lines, reverse it to maintain original order
    final_lines.reverse()

    # Join the lines back into a string, preserving the lines
    final_text = '\n'.join(final_lines)


    # Generate text with the adjusted prompt
    response = llm(
        final_text,
        max_tokens=500,
        stop=["User:"],  # Adjust the stop token as needed
    )
    if response.get('choices'):
        generated_content = response['choices'][0].get('text', '')  # Extract the generated text

        # Remove the input text (last 500 words prompt) from the generated text
        if generated_content.startswith(prompt_text):
            # Remove the prompt text from the beginning of the generated_content
            generated_text = generated_content[len(prompt_text):].strip()
        else:
            generated_text = generated_content
    print(repr(generated_content))  # Use repr to make newline characters visible
    # Signal the animation thread to stop and wait for it to finish
    stop_event.set()
    animation_thread.join()

    thinking = False
    return generated_text

# Example: Copy text standardize it then paste it
def copy_and_paste_standardized_text():

    time.sleep(1)

    # Select all text
    pyautogui.hotkey('ctrl', 'a')  # For Windows/Linux
    
    # Wait a bit for the clipboard to register
    time.sleep(1)
    
    # Copy the selected text to clipboard
    pyautogui.hotkey('ctrl', 'c')  # For Windows/Linux
    # pyautogui.hotkey('command', 'c')  # For MacOS

    # Wait a bit for the clipboard to register
    time.sleep(1)

    # Get the text from clipboard
    copied_text = pyperclip.paste()

    # Standardize the text using OpenAI
    standardized_text = standardize_text(copied_text)

    # Copy the standardized text back to clipboard
    pyperclip.copy(standardized_text)
    pyautogui.hotkey('right')
    # Paste the text back where you need it
    pyautogui.hotkey('ctrl', 'v')  # For Windows/Linux
    # pyautogui.hotkey('command', 'v')  # For MacOS    

# Example: insert text by copying it to the clipboard then pasting it
def insert_text(text_to_insert):
    pyperclip.copy(text_to_insert)
    pyautogui.hotkey('ctrl', 'v')  # For Windows/Linux
    # pyautogui.hotkey('command', 'v')  # For MacOS
    
    

# Paths where Notepad++ is typically installed
possible_paths = [
    r"C:\Program Files\Notepad++\notepad++.exe",
    r"C:\Program Files (x86)\Notepad++\notepad++.exe"
]

# Check if Notepad++ is installed by looking for its executable
notepad_plus_plus_installed = any(os.path.exists(path) for path in possible_paths)

# Open Run dialog
pyautogui.hotkey('win', 'r')
pyautogui.sleep(1)  # Wait for the Run dialog to open

# Optional: a delay between each character in seconds
delay_between_characters = 0.1

if notepad_plus_plus_installed:
    # Typing out "Notepad++" one letter at a time
    pyautogui.typewrite("Notepad++", interval=delay_between_characters)
else:
    # Typing out "Notepad" one letter at a time
    pyautogui.typewrite("Notepad", interval=delay_between_characters)


pyautogui.hotkey('enter')  # For Windows/Linux
time.sleep(1)
pyautogui.hotkey('ctrl', 'n')  # For Windows/Linux

def new_install():
    pyautogui.typewrite(r"""Hello, this is the talking notepad. 

    A small demonstration project that shows off the possibilities of local LLMs that are as intergrated as hitting a hotkey on ur keyboard.

    If you understand please press the Right Shift key on your keyboard.""", 0.05)


    keyboard.wait('right shift')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')  # For Windows/Linux
    pyautogui.hotkey('backspace')  # For Windows/Linux

    pyautogui.typewrite(r"""The model in use is fintuned specifically for use in chat applications but has further capabilities. Honestly,
    you could use this same application to complete any text on screen.

    Do be cautious. Use beyond this demonstration is not the intended purpose of this application.

    Use of this application does not hold me responsable for missuse.
    View the popup on ur bar below if it did not apear.
    """, 0.01)

    import ctypes
    from ctypes import wintypes, windll
    import re

    # Setup for user32 functions
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    # MessageBox setup
    MessageBox = user32.MessageBoxW
    MessageBox.argtypes = (wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT)
    MessageBox.restype = wintypes.INT

    # SetForegroundWindow setup
    SetForegroundWindow = user32.SetForegroundWindow
    SetForegroundWindow.argtypes = [wintypes.HWND]
    SetForegroundWindow.restype = wintypes.BOOL

    # EnumWindows setup
    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
    EnumWindows.restype = wintypes.BOOL

    # Additional function prototypes
    GetWindowTextLength = user32.GetWindowTextLengthW
    GetWindowText = user32.GetWindowTextW
    GetWindowTextLength.argtypes = [wintypes.HWND]
    GetWindowText.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]

    def foreach_window(hwnd, lParam):
        length = GetWindowTextLength(hwnd) + 1  # Plus null terminator
        buffer = ctypes.create_unicode_buffer(length)
        GetWindowText(hwnd, buffer, length)
        if re.search(r'Notepad', buffer.value, re.IGNORECASE):
            matching_windows.append(hwnd)
        return True

    # MessageBox parameters
    MB_YESNO = 0x04
    MB_ICONQUESTION = 0x20
    IDYES = 6
    title = "Agree or Disagree"
    text = r"""I, the user of this program, do not hold reponsible the creator of the program for my missuse.
    Do you agree?"""
    response = MessageBox(0, text, title, MB_YESNO | MB_ICONQUESTION)

    if response == IDYES:
        print("User agreed.")
        matching_windows = []
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        if matching_windows:
            SetForegroundWindow(matching_windows[0])
            print("Notepad window focused.")
        else:
            print("No Notepad windows found.")
    else:
        print("User disagreed.")

    text = r"""I, the user of this program, do not hold reponsible the creator of the program for my missuse.
    Do you agree?"""
    time.sleep(1)
    pyautogui.typewrite(r"""
    Thank you. You can exit out of this app at any time by pressing the ESC key on your keyboard to close the application.

    To complete a message press END key to allow the AI to respond or autocomplete your text.

    This message will self delete in.
    """, 0.02)


    # Starting number for the countdown
    start_number = 9

    # Time to wait between typing numbers (in seconds)
    wait_time = 1

    for number in range(start_number, -1, -1):  # Countdown to 0
        pyautogui.write(str(number))  # Type the current number
        time.sleep(wait_time)  # Wait for the specified time
        if number > 0:  # If this is not the last number
            pyautogui.press('backspace')  # Press backspace to delete the number


    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')  # For Windows/Linux
    pyautogui.hotkey('backspace')  # For Windows/Linux



# Define the filename
filename = 'Agreed.txt'

# Check if the file exists in the same directory as the program
if not os.path.exists(filename):
    # The file doesn't exist, create it by opening in append mode and immediately closing
    with open(filename, 'a') as f:
        pass  # You don't need to write anything, just create the file
    new_install()
    print(f"'{filename}' has been created.")
else:
    print(f"'{filename}' already exists.")

# Set up the hotkey for the ESC key
keyboard.add_hotkey('end', copy_and_paste_standardized_text)
pyautogui.typewrite("""Death:Welcome to my domain.\nUser:It is a pleasure sir death. For what do I owe the pleasure?\nDeath:I wish to speak on a important matter.\nUser:Do pray tell.\nDeath:Have you heard of a thing called Ephoria?\nUser:""", 0.002)
keyboard.wait('esc')
