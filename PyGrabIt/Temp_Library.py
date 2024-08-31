import os 
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class COLORS:
	def __enter__( self ):
		os.system('')
	def __exit__( self, *blah ):
		try: from colorama import Fore; print( Fore.WHITE + '\n' )
		except: pass
COLORS = COLORS()

class GraphGrabberApp:
	Version = "0.0.8"
	
	def __init__(self, root):
		self.h_line = None
		self.v_line = None
		self.magnifier_window = None
		self.magnifier_canvas = None
		
		self.root = root
		self.root.title("PyGrabIt")
		
		# Create a frame for instructions and buttons
		self.instruction_frame = tk.Frame(root)
		self.instruction_frame.pack(fill=tk.X, pady=10)

		# Instruction text
		self.instruction_label_bold = tk.Label(self.instruction_frame, text="Welcome to PyGrabIt! To start:", font=("Helvetica", 12, "bold"), pady=10)
		self.instruction_label_bold.pack()

		self.instruction_label = tk.Label(self.instruction_frame, text=(
			"1) Load an image\n"
			"2) Calibrate by clicking on the X and Y coordinates for the origin and maximum points\n"
			"3) Enter the X and Y values of the origin and maximum point\n"
			"4) Click on the points you want to capture\n"
			"5) Save the points you captured as a .txt file"
		), pady=10, justify=tk.LEFT)
		self.instruction_label.pack()

		# Error message label
		self.error_label = tk.Label(root, text="", fg="red", font=("Helvetica", 10))
		self.error_label.pack(pady=5)

		# Create the canvas and control buttons
		self.canvas = tk.Canvas(root, bg="white")
		self.canvas.pack(fill=tk.BOTH, expand=True)
		
		self.canvas.bind("<Motion>", self.on_mouse_move)
		self.canvas.bind("<Enter>", self.hide_cursor)
		self.canvas.bind("<Leave>", self.show_cursor)

		self.frame = tk.Frame(root)
		self.frame.pack(fill=tk.X)
		
		self.load_button = tk.Button(self.frame, text="Load Image", command=self.load_image)
		self.load_button.pack(side=tk.LEFT, padx=5)

		self.save_button = tk.Button(self.frame, text="Save Points", command=self.save_points)
		self.save_button.pack(side=tk.LEFT, padx=5)
		
		self.reset_button = tk.Button(self.frame, text="Reset Points", command=self.reset_points)
		self.reset_button.pack(side=tk.LEFT, padx=5)
		
		self.reset_calibration_button = tk.Button(self.frame, text="Reset Calibration", command=self.reset_calibration_button)
		self.reset_calibration_button.pack(side=tk.LEFT, padx=5)

		self.x0_label = tk.Label(self.frame, text="X0:")
		self.x0_label.pack(side=tk.LEFT, padx=5)
		self.x0_entry = tk.Entry(self.frame, width=5)
		self.x0_entry.pack(side=tk.LEFT, padx=5)

		self.xmax_label = tk.Label(self.frame, text="Xmax:")
		self.xmax_label.pack(side=tk.LEFT, padx=5)
		self.xmax_entry = tk.Entry(self.frame, width=5)
		self.xmax_entry.pack(side=tk.LEFT, padx=5)

		self.y0_label = tk.Label(self.frame, text="Y0:")
		self.y0_label.pack(side=tk.LEFT, padx=5)
		self.y0_entry = tk.Entry(self.frame, width=5)
		self.y0_entry.pack(side=tk.LEFT, padx=5)

		self.ymax_label = tk.Label(self.frame, text="Ymax:")
		self.ymax_label.pack(side=tk.LEFT, padx=5)
		self.ymax_entry = tk.Entry(self.frame, width=5)
		self.ymax_entry.pack(side=tk.LEFT, padx=5)

		self.canvas.bind("<Button-1>", self.on_click)
		self.canvas.bind("<Motion>", self.on_mouse_move)

		self.image = None
		self.points = []
		self.axis_points = {}
		self.axis_ranges_set = False

		# Create a separate window to display points
		self.points_window = None
		self.points_canvas = None

	def load_image(self):
		file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
		if file_path:
			self.image = Image.open(file_path)
			self.tk_image = ImageTk.PhotoImage(self.image)
			self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
			self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

			self.axis_points = {}  # Reset axis points when a new image is loaded
			self.axis_ranges_set = False

			# Clear any previous error messages
			self.error_label.config(text="")

			# Show the message to click on X0
			self.show_error("Click on X0 to set the origin point.", is_error=False)

			# Create magnifier window
			if self.magnifier_window is None:
				self.create_magnifier_window()

	def create_magnifier_window(self):
		self.magnifier_window = tk.Toplevel(self.root)
		self.magnifier_window.title("Magnifier")
		self.magnifier_canvas = tk.Canvas(self.magnifier_window, width=200, height=200)
		self.magnifier_canvas.pack()

	def save_points(self):
		if len(self.axis_points) < 4:
			self.show_error("Please click on all four axis points and assign values first.", is_error=True)
			return

		try:
			x0 = float(self.x0_entry.get())
			xmax = float(self.xmax_entry.get())
			y0 = float(self.y0_entry.get())
			ymax = float(self.ymax_entry.get())
		except ValueError:
			self.show_error("Invalid axis values. Please enter valid numbers for X0, Xmax, Y0, and Ymax.", is_error=True)
			return

		# Clear error message if values are valid
		self.error_label.config(text="", fg="black")

		# Ask the user for the save location and filename
		file_path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
			title="Save Points As"
		)
		
		if file_path:
			try:
				with open(file_path, "w") as file:
					file.write("X Y\n")  # Write header labels

					for (x, y) in self.points:
						# Convert pixel coordinates to graph coordinates
						graph_x = x0 + (x / self.tk_image.width()) * (xmax - x0)
						graph_y = y0 + ((self.tk_image.height() - y) / self.tk_image.height()) * (ymax - y0)
						file.write(f"{graph_x:.4f} {graph_y:.4f}\n")
				
				self.show_error(f"Points saved to {file_path}", is_error=False)
			except Exception as e:
				self.show_error(f"Failed to save points: {str(e)}", is_error=True)

	def show_error(self, message, is_error=True):
		# Set the text color based on whether it is an error message
		color = "red" if is_error else "blue"
		self.error_label.config(text=message, fg=color)

	def on_click(self, event):
		if self.image:
			x = event.x
			y = event.y

			if not self.axis_ranges_set:
				if len(self.axis_points) < 4:
					if len(self.axis_points) == 0:
						label = 'X0'
						self.show_error("Click on Xmax.", is_error=False)
					elif len(self.axis_points) == 1:
						label = 'Xmax'
						self.show_error("Click on Y0.", is_error=False)
					elif len(self.axis_points) == 2:
						label = 'Y0'
						self.show_error("Click on Ymax.", is_error=False)
					elif len(self.axis_points) == 3:
						label = 'Ymax'
						self.axis_ranges_set = True
						self.show_error("Axis points set. Now click on the points to capture.", is_error=False)

					self.axis_points[label] = (x, y)
					color = "blue" if label == 'X0' else "green" if label == 'Xmax' else "yellow" if label == 'Y0' else "orange"
					self.canvas.create_oval(x-4, y-4, x+4, y+4, outline=color, fill=color, tags="axis")
					self.canvas.create_text(x, y-10, text=label, fill=color, tags="axis")
				return

			self.points.append((x, y))
			self.update_points_window()
			self.draw_crosshairs(x, y, length=10)

	def reset_points(self):
		self.points = []
		self.update_points_window()
		self.canvas.delete("point")

	def draw_crosshairs(self, x, y, length=10):
		self.canvas.create_line(x - length, y, x + length, y, fill="red", tags="point")
		self.canvas.create_line(x, y - length, x, y + length, fill="red", tags="point")

	def update_points_window(self):
		if self.points_window is None:
			self.points_window = tk.Toplevel(self.root)
			self.points_window.title("Captured Points")
			self.points_canvas = tk.Canvas(self.points_window, bg="white", width=300, height=200)
			self.points_canvas.pack()

		self.points_canvas.delete("point_text")
		for i, (x, y) in enumerate(self.points):
			text = f"{i+1}: ({x}, {y})"
			self.points_canvas.create_text(10, 10 + i * 20, anchor=tk.NW, text=text, tags="point_text")


	def on_mouse_move(self, event):
		if self.h_line and self.v_line:
			self.canvas.delete(self.h_line)
			self.canvas.delete(self.v_line)
		
		self.h_line = self.canvas.create_line(0, event.y, self.canvas.winfo_width(), event.y, fill="gray")
		self.v_line = self.canvas.create_line(event.x, 0, event.x, self.canvas.winfo_height(), fill="gray")
		
		if self.image and self.magnifier_window:
			self.update_magnifier(event.x, event.y)

	def update_magnifier(self, x, y):
		zoom_factor = 3
		magnifier_size = 100
		
		x_min = max(0, x - magnifier_size // 2 // zoom_factor)
		y_min = max(0, y - magnifier_size // 2 // zoom_factor)
		x_max = min(self.image.width, x_min + magnifier_size // zoom_factor)
		y_max = min(self.image.height, y_min + magnifier_size // zoom_factor)
		
		zoomed_image = self.image.crop((x_min, y_min, x_max, y_max)).resize((magnifier_size, magnifier_size), Image.LANCZOS)
		self.tk_zoomed_image = ImageTk.PhotoImage(zoomed_image)
		
		self.magnifier_canvas.delete("all")
		self.magnifier_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_zoomed_image)
	
	def hide_cursor(self, event):
		self.root.config(cursor="none")
	
	def show_cursor(self, event):
		self.root.config(cursor="")
	
	def reset_calibration_button(self):
		# Clear axis points and reset related flags and entries
		self.axis_points = {}
		self.axis_ranges_set = False
		self.canvas.delete("axis")  # Remove axis point markers from the canvas

		# Clear the axis entry fields
		self.x0_entry.delete(0, tk.END)
		self.xmax_entry.delete(0, tk.END)
		self.y0_entry.delete(0, tk.END)
		self.ymax_entry.delete(0, tk.END)

		# Show a message to guide the user to recalibrate
		self.show_error("Axis points reset. Click on X0 to set the origin point.", is_error=False)


if __name__ == "__main__":
	with COLORS:
		root = tk.Tk()
		app = GraphGrabberApp(root)
		root.mainloop()
