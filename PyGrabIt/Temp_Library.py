import tkinter as tk
from PIL import Image, ImageTk

class PyGrabIt:
	def __init__(self, root):
		self.root = root
		self.root.title("PyGrabIt")

		# Main window for canvas
		self.main_canvas_window = tk.Toplevel(self.root)
		self.main_canvas_window.title("Main Canvas")

		# Instructions and buttons in root window
		self.label = tk.Label(self.root, text="Click on X0 to set the origin point.", fg="blue")
		self.label.pack()

		self.open_button = tk.Button(self.root, text="Open Image", command=self.open_image)
		self.open_button.pack()

		self.magnifier_button = tk.Button(self.root, text="Open Magnifier", command=self.open_magnifier)
		self.magnifier_button.pack()

		# Canvas in a separate window
		self.canvas = tk.Canvas(self.main_canvas_window, cursor="cross")
		self.canvas.pack(fill=tk.BOTH, expand=True)

		self.canvas.bind("<Button-1>", self.set_point)
		self.canvas.bind("<Left>", self.move_left)
		self.canvas.bind("<Right>", self.move_right)
		self.canvas.bind("<Up>", self.move_up)
		self.canvas.bind("<Down>", self.move_down)
		self.canvas.focus_set()

		self.points = []
		self.image = None
		self.photo_image = None
		self.cursor_x = None
		self.cursor_y = None
		self.cursor_id = None

	def open_image(self):
		self.image = Image.open("path_to_your_image.jpg")  # Replace with your image path
		self.photo_image = ImageTk.PhotoImage(self.image)
		self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
		self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

	def set_point(self, event):
		x, y = event.x, event.y
		self.cursor_x, self.cursor_y = x, y
		self.points.append((x, y))
		self.update_cursor()

	def update_cursor(self):
		if self.cursor_id is not None:
			self.canvas.delete(self.cursor_id)
		self.cursor_id = self.canvas.create_line(self.cursor_x, self.cursor_y, self.cursor_x + 1, self.cursor_y, fill="red")

	def move_cursor(self, dx, dy):
		if self.cursor_x is not None and self.cursor_y is not None:
			self.cursor_x += dx
			self.cursor_y += dy
			self.update_cursor()

	def move_left(self, event):
		self.move_cursor(-1, 0)

	def move_right(self, event):
		self.move_cursor(1, 0)

	def move_up(self, event):
		self.move_cursor(0, -1)

	def move_down(self, event):
		self.move_cursor(0, 1)

	def open_magnifier(self):
		if self.image is not None:
			magnifier_window = tk.Toplevel(self.root)
			magnifier_window.title("Magnifier")
			magnifier_canvas = tk.Canvas(magnifier_window, width=200, height=200)
			magnifier_canvas.pack()

			def magnify(event):
				mx, my = event.x, event.y
				if self.cursor_x is not None and self.cursor_y is not None:
					x0 = max(0, self.cursor_x - 50)
					y0 = max(0, self.cursor_y - 50)
					x1 = min(self.image.width, self.cursor_x + 50)
					y1 = min(self.image.height, self.cursor_y + 50)

					zoomed_image = self.image.crop((x0, y0, x1, y1)).resize((200, 200))
					zoomed_photo = ImageTk.PhotoImage(zoomed_image)
					magnifier_canvas.create_image(0, 0, anchor=tk.NW, image=zoomed_photo)
					magnifier_canvas.image = zoomed_photo  # Keep a reference to avoid garbage collection

			magnifier_canvas.bind("<Motion>", magnify)

if __name__ == "__main__":
	root = tk.Tk()
	app = PyGrabIt(root)
	root.mainloop()
