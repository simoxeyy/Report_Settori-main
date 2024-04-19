from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata

# CHIAMATA API DA AGRIDATA PER DATI CARNE DI AGNELLO VARIETA:
# HEAVY LAMB
# LIGHT LAMNB


def execute_update(project: ProjectAgridata):
    # UPDATE PREZZO CARNE DI AGNELLO
    # lamb_heavy
    project.update_generic_agridata(
        "sheepAndGoat/prices?category=Heavy Lamb&beginDate=01/01/1950&endDate=31/12/2025",
        "lamb_heavy",
    )

    # lamb_light
    project.update_generic_agridata(
        "sheepAndGoat/prices?category=Light Lamb&beginDate=01/01/1950&endDate=31/12/2025",
        "lamb_light",
    )

    # UPDATE DATI INFLAZIONE
    project.update_dati_inflazione()

    # UPDATE DATI GDP
    project.update_dati_gdp()

