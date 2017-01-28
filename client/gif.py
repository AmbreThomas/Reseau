import Tkinter as tk
from PIL import Image, ImageTk, ImageSequence

class App:
	def __init__(self, parent, filename):
		self.parent = parent
		self.canvas = tk.Canvas(parent, width = 750, height = 600)
		self.canvas.pack()
		self.sequence = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(Image.open(filename))]
		self.image = self.canvas.create_image(0,0, anchor=tk.NW, image = self.sequence[0])
		self.animating = True
		self.animate(0)

	def animate(self, counter):
		self.canvas.itemconfig(self.image, image = self.sequence[counter])
		if not self.animating:
			return
		self.parent.after(500, lambda: self.animate((counter + 1) % len(self.sequence)))
