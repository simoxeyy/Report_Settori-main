import pandas as pd
import numpy as np
from datetime import datetime
from codebase.modules.Project import Project

class DynamicAgridata():
    def __init__(self, project:Project) -> None:
        self.project = project

        # INFO ESTRATTE DA PROJECT
        self.dir_forecasting = project.dir_forecasting
        self.dir_simulation = project.dir_simulation
        self.config = project.config
        self.serie = project.serie

    def get_error(self):
        # Calcolo dell'errore percentuale tra i valori originali e le historical predictions
        df_original = pd.read_csv(self.dir_forecasting("Y_train.csv"))
        df_original.columns = ["TIME", "y_original"]
        df_historical = pd.read_csv(
            self.dir_forecasting("Y_historical_forecasts.csv")
        )
        df_historical.columns = ["TIME", "y_historical"]

        df = pd.merge(df_original, df_historical, on="TIME", how="inner")
        df["Errore"] = ((df["y_historical"] - df["y_original"]) / df["y_original"]) * 100
        ERRORE = df["Errore"].abs().mean()
        ERRORE = round(ERRORE, 2)

        return ERRORE


    def get_variazione_percentuale(self):
        # Calcolo dell'andamento tra 3 mesi
        df_original = pd.read_csv(self.dir_forecasting("Y_train.csv"))
        df_original.columns = ["TIME", "value"]
        last_original_value = df_original["value"].iloc[-1]
        last_original_date = df_original["TIME"].iloc[-1]
        df_pred = pd.read_csv(self.dir_forecasting("Y_pred.csv"))
        df_pred.columns = ["TIME", "value"]
        last_predict_value = df_pred["value"].iloc[-1]
        last_predict_date = df_pred["TIME"].iloc[-1]

        VARIAZIONE_PERCENTUALE = (
            (last_predict_value - last_original_value) / last_original_value
        ) * 100
        VARIAZIONE_PERCENTUALE = round(VARIAZIONE_PERCENTUALE, 2)

        VARIAZIONE_DESCRIPTION = {}
        VARIAZIONE_DESCRIPTION1 = {}

        for language in self.config["pdf"]:
            # calcolo la descrizione della variazione percentuale
            treshold = 1
            if VARIAZIONE_PERCENTUALE > treshold:
                VARIAZIONE_DESCRIPTION[language] = self.config["pdf"][language][
                    "custom"
                ]["andamento_desc"][0]
                VARIAZIONE_DESCRIPTION1[language] = self.config["pdf"][language][
                    "custom"
                ]["andamento_desc1"][0]
            elif VARIAZIONE_PERCENTUALE <= treshold and VARIAZIONE_PERCENTUALE >= -treshold:
                VARIAZIONE_DESCRIPTION[language] = self.config["pdf"][language][
                    "custom"
                ]["andamento_desc"][1]
                VARIAZIONE_DESCRIPTION1[language] = self.config["pdf"][language][
                    "custom"
                ]["andamento_desc1"][1]

            elif VARIAZIONE_PERCENTUALE < treshold:
                VARIAZIONE_DESCRIPTION[language] = self.config["pdf"][language][
                    "custom"
                ]["andamento_desc"][2]
                VARIAZIONE_DESCRIPTION1[language] = self.config["pdf"][language][
                    "custom"
                ]["andamento_desc1"][2]

            else:
                print("Errore durante il calcolo dell variazioe")
                exit()

        return VARIAZIONE_DESCRIPTION, VARIAZIONE_PERCENTUALE, VARIAZIONE_DESCRIPTION1


    def get_shock(self):
        # Calcolo i datit per gli shock
        shock_data = []
        simulation_config = self.config["series"][self.serie]["simulation"]
        for setting in simulation_config["settings"]:
            nodi_source_string = ",".join(setting["nodi_sorgente"])
            nodi_target_string = ",".join(setting["nodi_target"])

            df = pd.read_excel(
                self.dir_simulation(
                    f"[{nodi_source_string}]__[{nodi_target_string}].xlsx"
                ),
                sheet_name="Array_Nuovi_Nodi_Raggiunti",
            )
            list_values = df[simulation_config["column_array_values_excel_CP"]].iloc[0][
                1:-1
            ]
            value1 = np.fromstring(list_values, sep=" ")[setting["shock_steps"] - 1]

            df = pd.read_excel(
                self.dir_simulation(
                    f"[{nodi_source_string}]__[{nodi_target_string}].xlsx"
                ),
                sheet_name="Array_Steps_Raggiungimento",
            )
            step_values = df[simulation_config["column_array_values_excel_CP"]].iloc[0][
                1:-1
            ]
            value2 = np.fromstring(step_values, sep=" ")[setting["shock_steps"] - 1]

            value3 = self.dir_simulation(f"[{nodi_source_string}]_cumulative.png")
            value4 = self.dir_simulation(
                f"[{nodi_source_string}]__[{nodi_target_string}]_cumulative.png"
            )

            shock_data.append([value1, value2, value3, value4])

        return shock_data


    def get_forecasting(self):
        values_in_historical = 10
        values_in_predictions = 5

        # Carico i dati passati di training
        df_old = pd.read_csv(self.dir_forecasting("Y_train.csv")).round(2)
        df_old["TIME"] = pd.to_datetime(df_old["TIME"], format="%Y-%m-%d")

        # Carico le previsioni
        df_new = pd.read_csv(self.dir_forecasting("Y_pred.csv")).round(2)
        df_new["TIME"] = pd.to_datetime(df_new["TIME"], format="%Y-%m-%d")

        # I dati futuri (generati dal modello) ma che in realtà sono passati li metto 
        # nei dati storici
        df_missing = df_new[df_new['TIME'] < datetime.today()]
        df_future = df_new[df_new['TIME'] >= datetime.today()]
        df_old = pd.concat([df_old, df_missing])

        # Tengo il formato che mi interessa nel pdf
        df_old["TIME"] = df_old["TIME"].dt.strftime("%d-%b-%Y")
        df_future["TIME"] = df_future["TIME"].dt.strftime("%d-%b-%Y")

        # Mantengo solo gli ultimi/primi dati
        df_old = df_old.tail(values_in_historical)
        df_future = df_future.head(values_in_predictions)

        # Converto in liste
        data_old = df_old.values.tolist()
        data_new = df_future.values.tolist()

        return data_old, data_new


    def execute(self):
        VARIAZIONE_DESCRIPTION, VARIAZIONE_PERCENTUALE, VARIAZIONE_DESCRIPTION1 = (
            self.get_variazione_percentuale()
        )
        ERRORE = self.get_error()
        SHOCK_DATA = self.get_shock()
        FORECASTING_OLD, FORCASTSING_NEW = self.get_forecasting()

        json_data = {
            "andamento_prezzo_desc": VARIAZIONE_DESCRIPTION,
            "andamento_prezzo_desc1": VARIAZIONE_DESCRIPTION1,
            "andamento_prezzo_value": VARIAZIONE_PERCENTUALE,
            "low_range": round(VARIAZIONE_PERCENTUALE - ERRORE, 2),
            "high_range": round(VARIAZIONE_PERCENTUALE + ERRORE, 2),
            "andamento_prezzo_errore": ERRORE,
            "shock": [
                {
                    "raggiungimento": shock[0],
                    "raggiungimento_nodo_target": shock[1],
                    "img_path": shock[2],
                    "img_path_2": shock[3],
                }
                for shock in SHOCK_DATA
            ],
            "data_prediction_old": FORECASTING_OLD,
            "data_prediction_new": FORCASTSING_NEW,
        }

        self.project.dynamic_info[self.serie] = json_data
    