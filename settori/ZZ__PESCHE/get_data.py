from codebase.modules.classes import Project
from codebase.retrive_data.retrive_data_api import (
    update_dati_gdp,
    update_dati_inflazione,
    update_generic_agridata,
)
import requests
import json

# CHIAMATA API DA AGRIDATA PER DATI PESCHE VARIETA:
# Pêches jaunes - Cat. I - Size A/B Trays or packs of around 6-10 kg"
# Pêches blanches - Cat. I - Size A/B Trays or packs of around 6-10 kg"


def execute_update(project: Project):
    # UPDATE PREZZO PESCHE (peaches_jaunes)
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=peaches&varieties=Pêches jaunes - Cat. I - Size A/B Trays or packs of around 6-10 kg&beginDate=01/01/1950&endDate=31/12/2025",
        "peaches_jaunes",
    )

    # UPDATE PREZZO PESCHE (peaches_blanches)
    update_generic_agridata(
        project,
        "fruitAndVegetable/prices?products=peaches&varieties=Pêches blanches - Cat. I - Size A/B Trays or packs of around 6-10 kg&beginDate=01/01/1950&endDate=31/12/2025",
        "peaches_blanches",
    )

    # UPDATE DATI INFLAZIONE
    update_dati_inflazione(project)

    # UPDATE DATI GDP
    update_dati_gdp(project)
