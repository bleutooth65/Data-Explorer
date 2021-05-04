'''
File which contains all of the custom widgets created for the Data Explorer
'''

import wx
import pandas as pd
import seaborn as sns

import matplotlib as mpl
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)

def NotImplemented(self): 
      wx.MessageBox("Currently not implemented", "Not Implemented", wx.OK | wx.ICON_WARNING)

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
		self.parent = parent
		# self._init_gui()
		self.Layout()
		self.Show()

	def _init_gui(self):
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.add_table(self.data), 1, wx.EXPAND)
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
		self.nb = wx.Notebook(self)
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
	def __init__(self, parent, title): 
		super(TwoDimensionalPlotSelection, self).__init__(parent, title = title)

		# Save the data that was passed
		self.data = parent.data
		self.parent = parent
		# Make a list of the columns in the data
		columns = list(self.data.columns)

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
		
	def OnYSelect(self, event):
		y_index = self.y_selector.GetSelection()
		self.y = self.y_selector.GetString(y_index)

	def OnButtonPress(self, event):
		self.plotter_frame = wx.Frame(self.parent, -1, self.parent.Title[:-len(' - Data Explorer')])
		self.plotter_frame.SetSize((800, 600))
		self.plotter = create_plot_notebook(self.plotter_frame)

		axes = self.plotter.add(self.parent.Title[:-len(' - Data Explorer')]).gca()
		axes.plot(self.x, self.y, data=self.data)
		axes.set_xlabel(self.x, size=12)
		axes.set_ylabel(self.y, size=12)

		self.plotter_frame.Show()
		self.plotter_frame.Raise()

		self.Close()

class ThreeDimensionalPlotSelection(wx.Frame): 
	def __init__(self, parent, title): 
		super(ThreeDimensionalPlotSelection, self).__init__(parent, title = title)

		# Save the parent window and the data that was passed
		self.parent = parent
		self.data = parent.data
		# Make a list of the columns in the data
		columns = list(self.data.columns)

		# Set x and y data to none for the moment
		self.x = None
		self.y = None
		self.z = None

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
		self.z_selector.Bind(wx.EVT_LISTBOX, self.OnZSelect)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)

			# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show() 

	def OnXSelect(self, event): 
		x_index = self.x_selector.GetSelection()
		self.x = self.x_selector.GetString(x_index)
		
	def OnYSelect(self, event):
		y_index = self.y_selector.GetSelection()
		self.y = self.y_selector.GetString(y_index)

	def OnZSelect(self, event):
		z_index = self.z_selector.GetSelection()
		self.z = self.z_selector.GetString(z_index)

	def OnButtonPress(self, event):
		self.plotter_frame = wx.Frame(self.parent, -1, self.parent.Title[:-len(' - Data Explorer')])
		self.plotter_frame.SetSize((800, 800))
		self.plotter = create_plot_notebook(self.plotter_frame)

		pivotted_data = self.data.pivot(index=self.y, columns=self.x, values=self.z)

		axes = self.plotter.add(self.parent.Title[:-len(' - Data Explorer')]).gca()
		sns.heatmap(pivotted_data, ax=axes, cbar_kws={'label': self.z})
		axes.invert_yaxis()
		axes.set_xlabel(self.x, size=14)
		axes.set_ylabel(self.y, size=14)

		self.plotter_frame.Show()
		self.plotter_frame.Raise()

		self.Close()

class RenameColumnSelection(wx.Frame): 
	def __init__(self, parent, title): 
		super(RenameColumnSelection, self).__init__(parent, title = title)

		# Save the data that was passed
		self.data = parent.data
		self.parent = parent
		# Make a list of the columns in the data
		columns = list(self.data.columns)

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
		y_text = wx.StaticText(panel,label = "New Name",style = wx.ALIGN_CENTRE) 			
		y_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.new_text_box = wx.TextCtrl(panel, value="")
		y_box.Add(self.new_text_box,0,wx.EXPAND|wx.ALL,5) 
		main_box.Add(y_box, 0, wx.EXPAND|wx.ALL,5)

		self.button = wx.Button(panel,label="Confirm",style = wx.BU_EXACTFIT)
		main_box.Add(self.button, 0, wx.SHAPED|wx.ALIGN_CENTER, 5) 

		self.x_selector.Bind(wx.EVT_LISTBOX, self.OnXSelect) 
		self.new_text_box.Bind(wx.EVT_TEXT, self.OnTextEntry)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show()

	def OnTextEntry(self, event):
		self.text = self.new_text_box.GetValue()
			
	def OnXSelect(self, event): 
		x_index = self.x_selector.GetSelection()
		self.x = self.x_selector.GetString(x_index)
		self.new_text_box.SetValue(self.x)

	def OnButtonPress(self, event):

		self.parent.data = self.parent.data.rename(columns={self.x:self.text})
		self.parent.remove_table()
		self.parent._init_gui()
		self.Close()