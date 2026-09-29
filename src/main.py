"""Точка входа: python src/main.py"""
import tkinter as tk

from config import parse_args
from gui import App
from shell import Shell


def main():
    """Разбирает параметры, создаёт окно и запускает эмулятор."""
    config = parse_args()
    shell = Shell(config)
    root = tk.Tk()
    App(root, shell)
    if shell.running:
        root.mainloop()
    else:
        root.destroy()


if __name__ == "__main__":
    main()
