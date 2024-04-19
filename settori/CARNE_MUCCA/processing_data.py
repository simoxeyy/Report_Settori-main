from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata(project, "beef_adults")
    df2 = project.processing_agridata(project, "beef_calves")
    df3 = project.processing_gdp()
    df4 = project.processing_inflazione()

    df_beef_adults = merge_dfs(df1, df3, df4)
    df_beef_calves = merge_dfs(df2, df3, df4)

    project.final_steps(project, df_beef_adults, "beginDate", "DatasetClean_beef_adults.csv")
    project.final_steps(project, df_beef_calves, "beginDate", "DatasetClean_beef_calves.csv")
