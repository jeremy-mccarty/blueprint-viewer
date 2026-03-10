import tkinter as tk


class HomeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

    def log(self, message):
        self.log_text_area.configure(state="normal")
        self.log_text_area.insert(tk.END, message + "\n")
        self.log_text_area.see(tk.END)
        self.log_text_area.configure(state="disabled")
