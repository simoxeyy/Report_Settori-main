from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata


# CHIAMATA API DA AGRIDATA PER DATI CARNE DI MANZO VARIETA:
# Adult male
# Calves slaughtered <8M


def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO CARNE (beef_adults)
    project.update_generic_agridata(
        project,
        "beef/prices?categories=Adult male indicative price&beginDate=01/01/1950&endDate=31/12/2025",
        "beef_adults",
    )

    # UPDATE PREZZO CARNE (beef_calves)
    project.update_generic_agridata(
        project,
        "beef/prices?categories=Calves slaughtered <8M&beginDate=01/01/1950&endDate=31/12/2025",
        "beef_calves",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione(project)

    # UPDATE DATI GDP
    project.update_dati_gdp(project)

