from pathlib import Path
import sys

pardir = Path(__file__).resolve().parent
if str(pardir) not in sys.path:
    sys.path.insert(0, str(pardir))
from utils.basic_plots import CategoryPlots, make_subplots, go, PostProcess as plots_post_process
from helper_tools.request_soup_data.soup import Soup
from helper_tools.request_soup_data.data_loader import Dataset, PostProcess as data_post_process
from helper_tools.more_plotly.save_plot import PlotSaver

import pandas as pd
import numpy as np
import re
from typing import Optional, Dict


cat_plots = CategoryPlots()

def get_engagement_data(report_url:str)->Optional[Dict[str, Dict[str, pd.DataFrame]]]:
    #url = "https://about.netflix.com/en/news/what-we-watched-a-netflix-engagement-report"

    doc_links = Soup(report_url).get_document_links()

    if not doc_links:
        return
        
    data_urls = [x.get("url") for x in doc_links if "what_we_watched" in x.get("url").lower() and x.get("url").endswith("xlsx")]

    if not data_urls:
        return

    data_url = data_urls[0]
    
    print(data_url)

    time_period = data_url.split("/")[-1].replace("What_We_Watched_A_Netflix_Engagement_Report_", "").replace(".xlsx", "")

    print(time_period)



    def extract_season_number(text:str)->Optional[int]:
        # The parentheses around \d+ create a capturing group
        match = re.search(r"Season (\d+)", text)
        
        if match:
            season_number = match.group(1) # Get the content of the first capturing group
            #print(f"Extracted season number: {season_number}")
            return season_number
        else:
            #print("Season number not found.")
            return
            
    data_dir = Path(__file__).resolve().parent/"data"
    file_name = data_dir/f"raw_{time_period}.xlsx"
    data = Dataset(doc_url = data_url).load_data()
    if not data:
        return
        
    with pd.ExcelWriter(data_dir/file_name, engine="openpyxl") as writer:
            
            for key, df in data.items():
                
                
                df.to_excel(writer, sheet_name=key.lower(), index=False)

    
    try:
        #engagement_data = data['Engagement']
        cleaned_out = {}
        for key, engagement_data in data.items():

            engagement_data = engagement_data.iloc[:,1:]

            engagement_data_clean = data_post_process.set_columns_from_index_and_drop_rows(engagement_data, col_index=4)

            engagement_data_clean = data_post_process.convert_data_types_of_cols(engagement_data_clean, "int")

            engagement_data_clean["release_date"] = pd.to_datetime(engagement_data_clean["release_date"], errors="coerce")

            engagement_data_clean:pd.DataFrame = (
                engagement_data_clean
                .assign(
                    month = engagement_data_clean["release_date"].dt.month_name(),
                    year = engagement_data_clean["release_date"].dt.year,
                    season_number = engagement_data_clean["title"].apply(lambda x:extract_season_number(x)),
                    show_name = engagement_data_clean["title"].apply(lambda x: re.sub(r": Season \d+", "", x))
                )
            )

            
            data_dir.mkdir(exist_ok=True)
            engagement_data_clean.to_csv(data_dir/f"{key.lower()}_{time_period}.csv", index=False)
            cleaned_out[key.lower()] = engagement_data_clean
        
        return {time_period: cleaned_out}
    
    except Exception as e:
        print("Failed to get engagement data")
        print(e)
        return
    

class NetflixEngagementReport:
    def __init__(self, report_url:str):
        self.report_url = report_url
        print(f"Engagement Report Url: {self.report_url}")
        self._engagement_data = get_engagement_data(self.report_url)
        if self._engagement_data:
            for time_period, data_dict in self._engagement_data.items():
                setattr(self, "time_period", time_period)
                setattr(self, "available_options", data_dict.keys())
                
    
    def get_df_for_option(self, option:str)->Optional[pd.DataFrame]:
        if option not in self.available_options:
            raise KeyError(f"Select from '{', '.join(self.available_options)}'")
        return self._engagement_data.get(self.time_period).get(option)
    
    #@classmethod
    def bar_plot_top_titles(self, option:str, top_n:int, by:str)->go.Figure:
        by = by.lower()
        if not self._assert_by_exists(option, by):
            return
        
        cat_plots.df = self.get_df_for_option(option).head(top_n)
        fig = cat_plots.plot_2_dimensional_data(plot_type="Bar", x_var="title", y_var = by, orientation="h", show_labels=True)
        fig.update_layout(yaxis = {'categoryorder' : 'total ascending'})
        return self._update_layout_add_source_to_fig(fig, 
                                                     title = f"Top {top_n} Most Watched Titles",
                                                     y = -0.15)
    
    def _assert_by_exists(self, option:str, by:str)->bool:
        df = self.get_df_for_option(option)
        by_lower = by.lower()
        if by_lower not in df.columns:
            print(f"Column '{by_lower}' does not exist in the dataframe")
            return False
        return True

    def bar_plot_top_shows(self, option:str, top_n:int, by:str)->go.Figure:

        by = by.lower()
        if not self._assert_by_exists(option, by):
            return
        
        cat_plots.df = (
            self.get_df_for_option(option)
            .groupby("show_name", 
                    as_index=False,
                    
                    )[by]
            .sum()
            .sort_values(by, 
                        ascending = False
                        )
            .reset_index(drop=True)
            .head(top_n)
            
        )
        
        
        fig = cat_plots.plot_2_dimensional_data(plot_type="Bar", x_var="show_name", y_var = by, orientation="h", show_labels=True)
        fig.update_layout(yaxis = {'categoryorder' : 'total ascending'})

        
        return self._update_layout_add_source_to_fig(fig, 
                                                     title = f"Top {top_n} most watched {option}",
                                                     y = -0.15)
    

    
    def _plot_metric_by_release_year(self, option:str, by:str, metric:str)->go.Figure:
        metric = metric.lower()
        if metric not in ["sum", "mean"]:
            raise KeyError(f"Invalid metric. Choose 'sum' or 'mean'")
        
        by = by.lower()
        if not self._assert_by_exists(option, by):
            return
    
        cat_plots.df = self.get_df_for_option(option)
        fig = cat_plots.group_and_plot(plot_type="Bar", group_by_var="year", group_metric=metric, y_var = by)
        
        return self._update_layout_add_source_to_fig(fig, 
                                                     title = f"Total {by} by release year" if metric=="sum" else f"Average {by} viewed by release year",
                                                     y = -0.1)
    

    def plot_average_hours_by_release_year(self, option:str)->go.Figure:
        return self._plot_metric_by_release_year(option, "hours_viewed", "mean")
    
    def plot_total_hours_by_release_year(self, option:str)->go.Figure:
        return self._plot_metric_by_release_year(option, "hours_viewed", "sum")
    
    def plot_average_views_by_release_year(self, option:str)->go.Figure:
        return self._plot_metric_by_release_year(option, "views", "mean")
    
    def plot_total_views_by_release_year(self, option:str)->go.Figure:
        return self._plot_metric_by_release_year(option, "views", "sum")
    

    def plot_number_of_shows_by_release_month_and_year(self,option:str)->go.Figure:
        cat_plots.df = (
            self.get_df_for_option(option)
            .loc[
            self.get_df_for_option(option)["release_date"].notna()
            ]["release_date"]
            .apply(
                lambda x: x.replace(day = 1)
            )
            .value_counts()
            .reset_index()
        )

        fig = cat_plots.plot_2_dimensional_data(plot_type="Bar", x_var="release_date", y_var="count")
        
        return self._update_layout_add_source_to_fig(fig, 
                                                     title = "Number of released shows by release month and year",
                                                     y = -0.1)
    

    def pie_plot_global_availability(self,option:str)->go.Figure:
        cat_plots.df = (
            self.get_df_for_option(option)["available_globally?"]
            .value_counts()
            .reset_index()
            
        )
        fig = cat_plots.group_and_plot(plot_type="Pie", group_by_var="available_globally?", group_metric="sum", y_var="count")
        fig.update_traces(textposition='inside', textinfo='percent+label')
       
        return self._update_layout_add_source_to_fig(fig, 
                                                     title = "Available globally?",
                                                     y = -0.1)
    

    def _update_layout_add_source_to_fig(self, fig, title, y, height=None, width=None)->go.Figure:
        fig = cat_plots._update_layout(fig, plot_title=title, height=height, width=width)
        fig = plots_post_process.add_source_to_plot(fig, 
                                            url = "https://about.netflix.com/en/news/what-we-watched-a-netflix-engagement-report", 
                                            text = f"What we watched? ({self.time_period})",
                                            y = y)
        return fig
    

    def subplot_figures(self, option:str, by:str, top_n:int=10)->go.Figure:
        by = by.lower()
        subplot = make_subplots(rows = 3, 
                        cols = 2, 
                        specs = [[{}, {}], 
                                 [{"type" : "pie"}, {}], 
                                 [{}, {}]],
                       subplot_titles=(
                           f"Top {top_n} most watched {option}",
                           f"Top {top_n} Most Watched Titles",
                           "Available globally?",
                            f"Number of released {option} by release month and year",
                            f"Average {by} by release year",
                            f"Total {by} by release year"
                       ))
        for trace in self.bar_plot_top_shows(option, top_n, by).data:
            subplot.add_trace(trace, row = 1, col = 1)
        

        for trace in self.bar_plot_top_titles(option, top_n, by).data:
            subplot.add_trace(trace, row = 1, col = 2)

        #subplot.update_layout(yaxis = {'categoryorder' : 'total ascending'})
        for trace in self.pie_plot_global_availability(option).data:
            subplot.add_trace(trace, row = 2, col = 1)

        for trace in self.plot_number_of_shows_by_release_month_and_year(option).data:

            subplot.add_trace(trace, row = 2, col = 2)

        if by == "hours_viewed":
            for trace in self.plot_average_hours_by_release_year(option).data:

                subplot.add_trace(trace, row = 3, col = 1)

            for trace in self.plot_total_hours_by_release_year(option).data:

                subplot.add_trace(trace, row = 3, col = 2)
        elif by == "views":
            for trace in self.plot_average_views_by_release_year(option).data:

                subplot.add_trace(trace, row = 3, col = 1)

            for trace in self.plot_total_views_by_release_year(option).data:

                subplot.add_trace(trace, row = 3, col = 2)



        #subplot = cat_plots._update_layout(subplot, height = 1400, width = 1800, #plot_title="Netflix Engagement Report"
        #                                   )
        #subplot.update_layout(yaxis = {'categoryorder' : 'total ascending'})
        for yaxis_name in subplot.layout:
            if yaxis_name.startswith('yaxis'):
                subplot.layout[yaxis_name].update(categoryorder='total ascending')


        subplot.update_xaxes(title = f"{by.title()}", row = 1, col = 1)
        subplot.update_xaxes(title = f"{by.title()}", row = 1, col = 2)
        subplot.update_xaxes(title = "Release Month and Year", row = 2, col = 2)
        subplot.update_xaxes(title = "Release Year", row = 3, col = 1)
        subplot.update_xaxes(title = "Release Year", row = 3, col = 2)

        subplot.update_yaxes(title = "Top Shows", row = 1, col = 1)
        subplot.update_yaxes(title = "Top Titles", row = 1, col = 2)
        subplot.update_yaxes(title = "Count of Shows", row = 2, col = 2)
        subplot.update_yaxes(title = f"Average {by.title()}", row = 3, col = 1)
        subplot.update_yaxes(title = f"Total {by.title()}", row = 3, col = 2)

        subplot.update_traces(showlegend = False)

        subplot.update_yaxes(tickangle = -45)
        fig = self._update_layout_add_source_to_fig(subplot,  f"Netflix Engagement Report - {option.upper()} ({self.time_period})<br><sup><b>By {by.upper()}</b></sup>", -0.3, height = 1400, width = 1800)
        PlotSaver(fig, base_path=pardir/"images", file_name = f"netflix_engagement_report_{option}_{self.time_period}_{by.lower()}", image_type="png", width = 1800, height=1400).save()
        return fig

    
def main(report_url:str)->None:
    engagement_report = NetflixEngagementReport(report_url)
    for by in ["hours_viewed", "views"]:
        for option in engagement_report.available_options:
            try:
                fig = engagement_report.subplot_figures(option, by, 10)
            except:
                continue
    return

if __name__ == "__main__":
    report_url = "https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2025"
    main(report_url)
    

