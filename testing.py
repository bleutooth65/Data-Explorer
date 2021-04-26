# import wx
# import wx.grid

# class GridFrame(wx.Frame):
#     def __init__(self, parent):
#         wx.Frame.__init__(self, parent)

#         # Create a wxGrid object
#         grid = wx.grid.Grid(self, -1)

#         # Then we call CreateGrid to set the dimensions of the grid
#         # (100 rows and 10 columns in this example)
#         grid.CreateGrid(100, 10)

#         # We can set the sizes of individual rows and columns
#         # in pixels
#         grid.SetRowSize(0, 60)
#         grid.SetColSize(0, 120)

#         # And set grid cell contents as strings
#         grid.SetCellValue(0, 0, 'wxGrid is good')

#         # We can specify that some cells are read.only
#         grid.SetCellValue(0, 3, 'This is read.only')
#         grid.SetReadOnly(0, 3)

#         # Colours can be specified for grid cell contents
#         grid.SetCellValue(3, 3, 'green on grey')
#         grid.SetCellTextColour(3, 3, wx.GREEN)
#         grid.SetCellBackgroundColour(3, 3, wx.LIGHT_GREY)

#         # We can specify the some cells will store numeric
#         # values rather than strings. Here we set grid column 5
#         # to hold floating point values displayed with width of 6
#         # and precision of 2
#         grid.SetColFormatFloat(5, 6, 2)
#         grid.SetCellValue(0, 6, '3.1415')

#         self.Show()


# if __name__ == '__main__':

#     app = wx.App(0)
#     frame = GridFrame(None)
#     app.MainLoop()


import pandas as pd

import wx
import wx.grid as grid

EVEN_ROW_COLOUR = '#CCE6FF'

data = {
   "downloadHistory": [
        {
            "titles": ["example123456789", "exampletitle2"],
            "author": ["author123456", "author2"],
            "urls": ["https://example.com/", "https://example.com/12345"]
        }
    ],
}

#declare DataTable to hold the wx.grid data to be displayed
class DataTable(wx.grid.GridTableBase):
    def __init__(self, data=None):
        grid.GridTableBase.__init__(self)
        self.headerRows = 1
        if data is None:
            data = pd.DataFrame()
        self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data.columns) + 1

    def GetValue(self, row, col):
        if col == 0:
            return self.data.index[row]
        return self.data.iloc[row, col - 1]

    def SetValue(self, row, col, value):
        self.data.iloc[row, col - 1] = value

    def GetColLabelValue(self, col):
        if col == 0:
            if self.data.index.name is None:
                return 'Index'
            else:
                return self.data.index.name
        return str(self.data.columns[col - 1])

    def GetTypeName(self, row, col):
        return grid.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = grid.GridCellAttr()
        if row % 2 == 1:
            attr.SetBackgroundColour(EVEN_ROW_COLOUR)
        return attr


class MyFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, "DOWNLOAD HISTORY")
        self._init_gui()
        self.Layout()
        self.Show()

    def _init_gui(self):
        # assign the DataFrame to df
        df = pd.DataFrame(data["downloadHistory"][0])
        table = DataTable(df)

        #declare the grid and assign data
        grid = grid.Grid(self, -1)
        grid.SetTable(table, takeOwnership=True)
        grid.AutoSizeColumns()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(grid, 0, wx.EXPAND)
        
        sizer.SetSizeHints(self)

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()