from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata



# CHIAMATA API DA AGRIDATA PER DATI BURRO

def execute_update(project:ProjectAgridata):
    # UPDATE DEI DATI BURRO
    project.update_generic_agridata(
        project,
        "dairy/prices?products=BUTTER&beginDate=01/01/1950&endDate=31/12/2025",
        "burro",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione()

    # UPDATE DATI GDP
    project.update_dati_gdp()

