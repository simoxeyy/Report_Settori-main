from darts.models import LinearRegressionModel
from darts.dataprocessing.transformers import Scaler
from pandas.core.series import Series
import matplotlib.pyplot as plt
from darts.utils.missing_values import fill_missing_values
from darts.utils.statistics import extract_trend_and_seasonality
from darts.utils.utils import ModelMode
from darts.timeseries import TimeSeries
from darts.timeseries import concatenate
import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from codebase.modules.Project import Project
from codebase.modules.classes import Visualization


class Forecasting(Visualization):
    def __init__(self, project:Project, json_info, target_columns) -> None:
        self.project = project
        self.json_info = json_info
        self.target_columns = target_columns

        self.training = None
        self.pred = None
        self.historic = None

        # INFO ESTRATTE DA PROJECT
        self.df = project.df
        self.dir_forecasting = project.dir_forecasting

    # VISUALIZATIONS
    def plot_pie(self, df, date_str, month, key_title):
        self.reset_matplotlib_settings()

        data = df.loc[date_str]
        data = data.where(data >= 0, 0)
        assert isinstance(data, Series)

        quote_original = data.div(data.sum()) * 100
        quote_filter = quote_original[quote_original > 5]
        quote_altri = pd.Series(
            [quote_original.sum() - quote_filter.sum()], index=["Other"]
        )
        quote_final = pd.concat([quote_filter, quote_altri])

        fig, ax = plt.subplots()
        wedges, texts, autopcts = ax.pie(
            quote_final.values,
            labels=quote_final.index,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontsize": 30},
        )  # Optional: customize start angle

        # Increase label font size
        for text in texts:
            text.set_fontsize(50)  # Adjust font size as desired
        # plt.pie(quote_final.values, labels=quote_final.index, textprops={'fontsize': 16})
        # plt.title(title, fontsize=BIG)

        PATH = self.dir_forecasting(f"pie_{month}_month.jpg")
        self.close_figure(PATH)

    def plot_bar(self, df, date_str, month, key_title):
        self.reset_matplotlib_settings()
        data = df.loc[date_str]
        data = data.where(data >= 0, 0)

        # Filtra solo i valori sopra la soglia
        data = data[data > data.max() * 0.05]

        # Ordina i dati in modo decrescente
        data = data.sort_values(ascending=False)

        assert isinstance(data, Series)
        plt.ticklabel_format(style="plain")
        bars = plt.bar(data.index, data.values)

        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                yval + 0.1,
                int(yval),
                ha="center",
                va="bottom",
                fontsize=self.SMALL,
            )

        # plt.title(title, fontsize=BIG)
        plt.xticks(fontsize=self.MEDIUM)
        plt.yticks(fontsize=self.MEDIUM)
        plt.xticks(rotation=45)

        PATH = self.dir_forecasting(f"bar_{month}_month.jpg")
        self.close_figure(PATH)

    def plot_graphs(self):
        df = pd.read_csv(self.dir_forecasting("Y_pred.csv"), index_col="TIME")
        df.columns = [str(col).split("#")[1] for col in df.columns]
        current_date = date.today()
        current_date = current_date.replace(day=1)

        date_1_month_forward = str(current_date + relativedelta(months=1))
        date_2_month_forward = str(current_date + relativedelta(months=2))
        date_3_month_forward = str(current_date + relativedelta(months=3))

        self.plot_bar(df, date_1_month_forward, 1, "forecasting_bar_1")
        self.plot_bar(df, date_2_month_forward, 2, "forecasting_bar_2")
        self.plot_bar(df, date_3_month_forward, 3, "forecasting_bar_3")
        self.plot_pie(df, date_1_month_forward, 1, "forecasting_pie_1")
        self.plot_pie(df, date_2_month_forward, 2, "forecasting_pie_2")
        self.plot_pie(df, date_3_month_forward, 3, "forecasting_pie_3")

    def plot_neural_network(self):
        self.reset_matplotlib_settings()

        df_train = self.training.pd_dataframe()
        serie_mean = df_train.mean()
        top_5_key = list(serie_mean.nlargest(5).index)

        # n = rescaled_Y_train.n_timesteps
        # rescaled_Y_train = rescaled_Y_train.drop_before(n-50)

        self.training[top_5_key].plot(label="Training")
        plt.gca().set_prop_cycle(None)
        self.pred[top_5_key].plot(label="Predictions", marker="o", markersize=10)
        # rescaled_historical_forecasts[top_5_key].plot(label="Historical forecasting")

        plt.ticklabel_format(style="plain", useOffset=False, axis="y")
        plt.xlabel("Tempo", fontsize=self.BIG)
        plt.ylabel("Prezzo", fontsize=self.BIG)
        plt.xticks(fontsize=self.MEDIUM, rotation=45)
        plt.yticks(fontsize=self.MEDIUM)
        plt.legend(fontsize=self.MEDIUM)

        self.close_figure(self.dir_forecasting("forecasting.png"))

    @staticmethod
    def filter_negative_values(arr):
        arr[arr < 0] = 0
        return arr

    def execute_forecasting(self):
        df = self.df.reset_index(names="TIME")
        ts = TimeSeries.from_dataframe(
            df,
            time_col="TIME",
            freq=self.json_info["frequency_pandas_format"],
        )

        ts = ts[self.target_columns]
        ts = ts.astype(np.float32)
        ts = fill_missing_values(
            ts,
            fill="auto",
            interpolate_kwargs={"method": "linear", "limit_direction": "both"},
        )

        scaler = Scaler()
        ts = scaler.fit_transform(ts)

        predictions = []
        historic_predictions = []

        for comp in ts.components:
            input_serie = ts[comp]
            trend, season = extract_trend_and_seasonality(
                input_serie, model=ModelMode.ADDITIVE, method="MSTL"
            )
            model_trend = LinearRegressionModel(lags=8, output_chunk_length=5)
            model_season = LinearRegressionModel(lags=8, output_chunk_length=5)
            model_trend.fit(trend)
            model_season.fit(season)
            pred_trend = model_trend.predict(series=trend, n=20)
            pred_trend = pred_trend.map(self.filter_negative_values) 
            pred_season = model_season.predict(series=season, n=20)
            pred = pred_trend + pred_season
            pred = pred.with_columns_renamed(col_names=['0'], col_names_new=[comp])
            pred = pred.map(self.filter_negative_values) 
            predictions.append(pred)

            # input_serie.plot(label='original')
            # pred.plot(label='predictions')
            # trend.plot(label='trend')
            # pred_trend.plot()
            # season.plot()
            # pred_season.plot()

            historic_pred = []
            for i in range(len(input_serie) // 2, len(input_serie)):
                pred_trend = model_trend.predict(series=trend[0:i], n=1)
                pred_season = model_season.predict(series=season[0:i], n=1)
                pred = pred_trend + pred_season
                pred = pred.with_columns_renamed(col_names=['0'], col_names_new=[comp])
                historic_pred.append(pred)

            historic_pred = concatenate(historic_pred, axis=0, ignore_time_axis=True)
            historic_predictions.append(historic_pred)

        predictions = concatenate(predictions, axis=1)
        historic_predictions = concatenate(historic_predictions, axis=1)
        
        rescaled_Y_train = scaler.inverse_transform(ts)
        rescaled_Y_pred = scaler.inverse_transform(predictions)
        rescaled_historical_forecasts = scaler.inverse_transform(historic_predictions)


        rescaled_Y_train.to_csv(
            self.dir_forecasting("Y_train.csv"),
        )
        rescaled_Y_pred.to_csv(
            self.dir_forecasting("Y_pred.csv"),
        )
        rescaled_historical_forecasts.to_csv(
            self.dir_forecasting("Y_historical_forecasts.csv"),
        )

        self.training = rescaled_Y_train
        self.pred = rescaled_Y_pred
        self.historic = rescaled_historical_forecasts