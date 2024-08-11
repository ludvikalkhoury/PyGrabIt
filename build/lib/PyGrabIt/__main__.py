"""
Command example:
python -m PyGrabIt

"""
import tkinter as tk
from .Library import GraphGrabberApp, COLORS

with COLORS:
	root = tk.Tk()
	app = GraphGrabberApp(root)
	root.mainloop()

