# Placeholder for helpers (if needed later)
def form_row(parent, label_text, widget):
    from tkinter import Label
    Label(parent, text=label_text).pack(side="left")
    widget.pack(side="left")