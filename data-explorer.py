import wx
import wx.adv as adv

from functools import partial

import functions.functions as fn
import widgets.widgets as wd


class DataExplorerApp(wx.App):
	'''
	Class which encompasses the entirety of the Data Explorer
	'''
	default_title = 'Data Explorer'

	def OnInit(self):
		self.filters = {}
		self.filter_columns = {}
		self.filter_dialog = None

		# Frames.
		self.csv_frame = wd.TabularDisplayFrame(None, title=self.default_title)

		# Menu.
		menuBar = wx.MenuBar()

		## File.
		menu = wx.Menu()
		menuBar.Append(menu, '&File')

		item = menu.Append(wx.ID_OPEN, '&Open...')
		self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, item)

		self.close_menu_item = menu.Append(wx.ID_CLOSE, '&Close')
		self.close_menu_item.Enable(False)
		self.Bind(wx.EVT_MENU, self.OnMenuFileClose, self.close_menu_item)

		menu.AppendSeparator()

		self.filter_menu_item = menu.Append(wx.ID_ANY, '&Filters...')
		self.filter_menu_item.Enable(False)
		self.Bind(wx.EVT_MENU, self.OnMenuFileFilters, self.filter_menu_item)

		menu.AppendSeparator()

		item = menu.Append(wx.ID_EXIT, 'E&xit')
		self.Bind(wx.EVT_MENU, self.OnMenuFileExit, item)

		## Plot.
		menu = wx.Menu()
		menuBar.Append(menu, '&Plot')

		menu.Append(wx.ID_ANY, ' 2D:').Enable(False)

		self.two_dimensional_menu = menu.Append(wx.ID_ANY, '&Curve...')
		self.Bind(wx.EVT_MENU, wd.NotImplemented, self.two_dimensional_menu)
		self.Bind(wx.EVT_MENU, self.create_curve, self.two_dimensional_menu) 
		#partial(self.create_plot, formats.two_dimensional),self.two_dimensional_menu)

		menu.AppendSeparator()

		menu.Append(wx.ID_ANY, ' 3D:').Enable(False)

		self.colormapped_menu = menu.Append(wx.ID_ANY, '&Colormapped...')
		self.Bind(wx.EVT_MENU, wd.NotImplemented, self.colormapped_menu) # self.Bind(wx.EVT_MENU, partial(self.create_plot, formats.colormapped), self.colormapped_menu)

		self.surface_menu = menu.Append(wx.ID_ANY, '&Surface...')
		self.Bind(wx.EVT_MENU, wd.NotImplemented,  self.surface_menu) # self.Bind(wx.EVT_MENU, partial(self.create_plot, formats.surface), self.surface_menu)

		menu.AppendSeparator()

		menu.Append(wx.ID_ANY, ' List:').Enable(False)

		self.waveforms_menu = menu.Append(wx.ID_ANY, '&Waveforms...')
		self.Bind(wx.EVT_MENU, wd.NotImplemented, self.waveforms_menu) # self.Bind(wx.EVT_MENU, partial(self.create_plot, formats.waveforms, type='list'), self.waveforms_menu)

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

	def create_curve(self):
		pass

	def create_plot(self, format, evt=None, type='scalar'):
		"""
		Open up a dialog to configure the selected plot format.
		"""

		headings, rows, types = self.csv_frame.display_panel.GetValue(types=[type])
		# available_formats[format](self.csv_frame, headings, rows).Show()

	def OnMenuFileOpen(self, evt=None):
		try:
			has_header, values, filename = fn.load_csv(self.csv_frame)
		except IOError as e:
			wx.MessageDialog(self.csv_frame, str(e), 'Could not load data').Show()
			return

		if not bool(has_header or values or filename):
			return
		else:
			self.OnMenuFileClose()

		self.csv_frame.display_panel.from_csv_data(has_header, values)
		self.csv_frame.Title = f'{filename} - {self.default_title}'

		self.update_plot_menus(len(self.csv_frame.display_panel) > 0)

		self.filter_menu_item.Enable(True)
		self.close_menu_item.Enable(True)

	def OnMenuFileClose(self, evt=None):
		self.csv_frame.display_panel.SetValue([], [])
		self.csv_frame.Title = self.default_title

		self.update_plot_menus(False)

		self.filter_menu_item.Enable(False)

		if self.filter_dialog is not None:
			self.filter_dialog.Close()

		self.filters = {}
		self.filter_columns = {}

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
		# headings, rows, types = self.csv_frame.display_panel.GetValue(types=[type])
		# dmath = FunctionMathSetupDialog(self.csv_frame, headings, rows)
		# dmath_open = dmath.ShowModal()
				
		# new_headings = headings
		# new_headings.append(dmath.dheading)
		# new_rows = concatenate([rows.astype(float),dmath.ddata],1)

		# self.csv_frame.display_panel.SetValue(new_headings,new_rows)

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

	def OnMenuHelpAbout(self, evt=None):
		info = adv.AboutDialogInfo()
		info.SetName('Data Explorer')
		info.SetDescription('''An application for displaying data in tabular and graphical form.\n'
		Written by Stephen Harrigan using code from Dmitri Iouchtchenko.
		'''
		)

		adv.AboutBox(info)

if __name__ == "__main__":
	app = DataExplorerApp()
	app.MainLoop()
