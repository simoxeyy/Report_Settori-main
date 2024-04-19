from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata



# CHIAMATA API DA AGRIDATA PER DATI LATTE TIPOLOGIA:
# Raw Milk

def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO DEL LATTE
    project.update_generic_agridata(
        project,
        "rawMilk/prices?products=raw%20milk&beginDate=01/01/2005&endDate=31/12/2025",
        "milk_raw",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione(project)

    # UPDATE DATI GDP
    project.update_dati_gdp(project)
