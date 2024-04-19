from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd


def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df


def execute_processing(project: ProjectAgridata):
    df1 = project.processing_agridata(project, "pigmeat_e")
    df2 = project.processing_agridata(project, "pigmeat_s")
    df3 = project.processing_gdp()
    df4 = project.processing_inflazione()

    df_pigmeat_e= merge_dfs(df1, df3, df4)
    df_pigmeat_s= merge_dfs(df2, df3, df4)

    project.final_steps(project, df_pigmeat_e, "beginDate", "DatasetClean_pigmeat_e.csv")
    project.final_steps(project, df_pigmeat_s, "beginDate", "DatasetClean_pigmeat_s.csv")
