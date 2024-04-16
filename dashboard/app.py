# imports #
from shiny import App, ui
import plotly.express as px
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly, render_widget
import palmerpenguins
import seaborn as sns
import pandas as pd
from scipy import stats
from shinyswatch import theme
from ipyleaflet import Map
from faicons import icon_svg

theme.united()

# Provides the Palmer Penguins dataset
import palmerpenguins

# Load the Palmer Penguins dataset
penguins_df = palmerpenguins.load_penguins()

# Title to main page
ui.page_opts(title="Penguin Data MhamedM", fillable=True)


with ui.sidebar(open="open"):
       
    ui.input_selectize(
        "selected_attribute",
        "Select Attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )

    ui.input_selectize(
        "second_selected_attribute",
        "Select Second Attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )
    
    ui.input_numeric("Plotly_bin_count", "Bin Count", 40)

    ui.input_slider("seaborn_bin_count", "Seaborn Slider", 0, 100, 50)

    
    ui.input_select(  
        "species_counter", "Species Counter:",
        {"1A": "Adelie", "1B": "Gentoo", "1C": "Chinstrap"})



ui.a(
        "Github",
        href="https://github.com/Mhamedben/cintel-06-custom",
        target="_blank",
    )

with ui.layout_column_wrap():

    with ui.card(full_screen=True):
        ui.h2("Penguin")
        @render_widget
        def small_map(width="50%", height="150px"):
            return Map(center=(64.7743, -64.0538), zoom=10)
    
    with ui.value_box(showcase=icon_svg("sun"),width="50px", theme="bg-gradient-indigo-purple"):
        
        "Number of  Penguins"
        
        @render.ui
# Use ui.input_checkbox_group() to create a checkbox group input to filter the species
        def selected_species_count():
            selected_species_key = input.species_counter()
            selected_species_name = {"1A": "Adelie", "1B": "Gentoo", "1C": "Chinstrap"}.get(selected_species_key)
            if selected_species_name:
                species_count = len(penguins_df[penguins_df['species'] == selected_species_name])
                return species_count
            else:
                return "Please select a species."

with ui.layout_column_wrap():
    with ui.card(full_screen=True):
        ui.h4("Palmer Penguins Data Grid")

        @render.data_frame
        def penguins_data():
            return render.DataGrid(filtered_data())

    with ui.card(full_screen=True):
        ui.h4("Species Histogram")

        @render_plotly
        def plotly_histogram():
            return px.histogram(filtered_data(), x=input.selected_attribute(), nbins=input.Plotly_bin_count(), color="species")

with ui.layout_column_wrap():
    
    with ui.card(full_screen=True):
        ui.h4("Seaborn Histogram")
        @render.plot(alt="Seaborn Histogram")
        def seaborn_histogram():
            bins = input.seaborn_bin_count()
            ax = sns.histplot(data=filtered_data(), x=input.selected_attribute(), bins=bins, hue="species")
            ax.set_title("Palmer Penguins")
            ax.set_ylabel("Count")
            return ax

    with ui.card(full_screen=True):
        ui.h4("Plotly Scatter Plot")
        @render_plotly
        def plotly_scatterplot():
            return px.scatter(
                filtered_data(),
                title="Plotly Scatter Plot",
                x=input.selected_attribute(),
                y=input.second_selected_attribute(),
                color="species",
                labels={
                    "bill_length_mm": "Bill Length (mm)",
                    "body_mass_g": "Body Mass (g)",
                },
            )


@reactive.calc
def filtered_data():
    return penguins_df[penguins_df["species"].isin(input.Selected_Species_list())]
