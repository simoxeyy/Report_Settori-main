from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
import pandas as pd

def merge_dfs(df1, df2, df3):
    df = pd.merge(df1, df2, left_on="year", right_on="year", how="left")
    df = pd.merge(df, df3, left_on="year", right_on="year", how="left")

    return df

def execute_processing(project: ProjectAgridata):
    df_rosso ,df_bianco  = project.processing_agridata_wine(project, 'wine')

    df3 = project.processing_gdp()
    df4 = project.processing_inflazione()

    df_bianco = merge_dfs(df_bianco, df3, df4)
    df_rosso = merge_dfs(df_rosso, df3, df4)
   
    project.final_steps(project, df_bianco, "beginDate", "DatasetClean_Bianco.csv")
    project.final_steps(project, df_rosso, "beginDate", "DatasetClean_Rosso.csv")

