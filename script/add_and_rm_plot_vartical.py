import numpy as np
import pandas as pd
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Select
from bokeh.palettes import Spectral4
from bokeh.plotting import figure

# Set up plot
plots = {}

# Set up widgets
file_path_input = TextInput(title="file path(*.csv):", value='')
plot_list = Select(value=None, title="", options=[""])

# Set up callbacks
def load_data(attrname, old, new):
    global plots
    
    file_path = str(new)
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        x_min = min(df["x"])-1
        x_max = max(df["x"])+1
        y_min = min([min(df[col]) for col in df.columns if "y" in col])-1
        y_max = max([max(df[col]) for col in df.columns if "y" in col])+1
        plot_name = "{}_{}".format(len(plots)+1, os.path.basename(file_path))
        plot = figure(height=400, width=400, title=plot_name,
                      tools="crosshair,pan,reset,save,wheel_zoom",
                      tooltips=[("Plot Name", "$name"), ("X", "@x"), ("Y", "@y")],
                      x_range=[x_min, x_max], y_range=[y_min, y_max])
        data = [(col, dict(x=df["x"], y=df[col])) for col in df.columns if "y" in col]
        for datum, color in zip(data, Spectral4):
            plot.line("x", "y", source=ColumnDataSource(data=datum[1]), color=color, legend_label=datum[0], name=datum[0])
        plots[plot_name] = plot
        plot_list.options = [""] + list(plots.keys())
        curdoc().add_root(plot)

def remove_data(attrname, old, new):
    global plots

    plot_name = str(new)
    plot_id = plots[plot_name].id
    plot_model = curdoc().get_model_by_id(plot_id)
    curdoc().remove_root(plot_model)
    del plots[plot_name]
    cur_no = 1
    new_plots = {}
    for plot_name in plots.keys():
        ref_no = plot_name.split("_")[0]
        if cur_no != ref_no:
            plot_name_wo_prefix = plot_name.replace(str(ref_no) + "_", "")
            cur_plot_name = "{}_{}".format(str(cur_no), plot_name_wo_prefix)
            plots[plot_name].title.text = cur_plot_name
            new_plots[cur_plot_name] = plots[plot_name]
        else:
            new_plots[plot_name] = plots[plot_name]
        cur_no += 1
    plots = new_plots
    plot_list.options = [""] + list(plots.keys())


file_path_input.on_change('value', load_data)
plot_list.on_change('value', remove_data)

# Set up layouts and add to document
curdoc().add_root(column(file_path_input, plot_list))
curdoc().title = "Sliders"
