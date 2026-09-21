"""Точка входа: python src/main.py"""
import tkinter as tk

from gui import App
from shell import Shell


def main():
    root = tk.Tk()
    App(root, Shell())
    root.mainloop()


if __name__ == "__main__":
    main()
