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
		self.zoom_factor = 5
		self.magnifier_size = 100
		
		# Main root
		self.root = root
		self.root.geometry("500x300")  # Set the size of the main window
		self.root.title("PyGrabIt")
		

		# Create a frame for instructions and buttons
		self.instruction_frame = tk.Frame(root)

		self.instruction_frame.pack(fill=tk.X, pady=10)

		# Instruction text
		self.instruction_label_bold = tk.Label(self.instruction_frame, text="Welcome to PyGrabIt! To start:", font=("Helvetica", 12, "bold"), pady=5)
		self.instruction_label_bold.pack()

		self.instruction_label = tk.Label(self.instruction_frame, text=(
			"1) Load an image\n"
			"2) Calibrate by clicking on the X and Y coordinates for the origin and maximum points\n"
			"3) Enter the X and Y values of the origin and maximum point\n"
			"4) Left click on the points you want to capture\n"
			"5) Right click on the points you want to delete\n"
			"6) Save the points you captured as a .txt file"
		), pady=5, justify=tk.LEFT)
		self.instruction_label.pack()
		
		# Error message label
		self.error_label = tk.Label(root, text="", fg="red", font=("Helvetica", 10))
		self.error_label.pack(pady=5)
		
		

		self.frame = tk.Frame(root)
		self.frame.pack(fill=tk.X)

		self.load_button = tk.Button(self.frame, text="Load Image", command=self.load_image)
		self.load_button.pack(side=tk.LEFT, padx=5)

		self.save_button = tk.Button(self.frame, text="Save Points", command=self.save_points)
		self.save_button.pack(side=tk.LEFT, padx=5)
		
		self.reset_button = tk.Button(self.frame, text="Reset Points", command=self.reset_points)
		self.reset_button.pack(side=tk.LEFT, padx=5)
		
		self.reset_calibration_button = tk.Button(self.frame, text="Reset Calibration", command=self.reset_calibration)
		self.reset_calibration_button.pack(side=tk.LEFT, padx=5)
		
		
		# Create a new frame for the buttons on the next line
		self.frame2 = tk.Frame(root)
		self.frame2.pack(fill=tk.X)
		
		self.x0_label = tk.Label(self.frame2, text="X0:")
		self.x0_label.pack(side=tk.LEFT, padx=5, pady=5)
		self.x0_entry = tk.Entry(self.frame2, width=5)
		self.x0_entry.pack(side=tk.LEFT, padx=5, pady=5)

		self.xmax_label = tk.Label(self.frame2, text="Xmax:")
		self.xmax_label.pack(side=tk.LEFT, padx=5)
		self.xmax_entry = tk.Entry(self.frame2, width=5)
		self.xmax_entry.pack(side=tk.LEFT, padx=5)

		self.y0_label = tk.Label(self.frame2, text="Y0:")
		self.y0_label.pack(side=tk.LEFT, padx=5, pady=5)
		self.y0_entry = tk.Entry(self.frame2, width=5)
		self.y0_entry.pack(side=tk.LEFT, padx=5, pady=5)

		self.ymax_label = tk.Label(self.frame2, text="Ymax:")
		self.ymax_label.pack(side=tk.LEFT, padx=5, pady=5)
		self.ymax_entry = tk.Entry(self.frame2, width=5)
		self.ymax_entry.pack(side=tk.LEFT, padx=5, pady=5)


		# Create a new frame for the buttons on the next line
		self.frame3 = tk.Frame(root)
		self.frame3.pack(fill=tk.X)
		self.magnifier_button = tk.Button(self.frame3, text="Open Magnifier", command=self.create_magnifier_window)
		self.magnifier_button.pack(side=tk.LEFT, padx=5, pady=5)


		# Add a window to create detect curves by colors
		self.color_capture_button = tk.Button(self.frame3, text="Auto Detect", command=self.apply_auto_detect)
		self.color_capture_button.pack(side=tk.LEFT, padx=5, pady=5)
		
		self.image = None
		self.points = []
		self.axis_points = {}
		self.axis_ranges_set = False

		# Create a separate window to display points
		self.points_window = None
		self.points_canvas = None
		
		
	


	def apply_auto_detect(self):
		if self.image:
			# Example logic to detect and mark colors automatically
			for x in range(0, self.tk_image.width(), 5):  # Adjust the step size as needed
				for y in range(0, self.tk_image.height(), 5):
					color = self.image.getpixel((x, y))  # Get pixel color
					
					# Define the color detection logic here
					# For example, detecting a specific shade of red
					if self.is_target_color(color):
						point_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red", tags="point")
						self.points.append((x, y, point_id))

	def is_target_color(self, color):
		if len(color) == 4:
			# RGBA format: discard the alpha channel
			r, g, b, _ = color
		elif len(color) == 3:
			# RGB format
			r, g, b = color
		else:
			raise ValueError("Unexpected color format")

		# Define your target color or range
		target_color = (255, 0, 0)  # Example target color (red)
		tolerance = 30  # Example tolerance

		# Check if the color matches the target color within the tolerance range
		return (
			abs(r - target_color[0]) <= tolerance and
			abs(g - target_color[1]) <= tolerance and
			abs(b - target_color[2]) <= tolerance
		)
	def load_image(self):
		file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
		if file_path:
			
			# Create a new window for the canvas
			self.canvas_window = tk.Toplevel(self.root)
			self.canvas_window.title("Image Canvas")
			self.canvas = tk.Canvas(self.canvas_window, bg="white")
			self.canvas.pack(fill=tk.BOTH, expand=True)
			
			self.canvas.bind("<Motion>", self.on_mouse_move)
			self.canvas.bind("<Enter>", self.hide_cursor)
			self.canvas.bind("<Leave>", self.show_cursor)
			self.canvas.bind("<Button-1>", self.on_click)
			self.canvas.bind("<Button-3>", self.on_right_click)

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
				
	def create_magnifier_window(self):
		self.magnifier_window = tk.Toplevel(self.root)
		self.magnifier_window.title("Magnifier")
		self.magnifier_canvas = tk.Canvas(self.magnifier_window, width=200, height=200)
		self.magnifier_canvas.pack()
		
		# Create sliders for zoom_factor and magnifier_size
		self.zoom_slider = tk.Scale(self.magnifier_window, from_=1, to=20, orient=tk.HORIZONTAL, label="Zoom Factor",
									command=self.update_zoom_factor)
		self.zoom_slider.set(self.zoom_factor)
		self.zoom_slider.pack(side=tk.LEFT, padx=5)

		self.size_slider = tk.Scale(self.magnifier_window, from_=50, to=400, orient=tk.HORIZONTAL, label="Magnifier Size",
									command=self.update_magnifier_size)
		self.size_slider.set(self.magnifier_size)
		self.size_slider.pack(side=tk.LEFT, padx=5)

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

		# Ask the user where they want to save the .txt file
		file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
		if file_path:
			with open(file_path, "w") as file:
				file.write(f"X0: {x0}\nXmax: {xmax}\nY0: {y0}\nYmax: {ymax}\n")
				file.write(f"X0: {self.axis_points['X0']}\nXmax: {self.axis_points['Xmax']}\nY0: {self.axis_points['Y0']}\nYmax: {self.axis_points['Ymax']}\n")
				file.write("Captured Points:\n")
				for point in self.points:
					file.write(f"{point[0]}, {point[1]}\n")

	def on_mouse_move(self, event):
		# Move horizontal and vertical lines with the cursor
		if self.h_line:
			self.canvas.delete(self.h_line)
		if self.v_line:
			self.canvas.delete(self.v_line)

		self.h_line = self.canvas.create_line(0, event.y, self.canvas.winfo_width(), event.y, fill="blue")
		self.v_line = self.canvas.create_line(event.x, 0, event.x, self.canvas.winfo_height(), fill="blue")

		# Update the magnifier window
		self.update_magnifier(event.x, event.y)
		
	def reset_points(self):
		self.points = []
		self.canvas.delete("point")
		self.canvas.delete("selected_point")
		if self.points_window:
			self.points_window.destroy()
		self.create_points_window()
		
	def reset_calibration(self):
		self.axis_points = {}
		self.axis_ranges_set = False
		self.canvas.delete("axis_point")

	def on_click(self, event):
		# Handle clicks for setting axis points or capturing points
		if len(self.axis_points) < 4:
			self.set_axis_point(event)
		else:
			self.capture_point(event)

	def set_axis_point(self, event):
		axis_order = ["X0", "Xmax", "Y0", "Ymax"]
		point_name = axis_order[len(self.axis_points)]
		point_id = self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, outline="blue", fill="blue", tags="axis_point")
		self.axis_points[point_name] = (event.x, event.y, point_id)

		if len(self.axis_points) < 4:
			self.show_error(f"Click on {axis_order[len(self.axis_points)]} to set the {point_name} point.", is_error=False)
		else:
			self.axis_ranges_set = True
			self.show_error("", is_error=False)  # Clear the message

		self.create_points_window()

	def capture_point(self, event):
		point_id = self.canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, outline="red", fill="red", tags="point")
		self.points.append((event.x, event.y, point_id))
		self.update_points_window()

	def on_right_click(self, event):
		# Detect and remove a clicked point
		closest_point = self.canvas.find_closest(event.x, event.y)[0]
		for i, (x, y, point_id) in enumerate(self.points):
			if point_id == closest_point:
				self.canvas.delete(point_id)
				del self.points[i]
				break
		self.update_points_window()

	def create_points_window(self):
		# Create a window to display the captured points
		if self.points_window:
			self.points_window.destroy()

		self.points_window = tk.Toplevel(self.root)
		self.points_window.title("Captured Points")
		self.points_canvas = tk.Canvas(self.points_window, width=300, height=200)
		self.points_canvas.pack()

		self.update_points_window()

	def update_points_window(self):
		# Update the points window with the current points
		if not self.points_window or not self.points_canvas:
			return

		self.points_canvas.delete("all")  # Clear the previous points

		for i, (x, y, _) in enumerate(self.points):
			self.points_canvas.create_text(10, 10 + i * 20, anchor=tk.NW, text=f"Point {i+1}: ({x}, {y})")

	def show_error(self, message, is_error=True):
		# Display an error or information message
		self.error_label.config(text=message, fg="red" if is_error else "blue")

	def update_zoom_factor(self, val):
		self.zoom_factor = int(val)

	def update_magnifier_size(self, val):
		self.magnifier_size = int(val)

	def update_magnifier(self, x, y):
		# Update the magnifier window
		if not self.magnifier_canvas or not self.image:
			return

		left = max(0, x - self.magnifier_size // 2)
		top = max(0, y - self.magnifier_size // 2)
		right = min(self.image.width, x + self.magnifier_size // 2)
		bottom = min(self.image.height, y + self.magnifier_size // 2)

		cropped_image = self.image.crop((left, top, right, bottom))
		resized_image = cropped_image.resize((self.magnifier_size * self.zoom_factor, self.magnifier_size * self.zoom_factor), Image.ANTIALIAS)
		tk_resized_image = ImageTk.PhotoImage(resized_image)

		self.magnifier_canvas.create_image(0, 0, anchor=tk.NW, image=tk_resized_image)
		self.magnifier_canvas.image = tk_resized_image  # Keep a reference to prevent garbage collection

	def hide_cursor(self, event):
		self.canvas.config(cursor="none")

	def show_cursor(self, event):
		self.canvas.config(cursor="arrow")


if __name__ == "__main__":
	with COLORS:
		root = tk.Tk()
		app = GraphGrabberApp(root)
		root.mainloop()
