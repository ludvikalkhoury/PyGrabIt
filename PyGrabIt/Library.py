import os 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser

from PIL import Image, ImageTk, ImageDraw

class COLORS:
	def __enter__( self ):
		os.system('')
	def __exit__( self, *blah ):
		try: from colorama import Fore; print( Fore.WHITE + '\n' )
		except: pass
COLORS = COLORS()

class GraphGrabberApp:
	version = "0.0.11"
	
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

		self.view_point_button = tk.Button(self.frame, text="View Points", command=self.view_points)
		self.view_point_button.pack(side=tk.LEFT, padx=5)
		
		self.save_button = tk.Button(self.frame, text="Save Points", command=self.save_points)
		self.save_button.pack(side=tk.LEFT, padx=5)
		
		self.reset_button = tk.Button(self.frame, text="Reset Points", command=self.reset_points)
		self.reset_button.pack(side=tk.LEFT, padx=5)
		
		self.reset_calibration_button = tk.Button(self.frame, text="Reset Calibration", command=self.reset_calibration_button)
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


		# Add a window to create detect curves by choosing from a color pannel
		self.color_capture_button = tk.Button(self.frame3, text="Color Panel", command=self.select_color)
		self.color_capture_button.pack(side=tk.LEFT, padx=5, pady=5)
		
		# Add a window to create detect curves by clicking on the wanted color colors
		self.color_capture_button = tk.Button(self.frame3, text="Auto Detect", command=self.click_desired_color)
		self.color_capture_button.pack(side=tk.LEFT, padx=5, pady=5)
		
		# Add a window to create detect curves by clicking on the wanted color colors
		self.data_fit_button = tk.Button(self.frame3, text="Fit Data", command=self.fit_data)
		self.data_fit_button.pack(side=tk.LEFT, padx=5, pady=5)
		
		self.frame4 = tk.Frame(root)
		self.frame4.pack(side=tk.RIGHT, fill=tk.X, padx=3, pady=0)
		self.bottom_text_label = tk.Label(self.frame4, text="Version  "+str(self.version), font=("Helvetica", 8, "bold"), fg="#006400", anchor="e")
		self.bottom_text_label.pack()

		
		self.image = None
		self.points = []
		self.axis_points = {}
		self.axis_ranges_set = False

		# Create a separate window to display points
		self.points_window = None
		self.points_canvas = None
	
	
	
	def view_points(self):
		# Validate axis points
		if len(self.axis_points) < 4:
			self.show_error("Please click on all four axis points and assign values first.", is_error=True)
			return

		# Validate points
		if not self.points:
			self.show_error("No points to view.", is_error=True)
			return

		# Create the points window if not already open
		if not (self.points_window and self.points_window.winfo_exists()):
			self.points_window = tk.Toplevel(self.root)
			self.points_window.title("Captured Points")

		# Create or refresh points view
		self.create_points_view(self.points_window)

	def create_points_view(self, points_window):
		# Set up the frame for displaying points
		points_frame = tk.Frame(points_window)
		points_frame.pack(padx=10, pady=10)

		# Header for points table
		header = tk.Label(points_frame, text="Graph X\tGraph Y", font=("Helvetica", 12, "bold"))
		header.grid(row=0, column=0, padx=5, pady=5)
		
		try:
			# Assuming axis values are already assigned to self.x0, self.xmax, self.y0, self.ymax
			x0 = float(self.x0_entry.get())
			xmax = float(self.xmax_entry.get())
			y0 = float(self.y0_entry.get())
			ymax = float(self.ymax_entry.get())
		except ValueError:
			self.show_error("Invalid axis values. Please enter valid numbers for X0, Xmax, Y0, and Ymax.", is_error=True)
			
		# Display the captured points
		for i, (x, y, _) in enumerate(self.points, 1):
			calib_x0, _ = self.axis_points["X0"]
			calib_xmax, _ = self.axis_points["Xmax"]
			_, calib_y0 = self.axis_points["Y0"]
			_, calib_ymax = self.axis_points["Ymax"]

			graph_x = x0 + ((x - calib_x0) / (calib_xmax - calib_x0)) * (xmax - x0)
			graph_y = y0 + ((y - calib_y0) / (calib_ymax - calib_y0)) * (ymax - y0)

			point_label = tk.Label(points_frame, text=f"{graph_x:.4f}\t{graph_y:.4f}")
			point_label.grid(row=i, column=0, padx=5, pady=5)

		# Add a close button if not already present
		close_button = tk.Button(points_window, text="Close", command=points_window.destroy)
		close_button.pack(pady=10)
		



	def update_view_points(self):
		# Check if the points window exists and is open
		if self.points_window and self.points_window.winfo_exists():
			# Clear the current content of the points window
			for widget in self.points_window.winfo_children():
				widget.destroy()

			# Recreate the points view inside the existing window
			self.create_points_view(self.points_window)


	def perform_fit(self):
		import numpy as np
		import matplotlib.pyplot as plt
		
		if self.points and len(self.axis_points) == 4:
			try:
				# Get axis calibration values
				x0_graph = float(self.x0_entry.get())
				xmax_graph = float(self.xmax_entry.get())
				y0_graph = float(self.y0_entry.get())
				ymax_graph = float(self.ymax_entry.get())
			except ValueError:
				self.show_error("Invalid axis values. Please enter valid numbers for X0, Xmax, Y0, and Ymax.", is_error=True)
				return

			# Extract pixel coordinates of the axis calibration points
			x0_pixel, _ = self.axis_points['X0']
			xmax_pixel, _ = self.axis_points['Xmax']
			_, y0_pixel = self.axis_points['Y0']  # Access only the Y component for Y0
			_, ymax_pixel = self.axis_points['Ymax']  # Access only the Y component for Ymax

			# Convert pixel coordinates to graph coordinates
			x_data = []
			y_data = []
			
			for x_pixel, y_pixel, _ in self.points:
				# Transform pixel coordinates to graph coordinates
				x_graph = x0_graph + ((x_pixel - x0_pixel) / (xmax_pixel - x0_pixel)) * (xmax_graph - x0_graph)
				y_graph = y0_graph + ((y_pixel - y0_pixel) / (ymax_pixel - y0_pixel)) * (ymax_graph - y0_graph)
				x_data.append(x_graph)
				y_data.append(y_graph)
			
			# Get the selected polynomial degree
			degree = int(self.degree_var.get())
			
			# Fit the data with a polynomial of the selected degree
			coefficients = np.polyfit(x_data, y_data, degree)
			polynomial = np.poly1d(coefficients)
			
			# Generate x values for plotting the polynomial
			x_fit = np.linspace(min(x_data), max(x_data), 500)
			y_fit = polynomial(x_fit)

			# Calculate the predicted values for x_data and the RMSE
			y_pred = polynomial(x_data)
			rmse = np.sqrt(np.mean((np.array(y_data) - np.array(y_pred))**2))
			
			# Generate the polynomial equation in LaTeX format
			equation_parts = [f"{coeff:.3f}x^{{{deg}}}" if deg > 1 else (f"{coeff:.3f}x" if deg == 1 else f"{coeff:.3f}")
						  for coeff, deg in zip(coefficients, range(degree, -1, -1))]
		
			# Group the terms into lines of 6 terms each
			equation_lines = [" + ".join(equation_parts[i:i + 6]) for i in range(0, len(equation_parts), 6)]
			equation = "y = " + "\n".join(equation_lines)
			
			# Create a new window to display the equation and RMSE
			result_window = tk.Toplevel(self.root)
			result_window.title("Fitted Equation and RMSE")
			
			# Create a label to display the equation
			equation_label = tk.Label(result_window, text=f"Fitted Polynomial Equation:\n{equation}", font=("Helvetica", 12))
			equation_label.pack(pady=10)
			
			# Create a label to display the RMSE
			rmse_label = tk.Label(result_window, text=f"Root Mean Squared Error (RMSE): {rmse:.4f}", font=("Helvetica", 12))
			rmse_label.pack(pady=10)
			
			# Add an OK button to close the window
			ok_button = tk.Button(result_window, text="OK", command=result_window.destroy)
			ok_button.pack(pady=10)
			
			# Plot the data and the polynomial fit
			plt.figure()
			plt.plot(x_data, y_data, 'bo', label='Captured Points (Graph Coordinates)')
			plt.plot(x_fit, y_fit, 'r-', label=f'{degree}-Degree Polynomial Fit')
			plt.xlabel('X (Graph Coordinates)')
			plt.ylabel('Y (Graph Coordinates)')
			plt.title(f'{degree}-Degree Polynomial Fit')
			plt.legend()
			plt.show()

		else:
			self.show_error("No points or calibration points detected.", is_error=True)









	
	def fit_data(self):
		if self.image:
			self.data_fit_window = tk.Toplevel(self.root)
			self.data_fit_window.title("Fit data")
			
			#self.fitting_models = tk.Label(self.data_fit_window, text="Coming soon...")
			#self.fitting_models.pack(side=tk.LEFT, padx=5, pady=5)
			
			##
			tk.Label(self.data_fit_window, text="Select polynomial degree:").pack(side=tk.LEFT, padx=5, pady=5)
			self.degree_var = tk.StringVar(value="1")
			self.degree_entry = tk.Entry(self.data_fit_window, textvariable=self.degree_var)
			self.degree_entry.pack(side=tk.LEFT, padx=5, pady=5)
		
			self.fit_button = tk.Button(self.data_fit_window, text="Fit Data", command=self.perform_fit)
			self.fit_button.pack(side=tk.LEFT, padx=5, pady=5)
			##

		else:
			self.show_error("Please load an image first.", is_error=True)
			
			
	
	def click_desired_color(self):
		# Activate color selection mode from the image
		if self.image:
			self.show_error("Click on the image to pick a color.", is_error=False)
			self.canvas.bind("<Button-1>", self.pick_color_from_image)
		else:
			self.show_error("Please load an image first.", is_error=True)
	
	
	def pick_color_from_image(self, event):
		# Get the color from the clicked pixel
		x, y = event.x, event.y
		
		pixel_color = self.image.getpixel((x, y))
		if len(pixel_color) == 4:
			pixel_color = pixel_color[:3]
		
		self.selected_color = pixel_color  # Store the selected color (RGB)

		# Display the selected color
		self.show_selected_color()

		# Unbind the pick color function
		self.canvas.unbind("<Button-1>")
		


	def select_color(self):
		
		if self.image:
			# Open color picker dialog
			color = colorchooser.askcolor(title="Choose a color")

			if color[1] is not None:
				self.selected_color = color[0]  # Store the selected color (RGB)
				self.show_selected_color()	
				
		else:
			self.show_error("Please load an image first.", is_error=True)
			
			
		
	def auto_capture(self):
		# Remove all previous points
		points_copy = self.points[:]
		for px, py, point_id in points_copy:
			self.canvas.delete(point_id)  # Remove the point from the canvas
			self.points.remove((px, py, point_id))  # Remove the point from the list

		if not hasattr(self, 'selected_color') or self.selected_color is None:
			print("No color selected.")
			return

		# Get the selected color
		target_color = self.selected_color

		# Convert the selected color to a format suitable for comparison
		target_r, target_g, target_b = target_color

		# Create a copy of the image to work with
		image_copy = self.image.copy()
		width, height = image_copy.size

		# Define a threshold for color similarity
		color_threshold = self.color_threshold_slider.get()  # Adjust this threshold as needed

		# Define DeltaX and DeltaY
		DeltaX = int(self.Deltax_entry.get())  # Adjust this value as needed
		DeltaY = int(self.Deltay_entry.get())  # Adjust this value as needed
		

		
		# Initialize the last captured point position
		last_captured_x = -DeltaX
		last_captured_y = -DeltaY

		# Scan through all pixels in the image
		for x in range(0, width, DeltaX):  # Increment x by DeltaX
			for y in range(0, height, DeltaY):  # Increment y by DeltaY
				pixel = image_copy.getpixel((x, y))

				if isinstance(pixel, tuple):
					r, g, b = pixel[:3]

					# Calculate the color difference
					color_diff = abs(r - target_r) + abs(g - target_g) + abs(b - target_b)

					# If the color difference is within the threshold, and the point is sufficiently separated, draw a red point
					if color_diff < color_threshold:
						if (abs(x - last_captured_x) >= DeltaX) or (abs(y - last_captured_y) >= DeltaY):
							point_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red", tags="point")
							self.points.append((x, y, point_id))

							# Update the last captured point position
							last_captured_x = x
							last_captured_y = y



		
		
	def show_selected_color(self):
		# Display the selected color in a new window
		self.selected_color_window = tk.Toplevel(self.root)
		self.selected_color_window.title("Selected Color")

		# Create a canvas to display the selected color
		color_canvas = tk.Canvas(self.selected_color_window, width=100, height=100, bg=self.rgb_to_hex(self.selected_color))
		color_canvas.pack(pady=20)
		
		
		 # Color threshold slider
		self.color_threshold_label = tk.Label(self.selected_color_window, text="Color Threshold:")
		self.color_threshold_label.pack(side=tk.TOP, padx=5, pady=0)
		self.color_threshold_slider = tk.Scale(self.selected_color_window, from_=0, to_=255, orient=tk.HORIZONTAL)
		self.color_threshold_slider.set(50)  # Set initial value
		self.color_threshold_slider.pack(side=tk.TOP, padx=5, pady=5)
		
		
		# Delta X label and entry
		self.Deltax_label = tk.Label(self.selected_color_window, text="Δ X:")
		self.Deltax_label.pack(side=tk.LEFT, padx=5, pady=5)
		self.Deltax_entry = tk.Entry(self.selected_color_window, width=5)
		self.Deltax_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.Deltax_entry.insert(0, "1")  # Insert default value of 5
		
		# Delta Y label and entry
		self.Deltay_label = tk.Label(self.selected_color_window, text="Δ Y:")
		self.Deltay_label.pack(side=tk.LEFT, padx=5, pady=5)
		self.Deltay_entry = tk.Entry(self.selected_color_window, width=5)
		self.Deltay_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.Deltay_entry.insert(0, "1")  # Insert default value of 5
		
		# Auto Capture button
		self.auto_capture_button = tk.Button(self.selected_color_window, text="Capture", command=self.auto_capture)
		self.auto_capture_button.pack(side=tk.LEFT, padx=5)
				
		
		
		
	@staticmethod
	def rgb_to_hex(rgb):
		# Convert RGB tuple to HEX format
		return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


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
			
			# Create magnifier window
			#if self.magnifier_window is None:
			#	self.create_magnifier_window()
				
				


	def on_right_click(self, event):
		x, y = event.x, event.y
		self.remove_point(x, y)
		
	def create_magnifier_window(self):
		if self.image:
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
		
		else:
			self.show_error("Please load an image first.", is_error=True)
			
		

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

					for (x, y, id_points) in self.points:
						# Convert pixel coordinates to graph coordinates
						#graph_x = x0 + (x / self.tk_image.width()) * (xmax - x0)
						#graph_y = y0 + ((self.tk_image.height() - y) / self.tk_image.height()) * (ymax - y0)
						calib_x0, _ = self.axis_points['X0']
						calib_xmax, _ = self.axis_points['Xmax']
						_, calib_y0 = self.axis_points['Y0']  # Access only the Y component for Y0
						_, calib_ymax = self.axis_points['Ymax']  # Access only the Y component for Ymax
						
						graph_x = x0 + ((x - calib_x0) / (calib_xmax - calib_x0)) * (xmax - x0)
						graph_y = y0 + ((y - calib_y0) / (calib_ymax - calib_y0)) * (ymax - y0)

						
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
				point_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red", tags="point")
				self.points.append((x, y, point_id))
				

					
				if self.points_window is None:
					self.show_points_window()
				
				## Draw the point on the secondary window as well
				#if self.points_window:
				#	self.points_canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red", tags="point")
		
		# Refresh the points view window
		self.update_view_points()
	
	

	def remove_point(self, x, y):
		# Make a copy of the points list to avoid modifying it while iterating
		points_copy = self.points[:]
		for px, py, point_id in points_copy:
			if abs(px - x) < 5 and abs(py - y) < 5:  # Check if click is near the point
				self.canvas.delete(point_id)  # Remove the point from the canvas
				self.points.remove((px, py, point_id))  # Remove the point from the list
				break
				
	def reset_points(self):
		# Clear the points list and remove drawn red points from the main canvas
		self.points = []
		# Delete all items with tag "point" from the main canvas
		self.canvas.delete("point")  

		# If the points window exists, clear it and reset its state
		if self.points_window:
			self.points_window.destroy()  # Destroy the points window
			self.points_window = None  # Reset the reference to None
			
			# Check if points_canvas exists and clear it
			if hasattr(self, 'points_canvas') and self.points_canvas:
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
		a = 1
		'''
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
		'''

	def on_mouse_move(self, event):
		x, y = event.x, event.y
		self.canvas.delete(self.h_line)
		self.canvas.delete(self.v_line)
		self.h_line = self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill='gray', dash=(2, 2))
		self.v_line = self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill='gray', dash=(2, 2))
		
		if self.image and self.magnifier_window:
			self.update_magnifier(event.x, event.y)

	def hide_cursor(self, event):
		self.canvas.config(cursor="none")

	def show_cursor(self, event):
		self.canvas.config(cursor="")
		
	
	def update_magnifier(self, x, y):
		zoom_factor = self.zoom_factor
		magnifier_size = self.magnifier_size
		
		x_min = max(0, x - magnifier_size // 2 // zoom_factor)
		y_min = max(0, y - magnifier_size // 2 // zoom_factor)
		x_max = min(self.image.width, x_min + magnifier_size // zoom_factor)
		y_max = min(self.image.height, y_min + magnifier_size // zoom_factor)
		
		
		
		zoomed_image = self.image.crop((x_min, y_min, x_max, y_max)).resize((magnifier_size, magnifier_size), Image.LANCZOS)
		self.tk_zoomed_image = ImageTk.PhotoImage(zoomed_image)
		
		self.magnifier_canvas.delete("all")
		self.magnifier_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_zoomed_image)



	
		# Draw horizontal and vertical lines in the middle of the magnifier
		center_x = magnifier_size // 2
		center_y = magnifier_size // 2
		line_color = "black"  # Choose a color for the lines

		self.magnifier_canvas.create_line(0, center_y, magnifier_size, center_y, fill=line_color, dash=(2, 2))
		self.magnifier_canvas.create_line(center_x, 0, center_x, magnifier_size, fill=line_color, dash=(2, 2))
	
		# Draw captured points on the magnifier canvas
		if self.points:
			for (px, py, point_id) in self.points:
				# Transform points to magnifier coordinates
				mag_x = (px - x_min) * magnifier_size // (x_max - x_min)
				mag_y = (py - y_min) * magnifier_size // (y_max - y_min)
				self.magnifier_canvas.create_oval(mag_x-2, mag_y-2, mag_x+2, mag_y+2, outline="red", fill="red", tags="point")
			
	
		# Draw calibration points on the magnifier canvas
		if self.axis_points:
			for label, (px, py) in self.axis_points.items():
				# Transform points to magnifier coordinates
				mag_x = (px - x_min) * magnifier_size // (x_max - x_min)
				mag_y = (py - y_min) * magnifier_size // (y_max - y_min)
				color = "blue" if label == 'X0' else "green" if label == 'Xmax' else "yellow" if label == 'Y0' else "orange"
				self.magnifier_canvas.create_oval(mag_x-4, mag_y-4, mag_x+4, mag_y+4, outline=color, fill=color, tags="axis")
				self.magnifier_canvas.create_text(mag_x, mag_y-10, text=label, fill=color, tags="axis")
		
		


	def update_zoom_factor(self, value):
		self.zoom_factor = int(value)
		if self.magnifier_canvas:
			# Trigger a redraw of the magnifier with the new zoom factor
			self.update_magnifier(self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(), self.canvas.winfo_pointery() - self.canvas.winfo_rooty())

		#self.update_magnifier(self.canvas.winfo_pointerx(), self.canvas.winfo_pointery())

	def update_magnifier_size(self, value):
		self.magnifier_size = int(value)
		self.magnifier_canvas.config(width=self.magnifier_size, height=self.magnifier_size)
		self.update_magnifier(self.canvas.winfo_pointerx(), self.canvas.winfo_pointery())


if __name__ == "__main__":
	root = tk.Tk()
	app = GraphGrabberApp(root)
	root.mainloop()
