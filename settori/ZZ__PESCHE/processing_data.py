from codebase.processing.processing_agridata import processing_agridata
from codebase.modules.classes import Project
from codebase.processing.processing_shared import processing_gdp, processing_inflazione
from codebase.modules.processing import final_steps
import pandas as pd
import numpy as np


def merge_dfs(df1, df2, df3, df4):
    media = df1["IT_peaches_jaunes"].mean()
    df1["DE_peaches_jaunes"] = np.nan
    df1["BE_peaches_jaunes"] = np.nan
    df1["DE_peaches_jaunes"].fillna(media, inplace=True)
    df1["BE_peaches_jaunes"].fillna(media, inplace=True)

    media1 = df2["ES_peaches_blanches"].mean()
    df2["DE_peaches_blanches"] = np.nan
    df2["BE_peaches_blanches"] = np.nan
    df2["DE_peaches_blanches"].fillna(media1, inplace=True)
    df2["BE_peaches_blanches"].fillna(media1, inplace=True)

    df = pd.merge(
        df1,
        df2,
        left_on=["beginDate", "year", "month"],
        right_on=["beginDate", "year", "month"],
        how="outer",
    )
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df4, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: Project):
    df1 = processing_agridata(project, "peaches_jaunes")
    df2 = processing_agridata(project, "peaches_blanches")
    df3 = processing_gdp()
    df4 = processing_inflazione()

    df = merge_dfs(df1, df2, df3, df4)
    df = final_steps(project, df, "beginDate", "DatasetClean.csv")
