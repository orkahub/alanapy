import pandas as pd
#import alanapy
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import LinearAxis, Range1d, HoverTool, Legend
import folium
import random

class ResultsParser:
    def __init__(self, response, *args, **kwargs):
        self.response = response
        self._df = None
        self._list = None
        super(ResultsParser, self).__init__(*args, **kwargs)

    @property
    def df(self):
        if self._df is None:
            self._df = pd.DataFrame(self.response.get('data', []))
        return self._df

    @property
    def list(self):
        if self._list is None:
            self._list = self.response.get('data', [])
        return self._list

class ProdResultsParser(ResultsParser):
    def plot(self, var="oil_rate", var2="oil_cum", plot_type="matplotlib"):
        """
        Plot data for multiple wells using either Matplotlib or Bokeh.

        Parameters:
        -----------
        var : str, optional
            The variable for the primary y-axis, default is "sum_oil_rate".

        var2 : str, optional
            The variable for the secondary y-axis, default is "sum_oil_cum".

        plot_type : str, optional
            The type of plot to generate. Accepts either "matplotlib" or "bokeh", default is "matplotlib".

        Returns:
        --------
        None
            The function generates a plot and does not return any value.

        Example:
        --------
        >>> plot(var="oil_rate", var2="oil_cum", plot_type="bokeh")

        """
        # labels_dict = {
        #     "sum_oil_rate": "Sum Oil Rate",
        #     "sum_oil_cum": "Sum Cumulative Oil"
        # }

        def get_singleton():
            import alanapy
            mysingle = alanapy.Singleton()
            return mysingle
        mysingle = get_singleton()
        var_settings = mysingle.master.plot_config.get(var, {})
        var2_settings = mysingle.master.plot_config.get(var2, {})

        label = var_settings.get('label', var)
        color = var_settings.get('color', 'blue')
        line_thickness = var_settings.get('line_thickness', 1)
        line_type = var_settings.get('line_type', 'solid')

        label2 = var2_settings.get('label', var2)
        color2 = var2_settings.get('color', 'blue')
        line_thickness2 = var2_settings.get('line_thickness', 1)
        line_type2 = var2_settings.get('line_type', 'solid')

        my_wells = list(set(self.df['well_name']))

        if plot_type == "matplotlib":
            fig, ax1 = plt.subplots()
            plt.title("Production for multiple wells")
            # Create primary axis for rate
            ax1.set_xlabel('Date')
            ax1.tick_params(axis='x', rotation=45)
            ax1.set_ylabel(label, color=color)

            # Create secondary axis for cumulative
            ax2 = ax1.twinx()
            ax2.set_ylabel(label2, color=color2)
            my_wells = list(set(self.df['well_name']))
            for well in my_wells:
                mydf = self.df[self.df["well_name"] == well]
                new_date = pd.to_datetime(mydf['date'])
                ax1.plot(new_date, mydf[var2])
                ax2.plot(new_date, mydf[var], linestyle="--")
            plt.legend(my_wells)
            plt.plot()
        elif plot_type == "bokeh":
            # Configure Bokeh plot
            p = figure(title="Production for multiple wells", x_axis_label='Date', x_axis_type="datetime",
                       y_axis_label=label)

            p.extra_y_ranges = {"secondary": None}
            p.add_layout(LinearAxis(y_range_name="secondary", axis_label=label2), 'right')

            legend_items = []

            for well in my_wells:
                mydf = self.df[self.df["well_name"] == well]
                new_date = pd.to_datetime(mydf['date'])

                l1 = p.line(new_date, mydf[var], line_width=line_thickness, legend_label=well)
                l2 = p.line(new_date, mydf[var2], line_width=line_thickness, line_dash="dashed", y_range_name="secondary")

                legend_items.append((well, [l1, l2]))

            legend = Legend(items=legend_items)
            p.add_layout(legend, 'right')

            show(p)
        else:
            print("Invalid plot_type specified.")

class WellResultsParser(ResultsParser):
    def map(self, plot_type="other", circle_variable=None, buble_color="green"):
        '''
            The `mapWellsFolium` function takes a dataframe (`df`) as input and generates a folium map with circle markers at the locations specified by the latitude and longitude values in the dataframe. Here is a step-by-step explanation of what each part of the function does:

        1. It extracts the latitude, longitude, and well names from the dataframe using list comprehensions.

        2. It calculates the average latitude and average longitude from the extracted latitudes and longitudes. These average values are used to center the map.

        3. A new folium map is created with the calculated center and a specified zoom level of 10.

        4. A loop iterates over the latitude, longitude, and well name lists simultaneously (using `zip`) and adds a circle marker at each location on the map. The size of each circle is determined randomly within a range of 5 to 15 (radius parameter of `CircleMarker`). The tooltip parameter is used to display the well name when the marker is hovered over.

        5. Finally, the function returns the generated map, which can be displayed in a Jupyter notebook or saved as an HTML file.

        The circle markers are colored blue with a fill color of blue as well, these properties are customizable according to your preferences.
        '''
        # Extract latitude and longitude data
        lst_latitudes = [float(well["latitude"]) for index, well in self.df.iterrows()]
        lst_longitudes = [float(well["longitude"]) for index, well in self.df.iterrows()]
        lst_wellnames = [str(well["well_name"]) for index, well in self.df.iterrows()]
        if plot_type == "pie":
            lst_water_ratios = [float(well["water_ratio"]) for index, well in
                                self.df.iterrows()]  # replace with your column name
            lst_oil_ratios = [float(well["oil_ratio"]) for index, well in
                              self.df.iterrows()]  # replace with your column name

        lst_buble_sizes = lst_latitudes
        if circle_variable is not None:
            lst_buble_sizes = [float(well[circle_variable]) for index, well in self.df.iterrows()]
            _min = min(lst_buble_sizes)
            _max = max(lst_buble_sizes)

        average_latitude = sum(lst_latitudes) / len(lst_latitudes)
        average_longitude = sum(lst_longitudes) / len(lst_longitudes)
        # Create a map centered on a specific location
        map_center = [average_latitude, average_longitude]
        map_zoom = 10  # Adjust the zoom level as needed
        map_osm = folium.Map(location=map_center, zoom_start=map_zoom)

        # Add markers for each point
        for latitude, longitude, well_name, buble_size in zip(lst_latitudes, lst_longitudes, lst_wellnames,
                                                              lst_buble_sizes):
            if plot_type == "circle":
                if circle_variable is None:
                    _buble_size = 10 # random.uniform(5, 15)
                else:
                    _buble_size = self.normalize(buble_size, _min, _max)
                folium.CircleMarker(location=[latitude, longitude],
                                    radius=_buble_size,
                                    tooltip=well_name,
                                    color=buble_color,
                                    fill=True,
                                    fill_color=buble_color
                                    ).add_to(map_osm)
            elif plot_type == "pie":
                pass
            else:
                folium.Marker(location=[latitude, longitude], tooltip=well_name).add_to(map_osm)

        # Display the map
        return map_osm

    def normalize(self, number, min_val, max_val, x=1, y=20):
        """
        Normalize a number from the range [min_val, max_val] to the range [x, y].

        :param number: The number to normalize
        :param min_val: The minimum value of the current range
        :param max_val: The maximum value of the current range
        :param x: The minimum value of the new range
        :param y: The maximum value of the new range

        :return: The normalized value
        """
        if max_val == min_val or y == x:
            raise ValueError("The range cannot be zero")

        normalized_value = ((number - min_val) / (max_val - min_val)) * (y - x) + x
        return normalized_value

    def pie(self, column="type"):
        type_counts = self.df[column].value_counts()
        labels = type_counts.index
        values = type_counts.values
        plt.pie(values, labels=labels)

class ProdResultsParserAggregated(ResultsParser):
    def plot(self, var="sum_oil_rate", var2="sum_oil_cum", plot_type="matplotlib"):
        """
        Plots aggregated production data for multiple wells.

        This method allows you to visualize well data using either Matplotlib or Bokeh.
        The plotted variables can be specified by the user.

        Parameters:
        - var (str): The variable to plot on the primary y-axis. Default is 'sum_oil_rate'.
            Options:
                "sum_oil_rate": Oil Rate
                "sum_oil_cum": Cumulative Oil
        - var2 (str): The variable to plot on the secondary y-axis. Default is 'sum_oil_cum'.
            Options:
                "sum_oil_rate": Oil Rate
                "sum_oil_cum": Cumulative Oil
        - plot_type (str): The type of plotting library to use. Default is 'matplotlib'.
            Options:
                "matplotlib": Use Matplotlib for plotting
                "bokeh": Use Bokeh for plotting

        Returns:
        - None: The function generates a plot.

        Example:
        >>> plot(var="sum_oil_rate", var2="sum_oil_cum", plot_type="bokeh")
        """

        labels_dict = {
            "sum_oil_rate": "Oil Rate",
            "sum_oil_cum": "Cumulative Oil"
        }

        new_date = pd.to_datetime(self.df['date'])

        if plot_type == "matplotlib":
            fig, ax1 = plt.subplots()
            plt.title("Aggregated production for multiple wells")
            ax1.set_xlabel('Date')
            ax1.tick_params(axis='x', rotation=45)
            ax1.set_ylabel(labels_dict[var], color='black')

            ax2 = ax1.twinx()
            ax2.set_ylabel(labels_dict[var2], color='black')

            ax1.plot(new_date, self.df[var2])
            ax2.plot(new_date, self.df[var], linestyle="--")

            plt.legend(["Aggregated Production"])
            plt.show()

        elif plot_type == "bokeh":
            p = figure(x_axis_type="datetime", title="Aggregated production for multiple wells", x_axis_label='Date',
                       y_axis_label=labels_dict[var])

            p.extra_y_ranges = {"secondary": Range1d(start=min(self.df[var2]), end=max(self.df[var2]))}
            p.add_layout(LinearAxis(y_range_name="secondary", axis_label=labels_dict[var2]), 'right')

            p.line(new_date, self.df[var], legend_label=labels_dict[var], color='navy', line_dash="dashed")
            p.line(new_date, self.df[var2], legend_label=labels_dict[var2], color='green', y_range_name="secondary")
            output_notebook()
            show(p)

class PetroResultsParser(ResultsParser):
    pass

