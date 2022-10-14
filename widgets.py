'''
File which contains all of the custom widgets created for the Data Explorer
'''

import wx
import numpy as np
import pandas as pd

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
	def __init__(self, parent, id=-1, heatmap=False, dpi=None, **kwargs):
		wx.Panel.__init__(self, parent, id=id, **kwargs)
		self.figure, self.axes = mpl.pyplot.subplots()
		self.canvas = FigureCanvas(self, -1, self.figure)
		self.toolbar = NavigationToolbar(self.canvas)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.canvas, 1, wx.EXPAND)
		if heatmap is True:
			v_sizer = wx.BoxSizer(wx.HORIZONTAL)

			min_text = wx.StaticText(self,label = "Min",style = wx.ALIGN_CENTRE) 	
			v_sizer.Add(min_text,0,wx.EXPAND|wx.ALL,5)
			self.min_text_box = wx.TextCtrl(self, value="0")
			v_sizer.Add(self.min_text_box, 0, wx.CENTER | wx.EXPAND)

			max_text = wx.StaticText(self,label = "Max",style = wx.ALIGN_CENTRE) 	
			v_sizer.Add(max_text,0,wx.EXPAND|wx.ALL,5)
			self.max_text_box = wx.TextCtrl(self, value="1")
			v_sizer.Add(self.max_text_box, 0, wx.CENTER | wx.EXPAND)

			self.sizer.Add(v_sizer, 0, wx.RIGHT)

		self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
		self.toolbar.Realize()
		self.SetSizer(self.sizer)
	
	def OnMinTextEntry(self, event):
		self.text = self.new_text_box.GetValue()
		
		self.canvas.draw()

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
		self.plotter = Plot(self.plotter_frame)

		axes = self.plotter.axes
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
		pivotted_data = self.data.pivot(index=self.y, columns=self.x, values=self.z)

		self.plotter_frame = wx.Frame(self.parent, -1, self.parent.Title[:-len(' - Data Explorer')])
		self.plotter_frame.SetSize((800, 800))
		self.plotter = Plot(self.plotter_frame, heatmap=True)

		figure = self.plotter.figure
		axes = self.plotter.axes
		
		pc = axes.pcolormesh(pivotted_data.columns, pivotted_data.index, pivotted_data)
		axes.set_xlabel(self.x, size=14)
		axes.set_ylabel(self.y, size=14)

		cbar = figure.colorbar(pc)
		cbar.set_label(self.z)

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

class RoundColumnSelection(wx.Frame): 
	def __init__(self, parent, title): 
		super(RoundColumnSelection, self).__init__(parent, title = title)

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
		y_text = wx.StaticText(panel,label = "Round to n digits",style = wx.ALIGN_CENTRE) 			
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
		# self.new_text_box.SetValue(self.x)

	def OnButtonPress(self, event):
		self.parent.data = self.parent.data.round({self.x:int(self.text)})
		self.parent.remove_table()
		self.parent._init_gui()
		self.Close()

class OneArgFunctionSelection(wx.Frame):
	def __init__(self, parent, title): 
		super(OneArgFunctionSelection, self).__init__(parent, title = title)

		# Save the data that was passed
		# self.data = parent.data
		self.parent = parent
		# Make a list of the columns in the data
		columns = list(self.parent.data.columns)

		# Set x and y data to none for the moment
		self.x = None

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
		y_text = wx.StaticText(panel,label = "Expression of X",style = wx.ALIGN_CENTRE) 			
		y_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.expression_box = wx.TextCtrl(panel, value="")
		y_box.Add(self.expression_box,0,wx.EXPAND|wx.ALL,5) 

		y_text = wx.StaticText(panel,label = "Column Name",style = wx.ALIGN_CENTRE) 			
		y_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.name_box = wx.TextCtrl(panel, value="")
		y_box.Add(self.name_box,0,wx.EXPAND|wx.ALL,5)

		main_box.Add(y_box, 0, wx.EXPAND|wx.ALL,5)

		self.button = wx.Button(panel,label="Confirm",style = wx.BU_EXACTFIT)
		main_box.Add(self.button, 0, wx.SHAPED|wx.ALIGN_CENTER, 5) 

		self.x_selector.Bind(wx.EVT_LISTBOX, self.OnXSelect) 
		self.expression_box.Bind(wx.EVT_TEXT, self.OnExpressionEntry)
		self.name_box.Bind(wx.EVT_TEXT, self.OnNameEntry)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show()

	def OnExpressionEntry(self, event):
		self.expression = self.expression_box.GetValue()

	def OnNameEntry(self, event):
		self.name = self.name_box.GetValue()
			
	def OnXSelect(self, event): 
		x_index = self.x_selector.GetSelection()
		self.x = self.x_selector.GetString(x_index)
		#self.new_text_box.SetValue('X')

	def OnButtonPress(self, event):
		new_column = eval(self.expression.replace('X', f'self.parent.data["{self.x}"]'))
		self.parent.data[self.name] = new_column
		self.parent.remove_table()
		self.parent._init_gui()
		self.Close()


class TwoArgFunctionSelection(wx.Frame):
	def __init__(self, parent, title): 
		super(TwoArgFunctionSelection, self).__init__(parent, title = title)

		# Save the data that was passed
		# self.data = parent.data
		self.parent = parent
		# Make a list of the columns in the data
		columns = list(self.parent.data.columns)

		# Set x and y data to none for the moment
		self.x = None

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

		# Create box for x selection interface
		y_box = wx.BoxSizer(wx.VERTICAL)

		# Create 'y' text label and place in box
		y_text = wx.StaticText(panel,label = "Y",style = wx.ALIGN_CENTRE) 	
		y_box.Add(y_text,0,wx.EXPAND|wx.ALL,5)

		# Add ListBox to select 
		self.y_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		y_box.Add(self.y_selector,0,wx.EXPAND|wx.ALL,5)

		# Add whole x selector menu into the main box
		main_box.Add(y_box, 0,wx.EXPAND|wx.ALL,5)
		
		# Create box for y selection interface
		text_box= wx.BoxSizer(wx.VERTICAL)

		# Add ListBox to select
		y_text = wx.StaticText(panel,label = "Expression of X and Y",style = wx.ALIGN_CENTRE) 			
		text_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.expression_box = wx.TextCtrl(panel, value="")
		text_box.Add(self.expression_box,0,wx.EXPAND|wx.ALL,5) 

		y_text = wx.StaticText(panel,label = "Column Name",style = wx.ALIGN_CENTRE) 			
		text_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.name_box = wx.TextCtrl(panel, value="")
		text_box.Add(self.name_box,0,wx.EXPAND|wx.ALL,5)

		main_box.Add(text_box, 0, wx.EXPAND|wx.ALL,5)

		self.button = wx.Button(panel,label="Confirm",style = wx.BU_EXACTFIT)
		main_box.Add(self.button, 0, wx.SHAPED|wx.ALIGN_CENTER, 5) 

		self.x_selector.Bind(wx.EVT_LISTBOX, self.OnXSelect) 
		self.y_selector.Bind(wx.EVT_LISTBOX, self.OnYSelect)
		self.expression_box.Bind(wx.EVT_TEXT, self.OnExpressionEntry)
		self.name_box.Bind(wx.EVT_TEXT, self.OnNameEntry)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show()

	def OnExpressionEntry(self, event):
		self.expression = self.expression_box.GetValue()

	def OnNameEntry(self, event):
		self.name = self.name_box.GetValue()
			
	def OnXSelect(self, event): 
		x_index = self.x_selector.GetSelection()
		self.x = self.x_selector.GetString(x_index)

	def OnYSelect(self, event):
		y_index = self.y_selector.GetSelection()
		self.y = self.y_selector.GetString(y_index)

	def OnButtonPress(self, event):
		new_column = eval(self.expression.replace('X', f'self.parent.data["{self.x}"]').replace('Y', f'self.parent.data["{self.y}"]'))
		self.parent.data[self.name] = new_column
		self.parent.remove_table()
		self.parent._init_gui()
		self.Close()

class DerivativeSelection(wx.Frame):
	def __init__(self, parent, title): 
		super(DerivativeSelection, self).__init__(parent, title = title)

		# Save the data that was passed
		# self.data = parent.data
		self.parent = parent
		# Make a list of the columns in the data
		columns = list(self.parent.data.columns)

		# Set x and y data to none for the moment
		self.x = None

		# Create the panel for the plot selector interface
		panel = wx.Panel(self) 

		# Create a horizontal box sizer, which will contain the x selection interface, the y selection interface and the confirmation button
		main_box = wx.BoxSizer(wx.HORIZONTAL)

		# Create box for x selection interface
		x_box = wx.BoxSizer(wx.VERTICAL)

		# Create 'X' text label and place in box
		x_text = wx.StaticText(panel,label = "d",style = wx.ALIGN_CENTRE) 	
		x_box.Add(x_text,0,wx.EXPAND|wx.ALL,5)

		# Add ListBox to select 
		self.x_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		x_box.Add(self.x_selector,0,wx.EXPAND|wx.ALL,5)

		# Add whole x selector menu into the main box
		main_box.Add(x_box, 0,wx.EXPAND|wx.ALL,5)

		# Create box for x selection interface
		y_box = wx.BoxSizer(wx.VERTICAL)

		# Create 'y' text label and place in box
		y_text = wx.StaticText(panel,label = "/d",style = wx.ALIGN_CENTRE) 	
		y_box.Add(y_text,0,wx.EXPAND|wx.ALL,5)

		# Add ListBox to select 
		self.y_selector = wx.ListBox(panel,choices = columns, style=wx.CB_SIMPLE) 
		y_box.Add(self.y_selector,0,wx.EXPAND|wx.ALL,5)

		# Add whole x selector menu into the main box
		main_box.Add(y_box, 0,wx.EXPAND|wx.ALL,5)
		
		# Create box for y selection interface
		text_box= wx.BoxSizer(wx.VERTICAL)

		# # Add ListBox to select
		# y_text = wx.StaticText(panel,label = "Expression of X and Y",style = wx.ALIGN_CENTRE) 			
		# text_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		# self.expression_box = wx.TextCtrl(panel, value="")
		# text_box.Add(self.expression_box,0,wx.EXPAND|wx.ALL,5) 

		y_text = wx.StaticText(panel,label = "Column Name",style = wx.ALIGN_CENTRE) 			
		text_box.Add(y_text, 0 ,wx.EXPAND|wx.ALL,5) 

		self.name_box = wx.TextCtrl(panel, value="")
		text_box.Add(self.name_box,0,wx.EXPAND|wx.ALL,5)

		main_box.Add(text_box, 0, wx.EXPAND|wx.ALL,5)

		self.button = wx.Button(panel,label="Confirm",style = wx.BU_EXACTFIT)
		main_box.Add(self.button, 0, wx.SHAPED|wx.ALIGN_CENTER, 5) 

		self.x_selector.Bind(wx.EVT_LISTBOX, self.OnXSelect) 
		self.y_selector.Bind(wx.EVT_LISTBOX, self.OnYSelect)
		self.name_box.Bind(wx.EVT_TEXT, self.OnNameEntry)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		# Set size of panel to fit the whole dialog, center it on the frame and then show the window

		panel.SetSizer(main_box)
		main_box.SetSizeHints(self)
		self.Centre() 
		self.Show()

	def OnNameEntry(self, event):
		self.name = self.name_box.GetValue()
			
	def OnXSelect(self, event): 
		x_index = self.x_selector.GetSelection()
		self.x = self.x_selector.GetString(x_index)

	def OnYSelect(self, event):
		y_index = self.y_selector.GetSelection()
		self.y = self.y_selector.GetString(y_index)

	def OnButtonPress(self, event):
		new_column = np.gradient(self.parent.data[self.x])/np.gradient(self.parent.data[self.y])
		self.parent.data[self.name] = new_column
		self.parent.remove_table()
		self.parent._init_gui()
		self.Close()