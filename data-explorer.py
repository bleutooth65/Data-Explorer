import wx
from wx.adv import AboutBox, AboutDialogInfo
import pandas as pd

from os.path import basename

import widgets as wd


class DataExplorerApp(wx.App):
	'''
	Class which encompasses the entirety of the Data Explorer
	'''
	default_title = 'Data Explorer'

	def OnInit(self):
		self.filters = {}
		self.filter_columns = {}
		self.filter_dialog = None

		# self.plotter = None
		self.plotter_frame = None

		# Frames.
		self.csv_frame = wd.TabularDisplayFrame(None, title=self.default_title)
		self.csv_frame.data = None

		# Menu.
		menuBar = wx.MenuBar()

		## File.
		menu = wx.Menu()
		menuBar.Append(menu, 'File')

		item = menu.Append(wx.ID_OPEN, 'Open...')
		self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, item)

		self.rename_menu_item = menu.Append(wx.ID_ANY, 'Rename column...')
		self.rename_menu_item.Enable(False)
		self.Bind(wx.EVT_MENU, self.rename_column, self.rename_menu_item)

		self.save_menu_item = menu.Append(wx.ID_ANY, 'Save as...')
		self.save_menu_item.Enable(False)
		self.Bind(wx.EVT_MENU, wd.NotImplemented, self.save_menu_item)

		self.close_menu_item = menu.Append(wx.ID_CLOSE, 'Close')
		self.close_menu_item.Enable(False)
		self.Bind(wx.EVT_MENU, self.OnMenuFileClose, self.close_menu_item)

		menu.AppendSeparator()

		self.filter_menu_item = menu.Append(wx.ID_ANY, 'Filters...')
		self.filter_menu_item.Enable(False)
		self.Bind(wx.EVT_MENU, self.OnMenuFileFilters, self.filter_menu_item)

		menu.AppendSeparator()

		item = menu.Append(wx.ID_EXIT, 'Exit')
		self.Bind(wx.EVT_MENU, self.OnMenuFileExit, item)

		## Plot.
		menu = wx.Menu()
		menuBar.Append(menu, 'Plot')

		menu.Append(wx.ID_ANY, ' 2D:').Enable(False)

		self.two_dimensional_menu = menu.Append(wx.ID_ANY, 'Curve...')
		self.Bind(wx.EVT_MENU, self.create_curve, self.two_dimensional_menu) 

		menu.AppendSeparator()

		menu.Append(wx.ID_ANY, ' 3D:').Enable(False)

		self.colormapped_menu = menu.Append(wx.ID_ANY, 'Color Map...')
		self.Bind(wx.EVT_MENU, self.create_heatmap, self.colormapped_menu)

		## Math.
		menu = wx.Menu()
		menuBar.Append(menu, '&Math')

		item = menu.Append(wx.ID_ANY, '&Derivative...')
		self.Bind(wx.EVT_MENU, self.OnMenuMathDerivative, item)

		item = menu.Append(wx.ID_ANY, '&Function f: y=f(X)...')
		self.Bind(wx.EVT_MENU, self.OnMenuMathFunction, item)

		item = menu.Append(wx.ID_ANY, '&Function f: z=f(X,Y)...')
		self.Bind(wx.EVT_MENU, self.OnMenuMathFunction2arg, item)

		## Help.
		menu = wx.Menu()
		menuBar.Append(menu, '&Help')

		### About.
		item = menu.Append(wx.ID_ABOUT, '&About...')
		self.Bind(wx.EVT_MENU, self.OnMenuHelpAbout, item)

		self.csv_frame.SetMenuBar(menuBar)

		self.update_plot_menus(False)

		# Display.
		self.csv_frame.Show()
		self.csv_frame.SetSize((800, 600))

		self.SetTopWindow(self.csv_frame)
		self.csv_frame.Raise()

		return True

	def update_plot_menus(self, status):
		"""
		If status is True, enable the plot menus corresponding to the available formats. Otherwise, disable all.
		"""

		# pairs = [
		# 	(formats.two_dimensional, self.two_dimensional_menu),
		# 	(formats.colormapped, self.colormapped_menu),
		# 	(formats.surface, self.surface_menu),
		# 	(formats.waveforms, self.waveforms_menu),
		# ]

		# for format, menu in pairs:
		# 	if not status or format in available_formats:
		# 		menu.Enable(status)

	def create_curve(self, event=None):
		selector = wd.TwoDimensionalPlotSelection(self.csv_frame, "Curve Selection Menu")
		selector.Show()
		selector.Raise()

	def create_heatmap(self, event=None):
		selector = wd.ThreeDimensionalPlotSelection(self.csv_frame, "Curve Selection Menu")
		selector.Show()
		selector.Raise()

	def rename_column(self, event=None):
		selector = wd.RenameColumnSelection(self.csv_frame, "Rename column")
		selector.Show()
		selector.Raise()

	# def create_plot(self, format, evt=None, type='scalar'):
	# 	"""
	# 	Open up a dialog to configure the selected plot format.
	# 	"""
	def OnMenuFileOpen(self, evt=None):
		try:
			self.csv_frame.data, self.filename = self._load_csv()
		except IOError as e:
			wx.MessageDialog(self.csv_frame, str(e), 'Could not load data').Show()
			return

		# if not bool(self.data or self.filename):
		# 	return
		# else:
		if hasattr(self.csv_frame, "sizer"):
			self.csv_frame.remove_table()
		#self.OnMenuFileClose()

		# self.csv_frame.display_panel.from_csv_data(has_header, values)
		self.csv_frame.Title = f'{self.filename} - {self.default_title}'

		# self.update_plot_menus(len(self.csv_frame.display_panel) > 0)

		# self.filter_menu_item.Enable(True)
		self.close_menu_item.Enable(True)
		self.save_menu_item.Enable(True)
		self.rename_menu_item.Enable(True)

		# self.data = pd.DataFrame(values[1:], columns=values[0], dtype='float64')
		self.csv_frame._init_gui()
		# self.filename = filename

	def OnMenuFileClose(self, evt=None):
		# self.csv_frame.display_panel.SetValue([], [])
		self.csv_frame.remove_table()
		self.csv_frame.Title = self.default_title

		self.update_plot_menus(False)

		self.filter_menu_item.Enable(False)

		if self.filter_dialog is not None:
			self.filter_dialog.Close()

		self.filters = {}
		self.filter_columns = {}

		self.close_menu_item.Enable(False)
		self.save_menu_item.Enable(False)
		self.rename_menu_item.Enable(False)

	def OnMenuFileFilters(self, evt=None):
		def close_callback(dlg):
			self.filters = dlg.filters
			self.filter_columns = dlg.filter_columns

			self.filter_dialog = None

		# if self.filter_dialog is None:
		# 	self.filter_dialog = FilterListDialog(self.csv_frame, self.csv_frame.display_panel.table,
		# 			close_callback, self.filters, self.filter_columns)
		# 	self.filter_dialog.Show()

		self.filter_dialog.Raise()

	def OnMenuFileExit(self, evt=None):
		if self.csv_frame:
			self.csv_frame.Close()

	def OnMenuMathDerivative(self, format, evt=None, type='scalar'):
		"""
		Open up a dialog to calculate derivative
		"""
		# headings, rows, types = self.csv_frame.display_panel.GetValue(types=[type])
		# dmath = DerivativeMathSetupDialog(self.csv_frame, headings, rows)
		# dmath_open = dmath.ShowModal()

		# new_headings = headings
		# new_headings.append(dmath.dheading)
		# new_rows = concatenate([rows.astype(float),dmath.ddata],1)

		# self.csv_frame.display_panel.SetValue(new_headings,new_rows)

	def OnMenuMathFunction(self, format, evt=None, type='scalar'):
		"""
		Open up a dialog to apply a scalar function of one variable
		"""
		selector = wd.OneArgFunctionSelection(self.csv_frame, "Function Selector")
		selector.Show()
		selector.Raise()

	def OnMenuMathFunction2arg(self, format, evt=None, type='scalar'):
		"""
		Open up a dialog to apply a scalar function of two variables
		"""
		headings, rows, types = self.csv_frame.display_panel.GetValue(types=[type])
		# dmath = FunctionMathSetupDialog2arg(self.csv_frame, headings, rows)
		# dmath_open = dmath.ShowModal()
				
		# new_headings = headings
		# new_headings.append(dmath.dheading)
		# new_rows = concatenate([rows.astype(float),dmath.ddata],1)

		# self.csv_frame.display_panel.SetValue(new_headings,new_rows)

	@staticmethod
	def _load_csv():

		dlg = wx.FileDialog(parent=None, message='Load...', wildcard="CSV (*.csv)|*.csv",
				style=wx.FD_OPEN)

		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			filename = basename(path)
			df = pd.read_csv(path, float_precision='round_trip')

			return df, filename

	def OnMenuHelpAbout(self, evt=None):
		info = AboutDialogInfo()
		info.SetName('Data Explorer')
		info.SetDescription('''An application for displaying data in tabular and graphical form.\n
		Written by Stephen Harrigan using code from Dmitri Iouchtchenko.
		'''
		)
		info.SetDevelopers(["Stephen Harrigan"])
		AboutBox(info)

if __name__ == "__main__":
	#import wx.lib.inspection
	app = DataExplorerApp()
	#wx.lib.inspection.InspectionTool().Show()
	app.MainLoop()
