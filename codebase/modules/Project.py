import json, os, requests
import pandas as pd
from pandas import DataFrame
from pandas.core.frame import DataFrame
from codebase.modules.processing import (
    denoising_media_mobile,
    interpola_valori_nulli,
    rimozione_eu_uk,
    rimuovi_colonne_null,
    rimuovi_outliers,
    verifica_dati_recenti,
)


class Project:
    def __init__(self, settore: str, update_data: bool, process_data: bool) -> None:
        self.serie: str | None = None
        self.update_data: bool = update_data
        self.process_data: bool = process_data
        self.df: DataFrame = None
        self.dfs: dict = {}
        self.dynamic_info: dict[str, DataFrame] = {}
        self.settore: str = settore
        self.config: dict = self.load_config()
        self.languages: list[str] = self.load_languages()


    # LOAD CONFIG FILE
    def load_config(self):
        with open(self.dir_base_path("config.json"), "r", encoding="utf-8") as file:
            return json.load(file)
  
    def load_languages(self):
        return list(self.config["pdf"].keys())

    # DATI INFLAZIONE
    def update_dati_inflazione(self):
        response = requests.get(
            "https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?downloadformat=excel"
        )
        PATH = "shared_data/inflazione/raw_data.xlsx"
        self.create_dir(PATH)
        with open(PATH, "wb") as output_file:
            output_file.write(response.content)

    def processing_inflazione(self):
        df = pd.read_excel(f"shared_data/gdp/raw_data.xlsx", skiprows=3)
        df = df.drop(columns=["Country Name", "Indicator Code", "Indicator Name"])
        df = df.set_index(keys="Country Code").T
        df = df[["BEL", "ITA", "DEU", "FRA", "ESP", "IRL"]]
        df.columns = [f"C#{col}#gdp" for col in df.columns]
        df = df.reset_index(names="year")
        df["year"] = df["year"].astype(int)
        df = df[df["year"] >= 1991]

        return df

    # UPDATE DATI GDP
    def update_dati_gdp(self):
        response = requests.get(
            "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?downloadformat=excel"
        )
        PATH = "shared_data/gdp/raw_data.xlsx"
        self.create_dir(PATH)
        with open(PATH, "wb") as output_file:
            output_file.write(response.content)

    def processing_gdp(self):
        df = pd.read_excel(f"shared_data/inflazione/raw_data.xlsx", skiprows=3)
        df = df.drop(columns=["Country Name", "Indicator Code", "Indicator Name"])
        df = df.set_index(keys="Country Code").T
        df = df[["BEL", "ITA", "DEU", "FRA", "ESP", "IRL"]]
        df.columns = [f"C#{col}#inflazione" for col in df.columns]
        df = df.reset_index(names="year")
        df["year"] = df["year"].astype(int)
        df = df[df["year"] >= 1991]

        return df

        # UPDATE DATI INFLAZIONE

    # PROCESSING DATA

    def final_steps(self, df, col_time, filename):
        # imposto la colonna col_time come index
        df = df.set_index(col_time)
        # Rinomino l'asse tempo
        df = df.rename_axis("TIME")

        # ordino la colonna relativa al tempo
        df = df.sort_index()

        if ("year" or "month") not in df.columns:
            print("Manca la colonna year e/o la colonna month")
            exit()

        # Estraggo mese e anno e li metto in prima posizione
        first_columns = ["year", "month"]
        other_columns = [x for x in df.columns if x not in first_columns]
        df = df[first_columns + other_columns]

        df = rimuovi_colonne_null(df)

        df = interpola_valori_nulli(df)

        df = verifica_dati_recenti(df)

        df = denoising_media_mobile(df)

        df = rimuovi_outliers(df)

        df = rimozione_eu_uk(df)

        df = df.round(2)

        df.to_csv(self.dir_base_path(filename))

        self.dfs[filename] = df

    # UPDATE AND PROCESSING CALL FUNCTIONS
    def check_execute_get_data(self):
        if self.update_data:
            while True:
                user_input = input("Proseguire con l'aggiornamento dei dati SI/NO: ")

                if user_input.upper() == "SI":
                    print("Continua con l'aggiornamento dei dati...")
                    return True  # Esci dal loop se l'utente ha inserito "SI"
                elif user_input.upper() == "NO":
                    print("Termina il programma.")
                    return False  # Termina il programma se l'utente ha inserito "NO"
                else:
                    print("Input non valido. Inserire 'SI' o 'NO'.")

        return False

    def fn_update_data(self, fn_get_data_from_api):
        if self.check_execute_get_data():
            fn_get_data_from_api(self)

    def fn_process_data(self, fn_processing, fn_load_data):
        if self.process_data:
            fn_processing(self)
        else:
            fn_load_data()

    # GESTIONE DELLE CARTELLE
    def create_dir(self, complete_path):
        os.makedirs(os.path.dirname(complete_path), exist_ok=True)
        return complete_path

    def create_path1(self, path):
        complete_path = os.path.join(os.getcwd(), "settori", self.settore, path)
        self.create_dir(complete_path)

        return complete_path

    def create_path2(self, section_dir, path):
        if self.serie != None:
            complete_path = os.path.join(
                os.getcwd(),
                "settori",
                self.settore,
                "output",
                section_dir,
                self.serie,
                path,
            )
        else:
            complete_path = os.path.join(
                os.getcwd(),
                "settori",
                self.settore,
                "output",
                section_dir,
                path,
            )
        self.create_dir(complete_path)
        return complete_path

    def dir_forecasting(self, path=""):
        return self.create_path2("forecasting", path)

    def dir_network(self, path=""):
        return self.create_path2("network", path)

    def dir_overview(self, path=""):
        return self.create_path2("overview", path)

    def dir_pdf(self, path=""):
        return self.create_path2("pdf", path)

    def dir_simulation(self, path=""):
        return self.create_path2("simulation", path)

    def dir_base_path(self, path=""):
        return self.create_path1(path)
