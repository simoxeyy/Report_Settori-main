from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata

# CHIAMATA API DA AGRIDATA PER DATI POMODORI VARIETA:
# Tomates cerises - Cherry tomatoes
# Tomates Grappes - Vine/trusses tomatoes
# Tomates rondes - Round tomatoes


def execute_update(project: ProjectAgridata):

    # UPDATE PREZZO POMODORI (tomatoes_cerises)
    project.update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=tomatoes&varieties=Tomates cerises - Cherry tomatoes&beginDate=01/01/1950&endDate=31/12/2025",
        "tomatoes_cerises",
    )
    # UPDATE PREZZO POMODORI (tomatoes_grappes)
    project.update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=tomatoes&varieties=Tomates Grappes - Vine/trusses tomatoes&beginDate=01/01/1950&endDate=31/12/2025",
        "tomatoes_grappes",
    )
    # UPDATE PREZZO POMODORI (tomatoes_rondes)
    project.update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=tomatoes&varieties=Tomates rondes - Round tomatoes&beginDate=01/01/1950&endDate=31/12/2025",
        "tomatoes_rondes",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione(project)

    # UPDATE DATI GDP
    project.update_dati_gdp(project)


