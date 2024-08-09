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
	Version = "1.0.0"
	
	def __init__(self, root):
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

		self.frame = tk.Frame(root)
		self.frame.pack(fill=tk.X)

		self.load_button = tk.Button(self.frame, text="Load Image", command=self.load_image)
		self.load_button.pack(side=tk.LEFT, padx=5)

		self.save_button = tk.Button(self.frame, text="Save Points", command=self.save_points)
		self.save_button.pack(side=tk.LEFT, padx=5)

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

		self.image = None
		self.points = []
		self.axis_points = {}
		self.axis_ranges_set = False

		# Create a separate window to display points
		self.points_window = None
		self.points_canvas = None

	def load_image(self):
		file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
		if file_path:
			self.image = Image.open(file_path)
			self.tk_image = ImageTk.PhotoImage(self.image)
			self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
			self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

			self.axis_points = {}  # Reset axis points when a new image is loaded
			self.axis_ranges_set = False

			# Clear any previous error messages
			self.error_label.config(text="")

	def save_points(self):
		if len(self.axis_points) < 4:
			self.show_error("Please click on all four axis points and assign values first.")
			return

		try:
			x0 = float(self.x0_entry.get())
			xmax = float(self.xmax_entry.get())
			y0 = float(self.y0_entry.get())
			ymax = float(self.ymax_entry.get())
		except ValueError:
			self.show_error("Invalid axis values. Please enter valid numbers for X0, Xmax, Y0, and Ymax.")
			return

		# Clear error message if values are valid
		self.error_label.config(text="")

		# Ask the user for the save location and filename
		file_path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
			title="Save Points As"
		)
		
		if file_path:
			with open(file_path, "w") as file:
				file.write("X Y\n")  # Write header labels

				for (x, y) in self.points:
					# Convert pixel coordinates to graph coordinates
					graph_x = x0 + (x / self.tk_image.width()) * (xmax - x0)
					graph_y = y0 + ((self.tk_image.height() - y) / self.tk_image.height()) * (ymax - y0)
					file.write(f"{graph_x:.4f} {graph_y:.4f}\n")

			print(f"Points saved to {file_path}")
			

	def show_error(self, message):
		self.error_label.config(text=message)

	def on_click(self, event):
		if self.image:
			x = event.x
			y = event.y

			if not self.axis_ranges_set:
				if len(self.axis_points) < 4:
					if not self.axis_points:
						label = 'X0'
					elif len(self.axis_points) == 1:
						label = 'Xmax'
					elif len(self.axis_points) == 2:
						label = 'Y0'
					elif len(self.axis_points) == 3:
						label = 'Ymax'
						self.axis_ranges_set = True

					self.axis_points[label] = (x, y)
					color = "blue" if label == 'X0' else "green" if label == 'Xmax' else "yellow" if label == 'Y0' else "orange"
					self.canvas.create_oval(x-4, y-4, x+4, y+4, outline=color, fill=color)
					self.canvas.create_text(x, y-10, text=label, fill=color)
				else:
					print("Axis ranges are already set. Click on points to save.")
					self.show_points_window()
			else:
				self.points.append((x, y))

				# Draw the point on the original canvas
				self.canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red")

				if self.points_window is None:
					self.show_points_window()

				# Draw the point on the new window
				self.points_canvas.create_oval(x-2, y-2, x+2, y+2, outline="red", fill="red")

	def show_points_window(self):
		if self.points_window is None:
			# Get the dimensions of the main window
			main_window_x = self.root.winfo_rootx()
			main_window_y = self.root.winfo_rooty()
			main_window_width = self.root.winfo_width()
			main_window_height = self.root.winfo_height()

			# Create a new window to show clicked points
			self.points_window = tk.Toplevel(self.root)
			self.points_window.title("Clicked Points")

			# Position the new window to the right of the main window
			new_window_x = main_window_x + main_window_width
			new_window_y = main_window_y
			self.points_window.geometry(f"{self.tk_image.width()}x{self.tk_image.height()}+{new_window_x}+{new_window_y}")

			self.points_canvas = tk.Canvas(self.points_window, width=self.tk_image.width(), height=self.tk_image.height(), bg="white")
			self.points_canvas.pack(fill=tk.BOTH, expand=True)

			# Draw axis markers in the new window
			for label, (x, y) in self.axis_points.items():
				color = "blue" if label == 'X0' else "green" if label == 'Xmax' else "yellow" if label == 'Y0' else "orange"
				self.points_canvas.create_oval(x-4, y-4, x+4, y+4, outline=color, fill=color)
				self.points_canvas.create_text(x, y-10, text=label, fill=color)

if __name__ == "__main__":
	root = tk.Tk()
	app = GraphGrabberApp(root)
	root.mainloop()