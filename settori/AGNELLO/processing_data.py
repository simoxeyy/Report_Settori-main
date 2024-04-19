from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata("lamb_heavy")
    df2 = project.processing_agridata("lamb_light")
    df3 = project.processing_gdp()
    df4 = project.processing_inflazione()

    df_lamb_heavy = merge_dfs(df1, df3, df4)
    df_lamb_light = merge_dfs(df2, df3, df4)

    project.final_steps(df_lamb_heavy, "beginDate", "DatasetClean_lamb_heavy.csv")
    project.final_steps(df_lamb_light, "beginDate", "DatasetClean_lamb_light.csv")


