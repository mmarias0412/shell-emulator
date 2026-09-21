"""Графический интерфейс эмулятора на tkinter."""
import tkinter as tk
from tkinter import scrolledtext

BG = "#1e1e1e"
FG = "#d4d4d4"
FONT = ("Courier New", 11)


class App:
    """Окно с областью вывода и строкой ввода."""

    def __init__(self, root, shell):
        self.root = root
        self.shell = shell
        root.title(shell.title())

        self.output = scrolledtext.ScrolledText(
            root, state="disabled", wrap="word", width=80, height=24,
            bg=BG, fg=FG, font=FONT,
        )
        self.output.pack(fill="both", expand=True)

        row = tk.Frame(root, bg=BG)
        row.pack(fill="x")
        tk.Label(
            row, text=shell.prompt(), bg=BG, fg="#6a9955", font=FONT
        ).pack(side="left")
        self.entry = tk.Entry(
            row, bg=BG, fg=FG, insertbackground=FG, font=FONT,
            relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

    def print(self, text):
        """Добавляет строку в область вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def on_enter(self, _event):
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.print(self.shell.prompt() + line)
        result = self.shell.execute(line)
        if result:
            self.print(result)
        if not self.shell.running:
            self.root.destroy()
