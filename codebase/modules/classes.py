from enum import Enum
import matplotlib.pyplot as plt

# Modalità diffusione messaggio
class DiffusionMethod(Enum):
    betweenness = 1
    eigencentrality = 2
    weight = 3
    random = 4


# Tipologia grafo
class GraphType(Enum):
    graph = 1  # (undirected, no paralled edges)
    diGraph = 2  # (directed, no paralled edges)
    multiGraph = 3  # (undirected, yes paralled edges)
    multiDiGraph = 4  # (directed, yes paralled edges)


class Visualization():
    SMALL = 30
    MEDIUM = 40
    BIG = 50

    def reset_matplotlib_settings(self):
        plt.rcdefaults()
        plt.rcParams.update(
            {
                "figure.autolayout": True,
                "figure.figsize": (45, 30),
                "font.size": 20,
            }
        )

    def close_figure(self, file_name):
        plt.savefig(file_name)
        plt.clf()
        plt.close()


