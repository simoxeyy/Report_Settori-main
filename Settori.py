from codebase.Projects.Agridata.ProjectAgridata import ProjectAgridata
from codebase.Projects.Eurostat.ProjectEurostat import ProjectEurostat
import pandas as pd
import numpy as np
import importlib.util
import json
import os
import warnings

warnings.filterwarnings("ignore")
pd.options.display.float_format = "{:.2f}".format
np.set_printoptions(suppress=True)


# I SETTORI che iniziano con ZZ__ sono da ignorare
# lista_settori = os.listdir('settori')
# lista_settori = [str(x).strip() for x in lista_settori]
# lista_settori.remove('.DS_Store')
# lista_settori = [x for x in lista_settori if 'ZZ__' not in x]
lista_settori = [
    # 'AGNELLO',
    #'BURRO',
    #'CARNE_MAIALE',
    # 'CARNE_MUCCA',
    #'LATTE',
    # 'MELE',
    #'PETTO_POLLO',
    'POMODORI',
    # 'UOVA',
     #'VINO'
    #"6343"
]

for settore in lista_settori:
    with open(f"settori/{settore}/config.json") as file:
        config_data = json.load(file)
        assert "type" in config_data, "Attributo type non presente nel config.json"
        type_source = config_data["type"]

    assert type_source in [
        "agridata",
        "eurostat",
    ], f"Source riconosciute (agridata, eurostat), ricevuto {type_source}"

    if type_source == "agridata":
        # Carico il modulo get_data dal rispettivo settore
        spec_get_data = importlib.util.find_spec(f"settori.{settore}.get_data")
        module_get_data = importlib.util.module_from_spec(spec_get_data)
        spec_get_data.loader.exec_module(module_get_data)

        # Carico il modulo processing_data dal rispettivo settore
        spec_processing_data = importlib.util.find_spec(
            f"settori.{settore}.processing_data"
        )
        module_processing_data = importlib.util.module_from_spec(spec_processing_data)
        spec_processing_data.loader.exec_module(module_processing_data)

        project = ProjectAgridata(
            settore,
            module_get_data.execute_update,
            module_processing_data.execute_processing,
            False,
            False,
        )
        project.execute()
        continue

    if type_source == "eurostat":
        project = ProjectEurostat(settore, True, True)
        project.execute()
        continue