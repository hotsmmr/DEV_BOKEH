import numpy as np
import pandas as pd
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, CheckboxGroup
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
        self.legend_list = []
        self.legend_items_org = []
        self.legend_list_check = CheckboxGroup(labels=[], active=[], visible=False)
    
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
        # keep the maximum configuration of legend-items in order to change item from invisible to visible
        self.legend_items_org = self.plot.legend.items
        self.legend_list = [legend_item.label["value"] for legend_item in self.legend_items_org]
        # set configurations of checkobox
        self.legend_list_check.labels = self.legend_list
        self.legend_list_check.active = [i for i in range(len(self.legend_list))]
        self.legend_list_check.visible = True
        self.legend_list_check.on_change('active', self.__update_legend)

    def get_plot(self):
        return self.plot

    def get_legend_list_check(self):
        return self.legend_list_check

    # Set up callback for checkbox
    def __update_legend(self, attrname, old, new):
        active_idx = new
        new_legend_items = []
        # append only active legend-items
        for idx, legend_item in enumerate(self.legend_items_org):
            if idx in active_idx:
                new_legend_items.append(legend_item)
        self.plot.legend.items = new_legend_items

        # renderes for plots corresponding to active legend-items will be visible
        for idx, legend_item in enumerate(self.legend_items_org):
            if idx in active_idx:
                for renderer in legend_item.renderers:
                    renderer.visible = True
            else:
                for renderer in legend_item.renderers:
                    renderer.visible = False

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
        curdoc().add_root(row(plots[plot_name].get_plot(), plots[plot_name].get_legend_list_check()))


file_path_input.on_change('value', load_data)

# Set up layouts and add to document
curdoc().add_root(file_path_input)
curdoc().title = "legend_test"
