from codebase.modules.classes import Project
from codebase.retrive_data.retrive_data_api import (
    update_dati_gdp,
    update_dati_inflazione,
    update_generic_agridata,
)

# CHIAMATA API DA AGRIDATA PER DATI DELLE CIPOLLE
def execute_update(project: Project):
    # UPDATE PREZZO CIPOLLE
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=onions&beginDate=01/01/1950&endDate=31/12/2025",
        "onions",
    )

    # UPDATE DATI INFLAZIONE
    update_dati_inflazione(project)

    # UPDATE DATI GDP
    update_dati_gdp(project)
