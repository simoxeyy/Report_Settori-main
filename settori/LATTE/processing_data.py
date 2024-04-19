from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


def merge_dfs(df1, df3, df4):
    df = pd.merge(df1, df3, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df4, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata(project, "milk_raw")
    df3 = project.processing_gdp()
    df4 = project.processing_inflazione()

    df = merge_dfs(df1, df3, df4)
    project.final_steps(project, df, "beginDate", "DatasetClean_milk.csv")
