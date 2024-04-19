from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata


def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO CARNE DI AGNELLO
    project.update_generic_agridata(
        project,
        "wine/prices?memberStateCodes=IT&beginDate=01/01/1950&endDate=01/01/2050",
        "wine",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione()

    # UPDATE DATI GDP
    project.update_dati_gdp()
