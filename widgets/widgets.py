'''
File which contains all of the custom widgets created for the Data Explorer
'''

import wx
import numpy as np

import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

import matplotlib as mpl
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

def NotImplemented(self): 
      wx.MessageBox("Currently not implemented", "Not Implemented" ,wx.OK | wx.ICON_WARNING)

def ListParser():
	"""
	A parser for list columns, where each list is composed of pairs of values.
	"""

	value = Regex(r'[-+]?[0-9]+(?:\.[0-9]*)?(?:e[-+]?[0-9]+)?', IGNORECASE)
	value.setParseAction(lambda toks: float(toks[0]))

	item = Suppress('(') + value + Suppress(',') + value + Suppress(')')
	item.setParseAction(tuple)

	lst = Suppress('[') + delimitedList(item) + Suppress(']')
	lst.setParseAction(list)

	def parse(s):
		try:
			return lst.parseString(s).asList()
		except ParseBaseException as e:
			raise ValueError(e)

	return parse


class VirtualListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
	"""
	A generic virtual list.
	"""

	max_value_len = 20 # Characters.

	@staticmethod
	def find_type(value):
		"""
		Determine the type of a column based on a single value.

		The type is one of: scalar, list, string.
		"""

		try:
			float(value)
		except ValueError:
			pass
		else:
			return 'scalar'

		try:
			ListParser()(value)
		except ValueError:
			pass
		else:
			return 'list'

		return 'string'

	def __init__(self, parent, *args, **kwargs):
		wx.ListCtrl.__init__(self, parent,
				style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES,
				*args, **kwargs)

		ListCtrlAutoWidthMixin.__init__(self)

		self.reset()

	def reset(self):
		self.headings = []
		self.data = np.array([])
		self.filtered_data = None
		self.display_data = np.array([])

		self.types = []

	def refresh_with_values(self, data):
		self.ItemCount = len(data)

		if self.ItemCount > 0:
			self.display_data = np.zeros(data.shape, dtype=f'|S{self.max_value_len}')

			for i, _ in enumerate(self.headings):
				# Truncate for display.
				self.display_data[:,i] = [str(x)[:self.max_value_len] for x in data[:,i]]

		self.Refresh()

	def apply_filter(self, f, afresh=False):
		"""
		Set the data to be the old data, along with the application of a filter.

		f is a function of two parameters: the index of the row and the row itself.
		f must return True if the row is to be kept and False otherwise.

		If afresh is True, all old filtered data is discarded.
		Otherwise, a new filter can be quickly applied.
		"""

		if afresh:
			self.filtered_data = None

		if self.filtered_data is not None:
			original_set = self.filtered_data
		else:
			original_set = self.data

		self.filtered_data = compress([f(i, x) for i, x in enumerate(original_set)], original_set, axis=0)

		self.refresh_with_values(self.filtered_data)

	def GetValue(self, types=None):
		# Get all types by default.
		if types is None:
			types = set(self.types)
		else:
			types = set(types)

		# Find column indices of the correct type.
		idxs = [i for i, t in enumerate(self.types) if t in types]

		if self.filtered_data is not None:
			data = self.filtered_data
		else:
			data = self.data

		return ([self.headings[i] for i in idxs], data[:,idxs], [self.types[i] for i in idxs])

	def SetValue(self, headings, data):
		"""
		headings: A list of strings.
		data: A 2D NumPy array.
		"""

		self.ClearAll()
		self.reset()

		self.headings = headings
		self.data = data

		self.refresh_with_values(self.data)

		if self.ItemCount > 0:
			width, height = self.GetSize()
			# Give some room for the scrollbar.
			col_width = (width - 50) / len(self.headings)

			for i, heading in enumerate(self.headings):
				self.InsertColumn(i, heading, width=col_width)

				type = self.find_type(data[0,i])
				self.types.append(type)

	def OnGetItemText(self, item, col):
		"""
		Return cell value for LC_VIRTUAL.
		"""

		return self.display_data[item,col]

class TabularDisplayPanel(wx.Panel):
	"""
	A panel to display arbitrary tabular data.
	"""

	def __init__(self, parent, *args, **kwargs):
		wx.Panel.__init__(self, parent, *args, **kwargs)

		# Panel.
		panel_box = wx.BoxSizer(wx.VERTICAL)

		## Table.
		self.table = VirtualListCtrl(self)
		panel_box.Add(self.table, proportion=1, flag=wx.EXPAND)

		self.SetSizer(panel_box)

	def __len__(self):
		return self.table.ItemCount

	# TODO: has headers does not function as intended, never will reach code to give header names
	def from_csv_data(self, has_header, values):
		"""
		Import the given CSV data into the table.

		If has_header is True, the first row is treated specially.
		"""

		if has_header:
			headers, rows = values[0], np.array(values[1:])
		else:
			headers, rows = [''] * len(values[0]), np.array(values)

		# Ensure that all columns have a header.
		for i, header in enumerate(headers):
			if not header:
				headers[i] = f'Column {i + 1}'

		self.SetValue(headers, rows)

	def GetValue(self, *args, **kwargs):
		return self.table.GetValue(*args, **kwargs)

	def SetValue(self, headings, values):
		self.table.SetValue(headings, values)


class TabularDisplayFrame(wx.Frame):
	def __init__(self, parent, *args, **kwargs):
		wx.Frame.__init__(self, parent, *args, **kwargs)

		# Frame.
		frame_box = wx.BoxSizer(wx.VERTICAL)

		## Display panel.
		self.display_panel = TabularDisplayPanel(self)
		frame_box.Add(self.display_panel, proportion=1, flag=wx.EXPAND)

		self.SetSizer(frame_box)

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
		super(TwoDimensionalPlotSelection, self).__init__(parent, title = title,size = (300,200))
		self.x = None
		self.y = None
		self.parent = parent
		self.data = data
			
		panel = wx.Panel(self) 
		box = wx.BoxSizer(wx.VERTICAL)
		x_text = wx.StaticText(panel,label = "X",style = wx.ALIGN_CENTRE) 
			
		box.Add(x_text,0,wx.EXPAND|wx.ALL,5) 
		languages = list(data.columns)
		self.x_selector = wx.ComboBox(panel,choices = languages) 
		box.Add(self.x_selector,1,wx.EXPAND|wx.ALL,5)

		y_text = wx.StaticText(panel,label = "Y",style = wx.ALIGN_CENTRE) 			
		box.Add(y_text,0,wx.EXPAND|wx.ALL,5) 
		self.y_selector = wx.ComboBox(panel,choices = languages) 
		box.Add(self.y_selector,1,wx.EXPAND|wx.ALL,5) 

		self.button = wx.Button(panel,label="Confirm",style = wx.ALIGN_CENTRE)
		box.Add(self.button,0,wx.EXPAND|wx.ALL,5) 
			
		box.AddStretchSpacer() 
		self.x_selector.Bind(wx.EVT_COMBOBOX, self.OnXSelect) 
		self.y_selector.Bind(wx.EVT_COMBOBOX, self.OnYSelect)
		self.button.Bind(wx.EVT_BUTTON, self.OnButtonPress)
			
		panel.SetSizer(box) 
		self.Centre() 
		self.Show() 
			
	def OnXSelect(self, event): 
		self.x = self.x_selector.GetValue()
		
	def OnYSelect(self,event): 
		self.y = self.y_selector.GetValue()

	def OnButtonPress(self, event):
		self.plotter_frame = wx.Frame(self.parent, -1, 'Plotter')
		self.plotter_frame.SetSize((800, 600))
		self.plotter = create_plot_notebook(self.plotter_frame)

		axes1 = self.plotter.add('figure 1').gca()
		axes1.plot(self.x, self.y , data=self.data)
		self.plotter_frame.Show()
		self.plotter_frame.Raise()

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