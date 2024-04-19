from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata

# CHIAMATA API DA AGRIDATA PER DATI DELLE UOVA VARIETA:
# Cage

def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO UOVA
    project.update_generic_agridata(
        project,
        "poultry/egg/prices?farmingMethods=cage&beginDate=01/01/1950&endDate=31/12/2025",
        "eggs_cage",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione(project)

    # UPDATE DATI GDP
    project.update_dati_gdp(project)
