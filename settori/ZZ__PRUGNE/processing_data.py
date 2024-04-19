from codebase.modules.classes import Project
from codebase.processing.processing_agridata import processing_agridata
from codebase.processing.processing_shared import processing_gdp, processing_inflazione
from codebase.modules.processing import final_steps
import pandas as pd


def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: Project):
    df1 = processing_agridata(project, "plums")
    df2 = processing_gdp()
    df3 = processing_inflazione()

    df = merge_dfs(df1, df2, df3)
    df = final_steps(project, df, "beginDate", "DatasetClean.csv")
