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


import numpy as np
import pandas as pd

import wx
import wx.grid

# EVEN_ROW_COLOUR = '#CCE6FF'
# GRID_LINE_COLOUR = '#ccc'

class DataTable(wx.grid.GridTableBase):
    def __init__(self, data=None):
        wx.grid.GridTableBase.__init__(self)
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
        return wx.grid.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = wx.grid.GridCellAttr()
        if row % 2 == 1:
            attr.SetBackgroundColour('#CCE6FF')
        return attr


class MyFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, "Pandas")
        self._init_gui()
        self.Layout()
        self.Show()

    def _init_gui(self):
        df = pd.DataFrame(np.random.random((20, 5)))
        table = DataTable(df)

        grid = wx.grid.Grid(self, -1)
        grid.SetTable(table, takeOwnership=True)
        grid.AutoSizeColumns()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)

        self.Bind(wx.EVT_CLOSE, self.exit)

    def exit(self, event):
        self.Destroy()


import wx

class Page(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "THIS IS A PAGE OBJECT", (20,20))

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Notebook Remove Pages Example")

        pannel  = wx.Panel(self)
        vbox    = wx.BoxSizer(wx.VERTICAL)
        hbox    = wx.BoxSizer(wx.HORIZONTAL)

        self.buttonRemove = wx.Button(pannel, id=wx.ID_ANY, label="DELETE", size=(80, 25))
        self.buttonRemove.Bind(wx.EVT_BUTTON, self.onButtonRemove)
        hbox.Add(self.buttonRemove)

        self.buttonInsert = wx.Button(pannel, id=wx.ID_ANY, label="CREATE", size=(80, 25))
        self.buttonInsert.Bind(wx.EVT_BUTTON, self.onButtonInsert)
        hbox.Add(self.buttonInsert)

        vbox.Add(hbox)

        self.Notebook3 = wx.Notebook(pannel)
        vbox.Add(self.Notebook3, 2, flag=wx.EXPAND)

        pannel.SetSizer(vbox)

        self.pageCounter = 0
        self.addPage()

    def addPage(self):
        self.pageCounter += 1
        page      = Page(self.Notebook3)
        pageTitle = "Page: {0}".format(str(self.pageCounter))
        self.Notebook3.AddPage(page, pageTitle)

    def onButtonRemove(self, event):   
        self.Notebook3.DeletePage(0)

    def onButtonInsert(self, event):   
        self.addPage()

if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()

# if __name__ == "__main__":
#     app = wx.App()
#     frame = MyFrame()
#     app.MainLoop()