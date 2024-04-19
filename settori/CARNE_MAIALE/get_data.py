from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata


def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO CARNE DI MAIALE (pigmeat_e)
    project.update_generic_agridata(
        project,
        "pigmeat/prices?pigClasses=E&beginDate=01/01/1950&endDate=31/12/2025",
        "pigmeat_e",
    )

    # UPDATE PREZZO CARNE DI MAIALE (pigmeat_s)
    project.update_generic_agridata(
        project,
        "pigmeat/prices?pigClasses=S&beginDate=01/01/1950&endDate=31/12/2025",
        "pigmeat_s",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione(project)

    # UPDATE DATI GDP
    project.update_dati_gdp(project)


