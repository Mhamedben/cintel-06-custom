###Final####
# imports #
import pandas as pd
import seaborn as sns
import plotly.express as px
import palmerpenguins
import random
from shiny import App, ui
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly, render_widget
from scipy import stats
from shinyswatch import theme
from ipyleaflet import Map
from faicons import icon_svg
from datetime import datetime
from collections import deque

# Provides the Palmer Penguins dataset
import palmerpenguins

# Load the Palmer Penguins dataset
penguins_df = palmerpenguins.load_penguins()

# Title to main page
ui.page_opts(title="Penguins Data MhamedM", fillable=True)
   
UPDATE_INTERVAL_SECS: int = 8

DEQUE_SIZE: int = 8

reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
    
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    
    temp = round(random.uniform(-10, 20 ), 1)
    penguin_activity = round(random.uniform(50,300))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "penguin_activity": penguin_activity, "timestamp": timestamp}

    
    reactive_value_wrapper.get().append(new_dictionary_entry)

    deque_snapshot = reactive_value_wrapper.get()
    
    df = pd.DataFrame(deque_snapshot)
    
    latest_dictionary_entry = new_dictionary_entry
   
    return deque_snapshot, df, latest_dictionary_entry

### Add a sidebar for user interaction

with ui.sidebar(open="open"):
   
    ui.h2("Sidebar")

    column_mapping = {
    "Bill Length (mm)": "bill_length_mm",
    "Bill Depth (mm)": "bill_depth_mm",
    "Flipper Length (mm)": "flipper_length_mm",
    "Body Mass (g)": "body_mass_g"}
   
    ui.input_selectize("selected_attribute", "Selected Attribute",
                       list(column_mapping.keys()))
    
    ui.input_slider("seaborn_bin_count", "Seaborn Bin Count", 0, 100, 50)

    # ui.input_checkbox_group() to create a checkbox group input to filter the species
    ui.input_checkbox_group("selected_species_list", "Species",
                            ["Adelie", "Gentoo", "Chinstrap"], selected=["Adelie", "Gentoo", "Chinstrap"])

    
    # ui.input_checkbox_group() to create a checkbox group input to filter the islands
    ui.input_checkbox_group("selected_island_list", "Island",
                            ["Torgersen", "Biscoe", "Dream"], selected= ["Torgersen", "Biscoe", "Dream"])
    
    ui.input_checkbox("show_sex", "Show Sex")

    ui.hr()

    # Use ui.a() to add a hyperlink to the sidebar
    ui.a("GitHub", href="https://github.com/Mhamedben/cintel-06-custom/blob/main/dashboard/app.py", target="_blank")

 
with ui.layout_columns():
   with ui.value_box(
        showcase=icon_svg("sun"),
        theme="Sunshine Serenade",
    ):
    "Pittsburgh Temperature"

    @render.text
    def display_temp():
       
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        temperature = latest_dictionary_entry['temp']
        return f"{temperature} C"
    
    @render.text
    def temperature_status():
    
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        temperature = latest_dictionary_entry['temp']
        if temperature < 0:
            
            return "Colder day"
        else:
            
            return "Warmer day" 
            

with ui.layout_column_wrap():
    with ui.card(full_screen=True):
        ui.h2("Pittsburgh")
        @render_widget
        def small_map(width="50%", height="100px"):
            return Map(center=(40.4406, -79.9959), zoom=6)

with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

        @render.text
        def active_penguins():
          """Get the latest reading and return a active penguin string"""
          deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
          activity = latest_dictionary_entry['penguin_activity']  
          return f"{activity} Active Penguins"


@reactive.calc
def filtered_data():
    return penguins_df[
        (penguins_df["species"].isin(input.selected_species_list())) &
        (penguins_df["island"].isin(input.selected_island_list()))
    ]

with ui.navset_card_tab(id="tab"):
    with ui.nav_panel("Recent Readings"):

        # Create a function to render the Plotly histogram
         @render.data_frame
         def display_df():
             
             
             deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
             pd.set_option('display.width', None)        
             return render.DataGrid( df,width="100%")

            

    with ui.nav_panel("Seaborn Histogram"):
        # Create a function to render the Seaborn histogram
        @render.plot
        def seaborn_histogram():
            selected_attribute = input.selected_attribute()
            seaborn_bin_count = input.seaborn_bin_count()
            show_sex = input.show_sex()

            title = f"Seaborn Histogram for {selected_attribute}"
            if show_sex:
                title = " (Sex Included)"

            sns.set(style="whitegrid")  # Set Seaborn style
            seaborn_histogram = sns.histplot(
                filtered_data(),
                x=column_mapping[selected_attribute],
                hue="sex" if show_sex else "species",
                bins=seaborn_bin_count,
            )
            # Update titles and labels
            seaborn_histogram.set_title(title)

            return seaborn_histogram

    with ui.nav_panel("Scatterplot"):
        ui.card_header("Plotly Scatterplot: Species")

        @render_plotly
        def ploty_scatterplot():
            selected_species_list = input.selected_species_list()
            filtered_df = penguins_df[penguins_df["species"].isin(selected_species_list)]
            plotly_scatter = px.scatter(
                filtered_df,
                x="body_mass_g",
                y="bill_length_mm",
                color="species",
                size_max=7,
                labels={
                    "body_mass_g": "Body Mass (g)",
                    "bill_length_mm": "Bill Length(mm)",
                },
            )
            return plotly_scatter
