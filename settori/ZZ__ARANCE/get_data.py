from codebase.modules.classes import Project
from codebase.retrive_data.retrive_data_api import (
    update_dati_gdp,
    update_dati_inflazione,
    update_generic_agridata,
)


# CHIAMATA API DA AGRIDATA PER DATI ARANCE VARIETA:
# Navel
# Tarocco - Cat. I - Cal. 2-4"
# Valencia late - Cat. I - Cal. 2-4"


def execute_update(project: Project):
    # UPDATE PREZZO ARANCE
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=oranges&varieties=navel&beginDate=01/01/1950&endDate=31/12/2025",
        "oranges_navel",
    )

    # UPDATE DATI INFLAZIONE
    update_dati_inflazione(project)

    # UPDATE DATI GDP
    update_dati_gdp(project)
