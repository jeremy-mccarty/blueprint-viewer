import pyperclip

def copy_to_clipboard(text: str):
    pyperclip.copy(text)

def paste_from_clipboard() -> str:
    return pyperclip.paste()