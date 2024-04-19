from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata(project, "apples_fuji")
    df2 = project.processing_agridata(project, "apples_golden")
    df3 = project.processing_gdp()
    df4 = project.processing_inflazione()

    df_apples_fuji = merge_dfs(df1, df3, df4)
    df_apples_golden = merge_dfs(df2, df3, df4)

    project.final_steps(project, df_apples_fuji, "beginDate", "DatasetClean_apples_fuji.csv")
    project.final_steps(project, df_apples_golden, "beginDate", "DatasetClean_apples_golden.csv")
