import tkinter as tk
import sv_ttk
from app.views.blueprint_view import BlueprintView


def main():

    root = tk.Tk()
    sv_ttk.set_theme("dark")
    root.title("Blueprint Viewer")
    root.geometry("1100x750")

    # apply a dark background to the main window
    from app.config import style
    root.configure(bg=style.CANVAS_BG)

    view = BlueprintView(root)
    view.pack(fill="both", expand=True)

    # menu
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Clear Text", command=lambda: view.text.delete("1.0", tk.END))
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="File", menu=filemenu)

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo", command=lambda: view.text.edit_undo(), accelerator="Ctrl+Z")
    editmenu.add_command(label="Redo", command=lambda: view.text.edit_redo(), accelerator="Ctrl+Y")
    editmenu.add_separator()
    editmenu.add_command(label="Select All", command=lambda: view.text.tag_add("sel","1.0","end"), accelerator="Ctrl+A")
    menubar.add_cascade(label="Edit", menu=editmenu)

    root.config(menu=menubar)

    root.mainloop()


if __name__ == "__main__":
    main()