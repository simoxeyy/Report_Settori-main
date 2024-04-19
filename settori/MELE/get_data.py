from codebase.modules.classes import Project
from codebase.retrive_data.retrive_data_api import (
    update_dati_gdp,
    update_dati_inflazione,
    update_generic_agridata,
)

###################################
# RIMUOVERE ULTIME 13 RIGHE
###################################

# CHIAMATA API DA AGRIDATA PER DATI MELE VARIETA:
# Fuji - Cat. I - Cal. 70-80
# Golden delicious - Cat. I - Cal. 70-80


def execute_update(project: Project):
    # UPDATE PREZZO MELE (apples_fuji)
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=apples&varieties=Fuji - Cat. I - Cal. 70-80&endDate=31/12/2025",
        "apples_fuji",
    )

    # UPDATE PREZZO MELE (apples_golden)
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=apples&varieties=Golden delicious - Cat. I - Cal. 70-80&beginDate=01/01/1950&endDate=31/12/2025",
        "apples_golden",
    )

    # UPDATE DATI INFLAZIONE
    update_dati_inflazione(project)

    # UPDATE DATI GDP
    update_dati_gdp(project)
