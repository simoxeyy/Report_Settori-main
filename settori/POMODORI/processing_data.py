from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


# MERGE DI TUTTI I DATAFRAME IN UN UNICO DATASET
def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata(project, "tomatoes_cerises")
    df2 = project.processing_agridata(project, "tomatoes_grappes")
    df3 = project.processing_agridata(project, "tomatoes_rondes")
    df4 = project.processing_gdp()
    df5 = project.processing_inflazione()

    df_tomatoes_cerises = merge_dfs(df1, df4, df5)
    df_tomatoes_grappes = merge_dfs(df2, df4, df5)
    df_tomatoes_rondes = merge_dfs(df3, df4, df5)

    project.final_steps(project, df_tomatoes_cerises, "beginDate", "DatasetClean_tomatoes_cerises.csv")
    project.final_steps(project, df_tomatoes_grappes, "beginDate", "DatasetClean_tomatoes_grappes.csv")
    project.final_steps(project, df_tomatoes_rondes, "beginDate", "DatasetClean_tomatoes_rondes.csv")
