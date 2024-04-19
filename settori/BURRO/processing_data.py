from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


def merge_dfs(df1, df3, df4):
    df = pd.merge(df1, df3, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df4, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata(project, "burro")
    df2 = project.processing_gdp()
    df3 = project.processing_inflazione()

    df = merge_dfs(df1, df2, df3)
    project.final_steps(project, df, "beginDate", "DatasetClean.csv")
