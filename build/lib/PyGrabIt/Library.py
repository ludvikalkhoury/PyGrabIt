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
	Version = "0.0.7"
	
	def __init__(self, root):
		self.h_line = None
		self.v_line = None
		
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
				else:
					self.show_points_window()
			else:
				# Add point to the list and draw it
				self.points.append((x, y))
				self.canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red", tags="point")

				if self.points_window is None:
					self.show_points_window()
				
				# Draw the point on the secondary window as well
				if self.points_window:
					self.points_canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red", tags="point")


	def reset_points(self):
		# Clear the points list and remove drawn red points from the main canvas
		self.points = []
		self.canvas.delete("point")  # Delete all items with tag "point"

		# If the points window exists, also clear points there
		if self.points_window:
			self.points_canvas.delete("point")  # Delete all items with tag "point"

		# Clear any previous error messages
		self.error_label.config(text="")
		self.show_error("Point reset. Now click on new points to capture.", is_error=False)
		
	
	def reset_calibration_button(self):
		self.axis_points = {}
		self.axis_ranges_set = False

		# Clear axis markers on the main canvas
		self.canvas.delete("axis")

		# Clear axis markers on the secondary canvas if it exists
		if self.points_window:
			self.points_canvas.delete("axis")

		# Clear axis range entries
		self.x0_entry.delete(0, tk.END)
		self.xmax_entry.delete(0, tk.END)
		self.y0_entry.delete(0, tk.END)
		self.ymax_entry.delete(0, tk.END)
		
		self.show_error("Calibration reset. Click to set X0.", is_error=False)

		
		
		
		

	def show_points_window(self):
		if self.points_window is None:
			# Get the dimensions and position of the main window
			main_window_x = self.root.winfo_rootx()
			main_window_y = self.root.winfo_rooty()
			main_window_width = self.root.winfo_width()
			main_window_height = self.root.winfo_height()

			# Create a new window to show clicked points
			self.points_window = tk.Toplevel(self.root)
			self.points_window.title("Captured Points")
			
			# Create a blank canvas (no image) in the secondary window
			self.points_canvas = tk.Canvas(self.points_window, bg="white", width=self.tk_image.width(), height=self.tk_image.height())
			self.points_canvas.pack()

			# Draw the axis markers on the secondary canvas
			for label, (x, y) in self.axis_points.items():
				color = "blue" if label == 'X0' else "green" if label == 'Xmax' else "yellow" if label == 'Y0' else "orange"
				self.points_canvas.create_oval(x-4, y-4, x+4, y+4, outline=color, fill=color, tags="axis")
				self.points_canvas.create_text(x, y-10, text=label, fill=color, tags="axis")
			
			# Position the new window to the right of the main window
			new_window_x = main_window_x + main_window_width
			new_window_y = main_window_y
			self.points_window.geometry(f"{self.tk_image.width()}x{self.tk_image.height()}+{new_window_x}+{new_window_y}")


	def on_mouse_move(self, event):
		x, y = event.x, event.y
		self.canvas.delete(self.h_line)
		self.canvas.delete(self.v_line)
		self.h_line = self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill='gray', dash=(2, 2))
		self.v_line = self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill='gray', dash=(2, 2))

	def hide_cursor(self, event):
		self.canvas.config(cursor="none")

	def show_cursor(self, event):
		self.canvas.config(cursor="")
		


#if __name__ == "__main__":
#    root = tk.Tk()
#    app = GraphGrabberApp(root)
#    root.mainloop()
