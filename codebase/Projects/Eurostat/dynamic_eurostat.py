import pandas as pd
from codebase.modules.Project import Project
from datetime import date
from dateutil.relativedelta import relativedelta


class DynamicEurostat:
    def __init__(self, project: Project) -> None:
        self.project = project

        # INFO ESTRATTE DA PROJECT
        self.config = project.config
        self.serie = project.serie
        self.dir_forecasting = project.dir_forecasting

    def top_countries(self, df, json_info):
        current_date = date.today()
        current_date = current_date.replace(day=1)

        date_1_month_forward = str(current_date + relativedelta(months=1))
        date_2_month_forward = str(current_date + relativedelta(months=2))
        date_3_month_forward = str(current_date + relativedelta(months=3))

        df_temp = df.loc[
            [date_1_month_forward, date_2_month_forward, date_3_month_forward]
        ]
        df_temp = df_temp.T
        df_temp = df_temp.sort_values(by=date_1_month_forward, ascending=False)

        somma = df_temp.sum()
        somma.name = json_info["desc_sum_countries"]
        somma = somma.to_frame().T.reset_index(names="Country")

        df_temp = df_temp.head(json_info["top_n"])
        df_temp = df_temp.reset_index(names="Country")
        df_temp["Country"] = df_temp["Country"].apply(
            lambda x: x.split("#")[1] if "#" in x else x
        )

        concat = pd.concat([df_temp, somma]).round(2)

        # Rimuove le cifre decimali dai valori numerici
        numeric_cols = concat.select_dtypes(include=[float]).columns
        concat[numeric_cols] = concat[numeric_cols].astype(int)

        # Leggi il file Excel contenente la mappatura delle sigle ISO ai nomi dei paesi
        country_mapping_df = pd.read_excel('files\Lista_Codici_Paesi.xlsx', sheet_name='ValidCountries')

        # Creare un dizionario di mapping dalle sigle ISO ai nomi dei paesi
        mapping_dict = dict(zip(country_mapping_df['ISO 3166-1 alpha-2'], country_mapping_df['Nome abbreviato ITA']))

        # Mappare le sigle ISO ai nomi dei paesi nel DataFrame concat
        concat['Country'] = concat['Country'].map(lambda x: mapping_dict.get(x, x))

        values = concat.values.tolist()
        values.insert(0, concat.columns.values.tolist())

        # Formatta i valori numerici con l'apostrofo come separatore delle migliaia
        concat[numeric_cols] = concat[numeric_cols].applymap(lambda x: "{:,}".format(x))

        self.project.dynamic_info[self.serie] = values

    def execute(self):
        json_info = self.config["series"][self.serie]["pdf"]
        df = pd.read_csv(self.dir_forecasting("Y_pred.csv"), index_col="TIME")
        self.top_countries(df, json_info)
