import os
import requests
import pandas as pd
from codebase.modules.processing import extract_subset
from codebase.modules.Project import Project
from codebase.modules.forecasting import Forecasting
from codebase.Projects.Eurostat.dynamic_eurostat import DynamicEurostat
from codebase.Projects.Eurostat.pdf_eurostat import PDFGenerationEurostat


class ProjectEurostat(Project):
    # Set dei paesi EU
    set_eu_iso = set(
        pd.read_excel(
            "files/EU_ISO.xlsx",
            sheet_name="Sheet1",
            na_filter=False,
        )["ISO_code"]
    )
    # Set di tutti i paesi
    set_iso_countries = set(
        pd.read_excel(
            "files/Lista_Codici_Paesi.xlsx",
            sheet_name="ValidCountries",
            na_filter=False,
        )["ISO 3166-1 alpha-2"]
    )
    # Set dei paesi non EU
    set_not_eu_sio = set.difference(set_iso_countries, set_eu_iso)

    def __init__(self, settore, update_data, process_data) -> None:
        super().__init__(settore, update_data, process_data)

    # UPDATE DATA
    def get_data_from_api(self):
        # https://ec.europa.eu/eurostat/databrowser/view/ds-018995/legacyMultiFreq/table?lang=en
        # products = ["6343","63411", "63432", "82153", "00121", "00122", "00131", "00139", "0015", "02231"]
        flow = "c[flow]=2&"
        freq = "c[freq]=M&"
        indicators = "c[indicators]=VALUE_IN_EUROS&"
        reporter = "c[reporter]=IT,EU27_2020&"
        partner = "c[partner]=AD,AE,AF,AG,AI,AL,AM,AN,AO,AQ,AR,AS,AT,AU,AW,AZ,BA,BB,BD,BE,BF,BG,BH,BI,BJ,BL,BM,BN,BO,BQ,BR,BS,BT,BV,BW,BY,BZ,CA,CC,CD,CF,CG,CH,CI,CK,CL,CM,CN,CO,CR,CS,CU,CV,CW,CX,CY,CZ,DD,DE,DJ,DK,DM,DO,DZ,EC,EE,EG,EH,ER,ES,ET,FI,FJ,FK,FM,FO,FR,GA,GB,GD,GE,GF,GH,GI,GL,GM,GN,GP,GQ,GR,GS,GT,GU,GW,GY,HK,HM,HN,HR,HT,HU,ID,IE,IL,IN,IO,IQ,IR,IS,IT,JM,JO,JP,KE,KG,KH,KI,KM,KN,KP,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,LT,LU,LV,LY,MA,MD,ME,MG,MH,MK,ML,MM,MN,MO,MP,MQ,MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NC,NE,NF,NG,NI,NL,NO,NP,NR,NU,NZ,OM,PA,PE,PF,PG,PH,PK,PL,PM,PN,PS,PT,PW,PY,QA,QP,QQ,QR,QS,QU,QV,QW,QX,QY,QZ,RE,RO,RU,RW,SA,SB,SC,SD,SE,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SR,SS,ST,SU,SV,SX,SY,SZ,TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,TP,TR,TT,TV,TW,TZ,UA,UG,UM,US,UY,UZ,VA,VC,VE,VG,VI,VN,VU,WF,WS,XA,XB,XC,XK,XL,XM,XO,XP,XR,XS,XZ,YD,YE,YT,YU,ZA,ZM,ZW&"
        time = "c[TIME_PERIOD]=ge:1999&"
        BASE_URL = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/3.0/data/dataflow/ESTAT/ds-018995/+?"
        END_URL = "format=csvdata&formatVersion=2.0&compress=false"

        # Aggiorna il parametro product con il codice prodotto corrente
        product = f"c[product]={self.settore}&"

        URL = (
            BASE_URL
            + flow
            + freq
            + indicators
            + product
            + reporter
            + partner
            + time
            + END_URL
        )

        response = requests.get(URL)

        folder_path = f"settori/{self.settore}/input_data"
        os.makedirs(folder_path, exist_ok=True)

        # Controlla se la richiesta ha avuto successo
        if response.ok:
            with open(os.path.join(folder_path, "raw_data.csv"), "wb") as file:
                file.write(response.content)
        else:
            print(
                f"Richiesta fallita per il prodotto {self.settore} con stato: {response.status_code}"
            )

    # PROCESSING DATA
    def processing_data(self):
        print("Caricamento del file raw_data.csv...")
        df = pd.read_csv(f"settori/{self.settore}/input_data/raw_data.csv")

        print("Filtro dei partner validi...")
        df = df[df["partner"].isin(list(self.set_iso_countries))]

        print("Selezione delle colonne rilevanti...")
        df = df[["reporter", "partner", "TIME_PERIOD", "OBS_VALUE"]]

        print("Rinominazione dei valori EU27_2020...")
        df["reporter"] = df["reporter"].replace("EU27_2020", "EU")

        print("Conversione della colonna TIME_PERIOD in formato data...")
        df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
        df = df.rename(columns={"TIME_PERIOD": "TIME"})
        df["year"] = df["TIME"].dt.year
        df["month"] = df["TIME"].dt.month

        print("Creazione dei dataset EU e IT...")
        df_eu = df[df["reporter"] == "EU"]
        df_it = df[df["reporter"] == "IT"]

        print("Pivot dei dataframe...")
        df_eu = df_eu.pivot_table(
            index=["TIME", "year", "month"], columns="partner", values="OBS_VALUE"
        )
        df_it = df_it.pivot_table(
            index=["TIME", "year", "month"], columns="partner", values="OBS_VALUE"
        )

        print("Rinominazione delle colonne...")
        df_eu.columns = [f"T#{col}#EU" for col in df_eu.columns]
        df_it.columns = [f"T#{col}#IT" for col in df_it.columns]

        print("Reset dell'indice...")
        df_eu = df_eu.reset_index()
        df_it = df_it.reset_index()

        print("Caricamento dei dati aggiuntivi...")
        df_inflazione = self.processing_inflazione()
        df_gdp = self.processing_gdp()

        print("Unione dei dataframe...")
        df_eu = pd.merge(left=df_eu, right=df_inflazione, on="year", how="left")
        df_eu = pd.merge(left=df_eu, right=df_gdp, on="year", how="left")

        df_it = pd.merge(left=df_it, right=df_inflazione, on="year", how="left")
        df_it = pd.merge(left=df_it, right=df_gdp, on="year", how="left")

        print("Salvataggio dei dati...")
        self.final_steps(df_eu, "TIME", "DatasetCleanEU.csv")
        self.final_steps(df_it, "TIME", "DatasetCleanIT.csv")

    # LOAD DATA
    def load_processed_data(self):
        print("Caricamento del file DatasetCleanEU.csv...")
        df_eu = pd.read_csv(self.dir_base_path("DatasetCleanEU.csv"))
        df_eu.columns = [str(col).strip() for col in df_eu.columns]

        print("Caricamento del file DatasetCleanIT.csv...")
        df_it = pd.read_csv(self.dir_base_path("DatasetCleanIT.csv"))
        df_it.columns = [str(col).strip() for col in df_it.columns]

        print("Impostazione degli indici...")
        df_eu = df_eu.set_index("TIME")
        df_it = df_it.set_index("TIME")

        print("Conversione dell'indice in formato data...")
        df_eu.index = pd.to_datetime(df_eu.index, format="%Y-%m-%d")
        df_it.index = pd.to_datetime(df_it.index, format="%Y-%m-%d")

        print("Aggiunta dei dataframe al progetto...")
        self.dfs = {"DatasetCleanEU.csv": df_eu, "DatasetCleanIT.csv": df_it}

    # FORECASTING
    def forecasting(self):
        json_info = self.config["series"][self.serie]["forecasting"]
        self.df = self.dfs[json_info["dataset"]]

        second_filter = (
            list(self.set_eu_iso)
            if json_info["is_target_eu"]
            else list(self.set_not_eu_sio)
        )

        target_columns = extract_subset(
            self.df,
            first_filter=["T"],
            second_filter=second_filter,
        )

        forecasting = Forecasting(self, json_info, target_columns)
        forecasting.execute_forecasting()
        forecasting.plot_neural_network()
        forecasting.plot_graphs()

    # SET DYNAMIC INFO
    def set_dynamic_info(self):
        DynamicEurostat(self).execute()


    # EXECUTE PROGRAM
    def execute(self):
        self.fn_update_data(self.get_data_from_api)
        self.fn_process_data(self.processing_data, self.load_processed_data)

        for sub_dir in self.config["series"]:
            self.serie = sub_dir
            self.forecasting()
            self.set_dynamic_info()

        for language in self.languages:
            pdf = PDFGenerationEurostat(self, language)
            pdf.create_pdf()
