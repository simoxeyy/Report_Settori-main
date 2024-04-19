from codebase.modules.classes import Project
from codebase.retrive_data.retrive_data_api import (
    update_dati_gdp,
    update_dati_inflazione,
    update_generic_agridata,
)


# CHIAMATA API DA AGRIDATA PER DATI DELLE PRUGNE
def execute_update(project: Project):
    # UPDATE PREZZO PRUGNE
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=plums&beginDate=01/01/1950&endDate=31/12/2025",
        "plums",
    )

    # UPDATE DATI INFLAZIONE
    update_dati_inflazione(project)

    # UPDATE DATI GDP
    update_dati_gdp(project)
