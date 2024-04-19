import pandas as pd
import numpy as np
import json, os, requests, glob
from codebase.modules.processing import extract_subset
from codebase.modules.Project import Project
from codebase.modules.classes import GraphType, DiffusionMethod
from codebase.modules.simulation import Simulation
from codebase.modules.network import Network
from codebase.modules.forecasting import Forecasting
from codebase.modules.overview import Overview
from codebase.Projects.Agridata.pdf_agridata import PDFGenerationAgridata
from codebase.Projects.Agridata.dynamic_agridata import DynamicAgridata


class ProjectAgridata(Project):
    def __init__(
        self, settore, fn_update, fn_process, update_data, process_data
    ) -> None:
        super().__init__(settore, update_data, process_data)
        self.fn_update = fn_update
        self.fn_process = fn_process

    # UPDATE DATA
    def update_generic_agridata(self, custom_url, dir_name):
        AGRIDATA_BASE_URL = "https://www.ec.europa.eu/agrifood/api/"
        response = requests.get(AGRIDATA_BASE_URL + custom_url)
        print(response.status_code)
        if response.status_code == 200:
            with open(
                self.dir_base_path(f"input_data/{dir_name}/raw_data.json"),
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(response.json(), file, indent=4, ensure_ascii=False)

    # PROCESSING DATA
    def processing_agridata(self, col_suffix):
        with open(
            self.dir_base_path(f"input_data/{col_suffix}/raw_data.json"),
            "r",
            encoding="utf-8",
        ) as f:
            json_data = json.load(f)
            df = pd.DataFrame(json_data)

        df = df[["memberStateCode", "price", "beginDate"]]
        df["price"] = df["price"].replace("#######", np.nan, regex=True)
        df["price"] = df["price"].replace(",", ".", regex=True)
        df["price"] = df["price"].replace("€", "", regex=True).astype(float)

        # Eseguo il pivot
        df = df.pivot_table(
            index="beginDate", columns="memberStateCode", values="price"
        )

        # aggiunto un suffisso
        df.columns = [f"T#{col}#{col_suffix}" for col in df.columns]

        if col_suffix == "burro":
            df = df.mask(df < 20, np.nan)

        df = df.reset_index()

        df["beginDate"] = pd.to_datetime(df["beginDate"], format="%d/%m/%Y")

        if col_suffix == "milk_raw":
            df = df[df["beginDate"].dt.day == 1]
        else:
            df = df[df["beginDate"].dt.weekday == 0]

        df = df.sort_values(by="beginDate")

        df = df.drop_duplicates(keep="first")

        df["year"] = df["beginDate"].dt.year
        df["month"] = df["beginDate"].dt.month

        return df

    def processing_agridata_wine(self, col_suffix):
        with open(
            self.dir_base_path(f"input_data/{col_suffix}/raw_data.json"),
            "r",
            encoding="utf-8",
        ) as f:
            json_data = json.load(f)
            df = pd.DataFrame(json_data)

        df = df[["description", "price", "beginDate"]]

        df["price"] = df["price"].replace("#######", np.nan, regex=True)
        df["price"] = df["price"].replace(",", ".", regex=True)
        df["price"] = df["price"].replace("€", "", regex=True).astype(float)

        df_dict = {"rosso": None, "bianco": None}

        for color_wine in ["rosso", "bianco"]:
            # Eseguo il pivot
            df_temp = df.pivot_table(
                index="beginDate", columns="description", values="price"
            )

            # Estraggo solo le colonne col il rispettivo colore vino e la colonna Altri vini
            valid_wines = [col for col in df_temp.columns if color_wine in col]

            df_temp = df_temp[valid_wines]
            df_temp.columns = [str(col).split(" ")[0] for col in df_temp.columns]
            df_temp.columns = [f"T#{col}#{col_suffix}" for col in df_temp.columns]

            df_temp = df_temp.reset_index()

            df_temp["beginDate"] = pd.to_datetime(df_temp["beginDate"], format="%d/%m/%Y")

            df_temp = df_temp[df_temp["beginDate"].dt.weekday == 0]

            df_temp = df_temp.sort_values(by="beginDate")

            df_temp = df_temp.drop_duplicates(keep="first")

            df_temp["year"] = df_temp["beginDate"].dt.year
            df_temp["month"] = df_temp["beginDate"].dt.month

            df_dict[color_wine] = df_temp

        return df_dict["rosso"], df_dict["bianco"]

    # LOAD DATA
    def load_agridata(self):
        BasePath = self.dir_base_path()
        for dataset_paths in glob.glob(os.path.join(BasePath, "Dataset*.csv")):
            filename = os.path.basename(dataset_paths)
            df = pd.read_csv(dataset_paths)
            df.columns = [str(col).strip() for col in df.columns]
            df = df.set_index("TIME")
            df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

            self.dfs[filename] = df


    # OVERVIEW
    def overview(self):
        json_info = self.config["series"][self.serie]["overview"]
        for index, settings in enumerate(json_info):
            Overview(self, settings, index).execute_overview()

    # NETWORK
    def network(self):
        Network(self).execute_network()

    # FORECASTING
    def forecasting(self):
        json_info = self.config["series"][self.serie]["forecasting"]

        target_columns = extract_subset(
            self.df,
            first_filter=["T"],
            second_filter=json_info["target_attribute_forecasting"],
        )

        forecasting = Forecasting(self, json_info, target_columns)
        forecasting.execute_forecasting()
        forecasting.plot_neural_network()

    # SIMULATION
    def simulation(self):
        for settings in self.config["series"][self.serie]["simulation"]["settings"]:
            simulation = Simulation(
                self,
                settings["nodi_sorgente"],
                settings["nodi_target"],
                GraphType.diGraph,
                DiffusionMethod.random,
            )
            simulation.execute_simulation()

    def set_dynamic_info(self):
        DynamicAgridata(self).execute()


    # EXECUTE PROGRAM
    def execute(self):
        self.fn_update_data(self.fn_update)
        self.fn_process_data(self.fn_process, self.load_agridata)

        for sub_dir in self.config["series"]:
            self.serie = sub_dir
            json_info = self.config["series"][self.serie]["generic"]
            self.df = self.dfs[json_info["dataset"]]

            self.overview()
            self.forecasting()
            self.network()
            self.simulation()
            self.set_dynamic_info()

        for language in self.languages:
            pdf = PDFGenerationAgridata(self, language)
            pdf.create_pdf()

