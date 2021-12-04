import pandas as pd
import os
import math
import glob

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, TextInput, Select, Button
from bokeh.palettes import Spectral4
from bokeh.plotting import figure

# Set up plot
plots = {}
plot_rows = []
root_path = ""
file_path = ""
remove_target = ""

# Set up widgets
root_path_input = TextInput(title="root path:", value='')
file_list = Select(value=None, title="", options=[])
plot_list = Select(value=None, title="", options=[])
all_load_button = Button(label="All Load", button_type="success", width=100, height_policy='fit')
load_button = Button(label="Load", button_type="success", width=100, height_policy='fit')
all_remove_button = Button(label="All Remove", button_type="warning", width=100, height_policy='fit')
remove_button = Button(label="Remove", button_type="warning", width=100, height_policy='fit')

# Set up callbacks
def set_root_path(attrname, old, new):
    global root_path
    root_path = str(new)
    file_list.options = glob.glob(os.path.join(root_path, "**", "*.csv"), recursive=True)
    file_list.value = file_list.options[0] if len(file_list.options) > 0 else ""

def set_load_target(attrname, old, new):
    global file_path
    file_path = str(new)
    
def load_data():
    global plots
    global plot_rows
    
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        x_min = min(df["x"])-1
        x_max = max(df["x"])+1
        y_min = min([min(df[col]) for col in df.columns if "y" in col])-1
        y_max = max([max(df[col]) for col in df.columns if "y" in col])+1
        plot_name = "{}_{}".format(len(plots)+1, os.path.basename(file_path))
        plot = figure(height=250, width=250, title=plot_name,
                      tools="crosshair,pan,reset,save,wheel_zoom",
                      tooltips=[("Plot Name", "$name"), ("X", "@x"), ("Y", "@y")],
                      x_range=[x_min, x_max], y_range=[y_min, y_max])
        data = [(col, dict(x=df["x"], y=df[col])) for col in df.columns if "y=" in col]
        for datum, color in zip(data, Spectral4):
            plot.line("x", "y", source=ColumnDataSource(data=datum[1]), color=color, legend_label=datum[0], name=datum[0])
        plots[plot_name] = plot
        plot_list.options = list(plots.keys())
        plot_list.value = plot_list.options[0]
        if len(plot_rows) == 0:
            plot_rows.append(row(children=[plots[plot_name]]))
            curdoc().add_root(plot_rows[-1])
        else:
            if len(plot_rows[-1].children) < 4:
                children = []
                for child in plot_rows[-1].children:
                    children.append(child)
                children.append(plots[plot_name])
                row_id = plot_rows[-1].id
                row_model = curdoc().get_model_by_id(row_id)
                curdoc().remove_root(row_model)
                del plot_rows[-1]
                plot_rows.append(row(children=children))
                curdoc().add_root(plot_rows[-1])
            else:
                plot_rows.append(row(children=[plots[plot_name]]))
                curdoc().add_root(plot_rows[-1])

def all_load_data():
    for file in file_list.options:
        set_load_target("", "", file)
        load_data()

def set_remove_target(attrname, old, new):
    global remove_target
    remove_target = str(new)

def remove_data():
    global plots
    global plot_rows

    if remove_target not in plots:
        return

    del plots[remove_target]

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
    plot_list.options = list(plots.keys())
    plot_list.value = plot_list.options[0] if len(plot_list.options) > 0 else ""

    for plot_row in plot_rows:
        row_id = plot_row.id
        row_model = curdoc().get_model_by_id(row_id)
        curdoc().remove_root(row_model)
    
    plot_rows = []

    row_num = math.ceil(len(plots)/4)
    for row_idx in range(row_num):
        cur_plots = list(plots.keys())[(row_idx*4):(row_idx*4)+4]
        children = [plots[cur_plot] for cur_plot in cur_plots]
        plot_rows.append(row(children=children))
        curdoc().add_root(plot_rows[-1])

def all_remove_data():
    for i in range(len(plot_list.options)):
        set_remove_target("", "", plot_list.options[0])
        remove_data()

root_path_input.on_change('value', set_root_path)
file_list.on_change('value', set_load_target)
plot_list.on_change('value', set_remove_target)
all_load_button.on_click(all_load_data)
load_button.on_click(load_data)
all_remove_button.on_click(all_remove_data)
remove_button.on_click(remove_data)

# Set up layouts and add to document
curdoc().add_root(row(column(root_path_input, row(file_list, load_button), row(plot_list, remove_button)), all_load_button, all_remove_button))
curdoc().title = "plot_test"
