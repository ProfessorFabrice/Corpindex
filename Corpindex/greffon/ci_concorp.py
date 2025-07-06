# import Tkinter
from tkinter import *
from tkinter import ttk


class Gui(object):
	
	def __init__(self):
		self.root = Root()
		self.menuBar = MenuBar()
		self.treeview = Treeview()
		self.console = Console()
		self.root.loop()
		

class Root(Tk):
	
	"""Creates the root and the window where the widgets are displayed."""
	
	def __init__(self):
		self.geometry("800x600")
		self.title("Concorp - Corpindex")
		self.window = Frame(self)
		self.window.pack(fill=BOTH, expand=YES)
		
	def loop(self):
		self.config(menu=menuBar)
		self.mainloop()
		
class MenuBar():
	
	"""Creates a menu bar."""

	def __init__(self):
		



class Query(Root):
	
	"""Creates a widget for entering queries."""

	
	def __init__(self):
		Root.__init__(self)
		self.frame = LabelFrame(self.window,text=__RSC["QUERY"])
		self.entry = Entry(self.frame)
		self.button = Button(self.frame,text="Go", command=lanceRequete)
		self.menu = Menu(root, tearoff=0)
		self.menu.add_command(label="Cut", command=self.cut)
		self.menu.add_command(label="Copy", command=self.copy)
		self.menu.add_command(label="Paste", command=self.paste)
		self.entry.bind('<Up>',keyboard)
		self.entry.bind('<Down>',keyboard)
		self.entry.bind('<Return>',keyboard)
		self.entry.pack(side=LEFT, fill=X, expand=YES)
		self.button.pack(side=RIGHT)
		self.frame.pack(fill=X)
		self.entry.bind("<Button-3>" "<ButtonRelease>", self.popup)
		
	def popup(self, event):
		"""Displays a contextual menu."""
		self.menu.post(event.x_root, event.y_root)
	
	def copy(self, event=None):
		self.entry.event_generate('<Control-c>')

	def cut(self, event=None):
		self.entry.event_generate('<Control-x>')

	def paste(self, event=None):
		self.entry.event_generate('<Control-v>')



class Console(Root):
	
	"""Creates a console widget with a scrollbar and displays it."""
	
	def __init__ (self):
		Root.__init__(self)
		self.frame = LabelFrame(self.window,text="Console")
		self.text = Text(self.frame, height=5,width=100, state="disabled")
		self.scrollBar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
		self.text.configure( yscrollcommand=self.scrollBar.set)
		self.menu = Menu(root, tearoff=0)
		self.menu.add_command(label="Copy", command=self.copy)
		self.scrollBar.pack(side=RIGHT, fill=Y)
		self.text.pack(fill=X)
		self.text.bind("<Button-3>" "<ButtonRelease>", self.popup)
		self.frame.pack(fill=X)
		
	def popup(self, event):
		"""Displays a contextual menu."""
		self.menu.post(event.x_root, event.y_root)
		
	def copy(self, event=None):
		self.text.clipboard_clear()
		text = self.text.get("sel.first", "sel.last")
		self.text.clipboard_append(text)
		
	def display(self,message):
		"""Displays a text in the console."""
		self.text.configure(state="normal")
		self.text.insert('end',str(message)+"\n")
		self.text.yview("end")
		self.text.configure(state="disabled")
		
		
		

