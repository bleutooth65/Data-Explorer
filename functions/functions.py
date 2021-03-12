import wx
import csv
from os.path import basename

def load_csv(parent):
	"""
	Load data from a CSV file based on a file dialog.

	ZParrott: has_header functions partially in that it removes a blank first
	row, but hte has_header boolean then fails in subsequent dependicies where
	it has meaning of having a column title or not.
	"""

	dlg = wx.FileDialog(parent=parent, message='Load...', wildcard="CSV (*.csv)|*.csv",
			style=wx.FD_OPEN)

	if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()

		filename = basename(path)

		with open(path, 'r') as f:
			try:
				result = list(csv.reader(f))
				try:
					has_header = len(result[0]) > 0
				except IndexError:
					has_header = False
				else:
					# Remove empty row.
					if not has_header:
						result = result[1:]

				return has_header, result, filename
			except Exception as e:
				# Wrap all problems.
				raise IOError('Could not load data.', e)