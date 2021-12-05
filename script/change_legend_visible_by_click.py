import numpy as np
import pandas as pd
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput
from bokeh.palettes import Spectral4
from bokeh.plotting import figure

# Set up plot
plots = {}
class Plot():
    X_COL = "x"
    Y_COL = "y="
    PLOT_SIZE = {
        "H":400,
        "W":400
    }
    TOOL_TIPS = [
        ("Plot Name", "$name"),
        ("X", "@x"),
        ("Y", "@y")
    ]

    def __init__(self, name, df_data):
        self.name = name
        self.df_data = df_data
        self.plot = None
    
    def gen_plot(self):
        data_x = self.df_data[self.X_COL]
        col_y = self.df_data.columns

        # set range of plot data
        ## x-axis is only set from "x" column
        ## y-axis is set from "y=*" columns
        self.x_min = min(data_x)-1
        self.x_max = max(data_x)+1
        self.y_min = min([min(self.df_data[col]) for col in col_y if self.Y_COL in col])-1
        self.y_max = max([max(self.df_data[col]) for col in col_y if self.Y_COL in col])+1

        # create plot, and set data
        ## x-data is only set from "x" column
        ## y-data is set from each "y=*" column
        ## legend-label is set from each "y=*" column name
        self.plot = figure(height=self.PLOT_SIZE["H"], width=self.PLOT_SIZE["W"], title=self.name,
                           tools="crosshair,pan,reset,save,wheel_zoom",
                           tooltips=self.TOOL_TIPS,
                           x_range=[self.x_min, self.x_max], y_range=[self.y_min, self.y_max]
                    )
        data = [(col, dict(x=data_x, y=self.df_data[col])) for col in col_y if self.Y_COL in col]
        for datum, color in zip(data, Spectral4):
            self.plot.line("x", "y", source=ColumnDataSource(data=datum[1]), color=color, legend_label=datum[0], name=datum[0])

    def set_legend_config(self):
        self.plot.legend.location = "top_left"
        self.plot.legend.click_policy = "hide"

    def get_plot(self):
        return self.plot

# Set up widgets
file_path_input = TextInput(title="file path(*.csv):", value='')

# Set up callbacks
def load_data(attrname, old, new):
    global plots
    
    file_path = str(new)
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        # plot-name is set from file-name and the loaded order
        plot_name = "{}_{}".format(len(plots)+1, os.path.basename(file_path))
        plot_obj = Plot(plot_name, df)
        plot_obj.gen_plot()
        plot_obj.set_legend_config()
        plots[plot_name] = plot_obj
        curdoc().add_root(plots[plot_name].get_plot())


file_path_input.on_change('value', load_data)

# Set up layouts and add to document
curdoc().add_root(file_path_input)
curdoc().title = "legend_test"
