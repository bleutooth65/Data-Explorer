'''
File which contains all of the custom widgets created for the Data Explorer
'''

import wx
import wx.grid
import numpy as np
import pandas as pd

import wx.lib.agw.aui as aui

import matplotlib as mpl
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

def NotImplemented(self): 
      wx.MessageBox("Currently not implemented", "Not Implemented" ,wx.OK | wx.ICON_WARNING)

# class VirtualListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
# 	"""
# 	A generic virtual list.
# 	"""

# 	max_value_len = 20 # Characters.

# 	@staticmethod
# 	def find_type(value):
# 		"""
# 		Determine the type of a column based on a single value.

# 		The type is one of: scalar, list, string.
# 		"""

# 		try:
# 			float(value)
# 		except ValueError:
# 			pass
# 		else:
# 			return 'scalar'

# 		try:
# 			ListParser()(value)
# 		except ValueError:
# 			pass
# 		else:
# 			return 'list'

# 		return 'string'

# 	def __init__(self, parent, *args, **kwargs):
# 		wx.ListCtrl.__init__(self, parent,
# 				style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES,
# 				*args, **kwargs)

# 		ListCtrlAutoWidthMixin.__init__(self)

# 		self.reset()

# 	def reset(self):
# 		self.headings = []
# 		self.data = np.array([])
# 		self.filtered_data = None
# 		self.display_data = np.array([])

# 		self.types = []

# 	def refresh_with_values(self, data):
# 		self.ItemCount = len(data)

# 		if self.ItemCount > 0:
# 			self.display_data = np.zeros(data.shape, dtype=f'|S{self.max_value_len}')

# 			for i, _ in enumerate(self.headings):
# 				# Truncate for display.
# 				self.display_data[:,i] = [str(x)[:self.max_value_len] for x in data[:,i]]

# 		self.Refresh()

# 	def apply_filter(self, f, afresh=False):
# 		"""
# 		Set the data to be the old data, along with the application of a filter.

# 		f is a function of two parameters: the index of the row and the row itself.
# 		f must return True if the row is to be kept and False otherwise.

# 		If afresh is True, all old filtered data is discarded.
# 		Otherwise, a new filter can be quickly applied.
# 		"""

# 		if afresh:
# 			self.filtered_data = None

# 		if self.filtered_data is not None:
# 			original_set = self.filtered_data
# 		else:
# 			original_set = self.data

# 		self.filtered_data = compress([f(i, x) for i, x in enumerate(original_set)], original_set, axis=0)

# 		self.refresh_with_values(self.filtered_data)

# 	def GetValue(self, types=None):
# 		# Get all types by default.
# 		if types is None:
# 			types = set(self.types)
# 		else:
# 			types = set(types)

# 		# Find column indices of the correct type.
# 		idxs = [i for i, t in enumerate(self.types) if t in types]

# 		if self.filtered_data is not None:
# 			data = self.filtered_data
# 		else:
# 			data = self.data

# 		return ([self.headings[i] for i in idxs], data[:,idxs], [self.types[i] for i in idxs])

# 	def SetValue(self, headings, data):
# 		"""
# 		headings: A list of strings.
# 		data: A 2D NumPy array.
# 		"""

# 		self.ClearAll()
# 		self.reset()

# 		self.headings = headings
# 		self.data = data

# 		self.refresh_with_values(self.data)

# 		if self.ItemCount > 0:
# 			width, height = self.GetSize()
# 			# Give some room for the scrollbar.
# 			col_width = (width - 50) / len(self.headings)

# 			for i, heading in enumerate(self.headings):
# 				self.InsertColumn(i, heading, width=col_width)

# 				type = self.find_type(data[0,i])
# 				self.types.append(type)

# 	def OnGetItemText(self, item, col):
# 		"""
# 		Return cell value for LC_VIRTUAL.
# 		"""

# 		return self.display_data[item,col]

class Table_Viewer(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent,id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_HRULES)
		self.df=pd.DataFrame()
#-----------------------------         
	def set_value(self,df):
		self.ClearAll()
		self.df=df.copy()
		for i, col in enumerate(df):
			self.InsertColumn(i,col)
			self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
		self.SetBackgroundColour(wx.Colour('#e6f3ff'))
		self.EnableAlternateRowColours(enable=True)
		self.SetItemCount(len(self.df))
		self.Update()
#----------------------------  
	def OnGetItemText(self,item, col):
			value = self.df.iloc[item, col]
			return str(value)

class TabularDisplayFrame(wx.Frame):
	"""
	Frame that holds all other widgets
	"""

	def __init__(self, parent, *args, **kwargs):
		"""Constructor"""
		wx.Frame.__init__(self, None, *args, **kwargs)
		# self._init_gui()
		self.Layout()
		self.Show()

	def _init_gui(self, data):
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.add_table(data), 1, wx.EXPAND)
		self.SetSizer(self.sizer)
		self.sizer.SetSizeHints(self)
		self.SetSize((800, 600))

	def add_table(self, data):
		table = Table_Viewer(self)
		table.set_value(data)
		self.SetSize((800, 600))
		return table

	def remove_table(self):
		self.sizer.Clear(delete_windows=True)
		self.sizer.SetSizeHints(self)
		self.SetSize((800, 600))

	def exit(self, event):
		self.Destroy()

class Plot(wx.Panel):
	def __init__(self, parent, id=-1, dpi=None, **kwargs):
		wx.Panel.__init__(self, parent, id=id, **kwargs)
		self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2, 2))
		self.canvas = FigureCanvas(self, -1, self.figure)
		self.toolbar = NavigationToolbar(self.canvas)
		self.toolbar.Realize()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
		self.SetSizer(sizer)

class PlotNotebook(wx.Panel):
	def __init__(self, parent, id=-1):
		wx.Panel.__init__(self, parent, id=id)
		self.nb = aui.AuiNotebook(self)
		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.SetSizer(sizer)

	def add(self, name="plot"):
		page = Plot(self.nb)
		self.nb.AddPage(page, name)
		return page.figure

def create_plot_notebook(frame):
	plotter = PlotNotebook(frame)
	return plotter

class TwoDimensionalPlotSelection(wx.Frame): 
	def __init__(self, parent, title, data): 
		super(TwoDimensionalPlotSelection, self).__init__(parent, title = title)

		# Save the data that was passed
		self.data = data
		self.parent = parent
		# Make a list of the columns in the data
		columns = list(data.columns)

		# Set x and y data to none for the moment
		self.x = None
		self.y = None

		# Create the panel for the plot selector interface
		panel = wx.Panel(self) 

		# Create a horizontal box sizer, which will contain the x selection interface, the y selection interface and the confirmation button
		main_box = wx.BoxSizer(wx.HORIZONTAL)

		# Create box for x selection interface
		x_box = wx.BoxSizer(wx.VERTICAL)

		# Create 'X' text label and place in box
		x_text = wx.StaticText(panel,label = "X",style = wx.ALIGN_CENTRE) 	
		x_box.Add(x_text,0,wx.EXPAND|wx.ALL,5)

		# Add ListBox to select 
		self.x_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		x_box.Add(self.x_selector,0,wx.EXPAND|wx.ALL,5)

		# Add whole x selector menu into the main box
		main_box.Add(x_box, 0,wx.EXPAND|wx.ALL,5)
		
		# Create box for y selection interface
		y_box= wx.BoxSizer(wx.VERTICAL)

		# Add ListBox to select
		y_text = wx.StaticText(panel,label = "Y",style = wx.ALIGN_CENTRE) 			
		y_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.y_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		y_box.Add(self.y_selector,0,wx.EXPAND|wx.ALL,5) 
		main_box.Add(y_box, 0, wx.EXPAND|wx.ALL,5)

		self.button = wx.Button(panel,label="Confirm",style = wx.BU_EXACTFIT)
		main_box.Add(self.button, 0, wx.SHAPED|wx.ALIGN_CENTER, 5) 

		self.x_selector.Bind(wx.EVT_LISTBOX, self.OnXSelect) 
		self.y_selector.Bind(wx.EVT_LISTBOX, self.OnYSelect)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show() 
			
	def OnXSelect(self, event): 
		x_index = self.x_selector.GetSelection()
		self.x = self.x_selector.GetString(x_index)
		
	def OnYSelect(self,event):
		y_index = self.y_selector.GetSelection()
		self.y = self.y_selector.GetString(y_index)

	def OnButtonPress(self, event):
		self.plotter_frame = wx.Frame(self.parent, -1, 'Plotter')
		self.plotter_frame.SetSize((800, 600))
		self.plotter = create_plot_notebook(self.plotter_frame)

		axes1 = self.plotter.add('figure 1').gca()
		axes1.plot(self.x, self.y , data=self.data)
		self.plotter_frame.Show()
		self.plotter_frame.Raise()

		self.Close()

class ThreeDimensionalPlotSelection(wx.Frame): 
	def __init__(self, parent, title, data): 
		super(TwoDimensionalPlotSelection, self).__init__(parent, title = title)

		# Save the parent window and the data that was passed
		self.parent = parent
		self.data = data
		# Make a list of the columns in the data
		columns = list(data.columns)

		# Set x and y data to none for the moment
		self.x = None
		self.y = None

		# Create the panel for the plot selector interface
		panel = wx.Panel(self) 

		# Create a horizontal box sizer, which will contain the x selection interface, the y selection interface and the confirmation button
		main_box = wx.BoxSizer(wx.HORIZONTAL)

		# Create box for x selection interface
		x_box = wx.BoxSizer(wx.VERTICAL)

		# Create 'X' text label and place in box
		x_text = wx.StaticText(panel,label = "X",style = wx.ALIGN_CENTRE) 	
		x_box.Add(x_text,0,wx.EXPAND|wx.ALL,5)

		# Add ListBox to select 
		self.x_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		x_box.Add(self.x_selector,0,wx.EXPAND|wx.ALL,5)

		# Add whole x selector menu into the main box
		main_box.Add(x_box, 0,wx.EXPAND|wx.ALL,5)
		
		# Create box for y selection interface
		y_box= wx.BoxSizer(wx.VERTICAL)

		# Add ListBox to select
		y_text = wx.StaticText(panel,label = "Y",style = wx.ALIGN_CENTRE) 			
		y_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.y_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		y_box.Add(self.y_selector,0,wx.EXPAND|wx.ALL,5) 
		main_box.Add(y_box, 0, wx.EXPAND|wx.ALL,5)

		z_box= wx.BoxSizer(wx.VERTICAL)

		# Add ListBox to select
		z_text = wx.StaticText(panel,label = "Z",style = wx.ALIGN_CENTRE) 			
		z_box.Add(z_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.z_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		z_box.Add(self.z_selector,0,wx.EXPAND|wx.ALL,5) 
		main_box.Add(z_box, 0, wx.EXPAND|wx.ALL,5)

		self.button = wx.Button(panel,label="Confirm",style = wx.BU_EXACTFIT)
		main_box.Add(self.button, 1, wx.SHAPED|wx.ALIGN_CENTER, 5) 

		self.x_selector.Bind(wx.EVT_LISTBOX, self.OnXSelect) 
		self.y_selector.Bind(wx.EVT_LISTBOX, self.OnYSelect)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show() 

# def demo():
#     app = wx.App()
#     frame = wx.Frame(None, -1, 'Plotter')
#     plotter = PlotNotebook(frame)
#     axes1 = plotter.add('figure 1').gca()
#     axes1.plot([1, 2, 3], [2, 1, 4])
#     axes2 = plotter.add('figure 2').gca()
#     axes2.plot([1, 2, 3, 4, 5], [2, 1, 4, 2, 3])
#     frame.Show()
#     app.MainLoop()

# if __name__ == "__main__":
#     demo()