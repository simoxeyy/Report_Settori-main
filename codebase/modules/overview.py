import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd
from codebase.modules.processing import extract_subset
from codebase.modules.Project import Project
from codebase.modules.classes import Visualization


class Overview(Visualization):
    def __init__(self, project: Project, settings, index) -> None:
        self.project = project
        self.settings = settings
        self.index = index

        # INFO ESTRATTE DA PROJECT
        self.dir_overview = project.dir_overview
        self.df = project.df

    def plot_line(self, df, columns, file_name, last_x_years):
        self.reset_matplotlib_settings()

        df = df.loc[:, columns]

        df = df[df.index.year > pd.Timestamp.now().year - last_x_years]

        fig, ax = plt.subplots(1)
        ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(md.DayLocator(interval=365))
        fig.autofmt_xdate()

        for col in df.columns:
            plt.plot(df.index, df[col], label=str(col.split("#")[1]))

        plt.xlabel("Data", fontsize=self.BIG)
        plt.ylabel("Prezzo", fontsize=self.BIG)
        plt.xticks(fontsize=self.MEDIUM, rotation=45)
        plt.yticks(fontsize=self.MEDIUM)
        plt.legend(fontsize=self.MEDIUM)

        self.close_figure(file_name)

    def execute_overview(self):
        extracted_columns = extract_subset(
            self.df,
            first_filter=["T"],
            second_filter=set(self.settings["columns"]),
        )

        self.plot_line(
            self.df,
            extracted_columns,
            self.dir_overview(f"image_{self.index}.png"),
            self.settings["year_back"],
        )
