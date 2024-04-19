from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata

# CHIAMATA API DA AGRIDATA PER DATI CARNE DI POLLO


def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO CARNE DI POLLO
    project.update_generic_agridata(
        project,
        "poultry/prices?products=Breast Fillet&beginDate=01/01/1950&endDate=31/12/2025",
        "chicken",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione(project)

    # UPDATE DATI GDP
    project.update_dati_gdp(project)
