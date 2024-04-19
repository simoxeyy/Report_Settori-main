import matplotlib.pyplot as plt
import networkx as nx
import networkx as nx
import seaborn as sb
from sklearn.preprocessing import MinMaxScaler
from networkx.drawing.nx_pylab import draw
from codebase.modules.Project import Project
from codebase.modules.classes import GraphType
from codebase.modules.processing import extract_subset
from codebase.modules.classes import Visualization



class Network(Visualization):
    def __init__(self, project:Project) -> None:
        self.project = project

        # INFO ESTRATTE DA PROJECT
        self.dir_network = project.dir_network
        self.df = project.df


    def plot_network(self, G):
        self.reset_matplotlib_settings()

        pos = nx.spring_layout(G, k=1.5)
        draw(
            G,
            pos,
            with_labels=True,
            node_size=20000,
            font_color="white",
            font_size=self.MEDIUM,
            arrowsize=50,
            arrows=True,
        )

        self.close_figure(self.dir_network("graph_network.png"))

    def plot_heatmap(self, df):
        self.reset_matplotlib_settings()

        df = df.round(2)
        color = sb.diverging_palette(20, 220, as_cmap=True)
        s = sb.heatmap(df, cmap=color, annot=False, vmin=0, vmax=1)

        # Edit legend label size
        cax = s.figure.axes[-1]
        cax.tick_params(labelsize=self.MEDIUM)

        plt.title("Correlation Matrix", fontsize=self.BIG, fontweight="bold")
        plt.xlabel("")
        plt.ylabel("")
        plt.xticks(fontsize=self.MEDIUM, rotation=90)
        plt.yticks(fontsize=self.MEDIUM, rotation=0)

        self.close_figure(self.dir_network("heatmap.png"))

    def corr_pearson(self, df, threshold=None):
        # Calcolo la matrice con la correlazione di Pearson
        matrix = df.corr(method="pearson").round(2)

        # Disegno la mappa di colore della matrice
        self.plot_heatmap(matrix)

        df_links = (
            matrix.reset_index()
            .rename(columns={"index": "source"})
            .melt(id_vars="source", var_name="target", value_name="weight")
        )
        if threshold is not None:
            df_links = df_links[abs(df_links["weight"]) > threshold]

        df_links = df_links[df_links["source"] != df_links["target"]]

        return df_links

    def dataframe_preparation(self, df, graph_type):
        # rimuovo spazi bianchi ad inizio e fine nome
        df["source"] = df["source"].str.strip()
        df["target"] = df["target"].str.strip()

        # nel caso in cui ho un grafo che non supporti gli archi paralleli vado ad eliminare i duplicati
        # (verrà mantenuto il primo)
        if graph_type in [GraphType.graph, GraphType.diGraph]:
            df.drop_duplicates(subset=["source", "target"], inplace=True)

        # se non è presente la colonna weight assegno 1 a tutti gli archi
        if "weight" not in df.columns:
            df["weight"] = 1

        # Se i weight non sono tutti uguali
        if len(set(df["weight"].values)) > 1:
            # faccio lo scaler tra 0.1 e 1
            scaler = MinMaxScaler(feature_range=(1, 10))
            df["weight"] = scaler.fit_transform(df["weight"].values.reshape(-1, 1))

        return df

    def create_Graph(self, df, graph_type):
        # GRAFI NON DIRETTI
        if graph_type == GraphType.graph:
            return nx.from_pandas_edgelist(
                df, create_using=nx.Graph(), edge_attr="weight"
            )

        if graph_type == GraphType.multiGraph:
            return nx.from_pandas_edgelist(
                df,
                create_using=nx.MultiGraph(),
                edge_attr="weight",
            )

        # GRAFI DIRETTI
        if graph_type == GraphType.diGraph:
            return nx.from_pandas_edgelist(
                df,
                create_using=nx.DiGraph(),
                source="source",
                target="target",
                edge_attr="weight",
            )

        if graph_type == GraphType.multiDiGraph:
            return nx.from_pandas_edgelist(
                df,
                source="source",
                target="target",
                create_using=nx.MultiDiGraph(),
                edge_attr="weight",
            )

    def execute_network(self):
        df_temp = self.df.copy()
        graph_type = GraphType.diGraph

        df_temp = df_temp[extract_subset(self.df, first_filter=["T"])]

        # Rimozione della sottostringa "_butter" dai nomi delle colonne
        df_temp.columns = [str(col).split("#")[1] for col in df_temp.columns]

        df_links = self.corr_pearson(df_temp, 0.25)
        df_links.to_csv(self.dir_network("source_target_weight.csv"), index=None)

        df_links = self.dataframe_preparation(df_links, graph_type)
        G = self.create_Graph(df_links, graph_type)

        self.plot_network(G)

        self.project.G = G
