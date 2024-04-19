import random, os
import pandas as pd
import networkx as nx
import numpy as np
import itertools
from codebase.modules.classes import DiffusionMethod, GraphType, Visualization
import matplotlib.pyplot as plt
from codebase.modules.Project import Project



class Simulation(Visualization):
    def __init__(
        self, project:Project, nodi_sorgente, nodi_target, graph_type, diffusion_method
    ) -> None:
        # INFO ESTRATTE DA PROJECT
        self.project = project
        self.dir_simulation = project.dir_simulation
        self.config = project.config
        self.serie = project.serie
        self.G = project.G.copy()

        # INFO DELLA CLASSE
        self.nodi_sorgente = nodi_sorgente
        self.nodi_target = nodi_target
        self.nodi_sorgente_string = ",".join(self.nodi_sorgente)
        self.nodi_target_string = ",".join(self.nodi_target)
        self.graph_type = graph_type
        self.diffusion_method = diffusion_method
        self.threshold = 5
        self.threshold_random_percentage_pass = 0.2
        self.betweenness = nx.betweenness_centrality(project.G, normalized=True)
        self.eigencentrality = nx.eigenvector_centrality(project.G)
        self.nodi_raggiungibili = self.numero_totale_nodi_raggiungibli()
        self.sim_params = {}

    def plot_hist(
        self,
        y_data,
        valore_massimo,
        filename,
        nodi_sorgente=[],
        country=None,
    ):
        self.reset_matplotlib_settings()

        percentuali = [(valore / valore_massimo) * 100 for valore in y_data]
        max_y = max(y_data) * 1.2

        # Dati dell'istogramma (sostituisci con i tuoi dati)
        steps = [str(x) for x in range(1, self.sim_params['steps'] + 1)]
        # Crea l'istogramma
        plt.bar(steps, y_data, edgecolor="black", color="skyblue")

        for i, valore in enumerate(y_data):
            # Metto il numero sopra la barra
            plt.text(
                i,
                valore + max_y / 100,
                f"{percentuali[i]:.2f}%",
                ha="center",
                fontsize=self.MEDIUM,
            )

        if country == None:
            # Etichette degli assi
            plt.xlabel("Tempo", fontsize=self.BIG)
            plt.ylabel(
                f"N° nodi raggiunti (Max raggiungibili: {valore_massimo})",
                fontsize=self.BIG,
            )

            # Titolo del grafico
            plt.title(
                "Istogramma dei nodi raggiunti", fontsize=self.BIG, fontweight="bold"
            )

        if country != None:
            # Etichette degli assi
            plt.xlabel("Tempo", fontsize=self.BIG)
            plt.ylabel("N° raggiungimenti nodo target", fontsize=self.BIG)

            # Titolo del grafico
            plt.title(
                f"Nodi Sorgente: {','.join(nodi_sorgente)} -- Nodi Target: {country}",
                fontsize=self.BIG,
                fontweight="bold",
            )

        plt.xticks(fontsize=self.MEDIUM)
        plt.yticks(fontsize=self.MEDIUM)
        plt.ylim(top=max_y)

        self.close_figure(filename)

    def generate_files_nodi_iniziali_finali(self):
        df_iniziali = pd.DataFrame({"nodi_iniziali": self.nodi_sorgente})
        df_finali = pd.DataFrame({"nodi_finali": self.nodi_target})

        df_iniziali.to_excel("nodi_iniziali.xlsx", index=None)
        df_finali.to_excel("nodi_finali.xlsx", index=None)

    def generate_excel(self, output_data):
        # output_data è un dict dove ogni key è una lista formata da oggetti

        with pd.ExcelWriter(
            self.dir_simulation(
                f"[{self.nodi_sorgente_string}]__[{self.nodi_target_string}].xlsx"
            )
        ) as writer:
            pd.DataFrame(output_data["Array_Nuovi_Nodi_Raggiunti"]).round(2).to_excel(
                writer, sheet_name="Array_Nuovi_Nodi_Raggiunti"
            )

            pd.DataFrame(output_data["Array_Steps_Raggiungimento"]).round(2).to_excel(
                writer, sheet_name="Array_Steps_Raggiungimento"
            )

    def numero_totale_nodi_raggiungibli(self):
        nodi_raggiungibili = {}
        for node in self.nodi_sorgente:
            nodi_raggiungibili.update(
                nx.single_source_shortest_path_length(self.G, node)
            )
        return nodi_raggiungibili

    def infection_test(self, edge):
        source = edge[0]
        target = edge[1]

        # teoricamente dovrebbe sempre esserci il campo weight
        # può capitare che alcuni weight siano mancanti in quel caso ho np.nan
        # assegno 1 nel caso in cui weight non abbia un peso associato
        # i valori di weight hanno subito in precedenza un scaler tra 1 e 10
        weight = edge[2].get("weight", np.nan)
        weight = 1 if np.isnan(weight) else weight

        if self.diffusion_method == DiffusionMethod.random:
            prob = random.random()
            if prob < self.threshold_random_percentage_pass:
                return True

        if self.diffusion_method == DiffusionMethod.betweenness:
            prob = random.random()
            if (
                self.betweenness[source] * prob * self.sim_params['intensita_messaggio']
                >= self.betweenness[target] * self.threshold
            ):
                return True

        if self.diffusion_method == DiffusionMethod.eigencentrality:
            prob = random.random()
            if (
                self.eigencentrality[source]
                * prob
                * self.sim_params['intensita_messaggio']
                >= self.eigencentrality[target] * self.threshold
            ):
                return True

        if self.diffusion_method == DiffusionMethod.weight:
            prob = random.random()
            if (
                self.eigencentrality[source]
                * prob
                * self.sim_params['intensita_messaggio']
                * weight
                >= self.eigencentrality[target] * self.threshold
            ):
                return True

        return False

    def array_nuovi_nodi_raggiunti(self, info):
        array_values = np.round(
            [x / self.sim_params['n_simulations'] for x in self.sim_params['count_reached_nodes']], 2
        )
        array_values_P = np.round(
            [(x / len(self.nodi_raggiungibili)) * 100 for x in array_values], 2
        )
        array_values_C = np.round(np.cumsum(array_values), 2)
        array_values_CP = np.round(
            [(x / len(self.nodi_raggiungibili)) * 100 for x in array_values_C], 2
        )

        # versione normale
        self.plot_hist(
            array_values,
            len(self.nodi_raggiungibili),
            self.dir_simulation(f"[{self.nodi_sorgente_string}]"),
        )

        # versione cumulata
        self.plot_hist(
            array_values_C,
            len(self.nodi_raggiungibili),
            self.dir_simulation(f"[{self.nodi_sorgente_string}]_cumulative"),
        )

        return {
            **info,
            "nodi_sorgente": self.nodi_sorgente_string,
            "nodi_raggiungibili": len(self.nodi_raggiungibili),
            self.config["series"][self.serie]["simulation"][
                "column_array_values_excel"
            ]: array_values,
            self.config["series"][self.serie]["simulation"][
                "column_array_values_excel_P"
            ]: array_values_P,
            self.config["series"][self.serie]["simulation"][
                "column_array_values_excel_C"
            ]: array_values_C,
            self.config["series"][self.serie]["simulation"][
                "column_array_values_excel_CP"
            ]: array_values_CP,
        }

    def array_raggiungimento_steps(self, info):
        return_data = []
        for nodo_target, array_values in self.sim_params['count_reached_target_nodes'].items():
            array_values = np.round(array_values, 2)
            array_values_P = np.round(
                [(x / self.sim_params['n_simulations']) * 100 for x in array_values], 2
            )
            array_values_C = np.round(np.cumsum(array_values), 2)
            array_values_CP = np.round(
                [(x / self.sim_params['n_simulations']) * 100 for x in array_values_C], 2
            )

            self.plot_hist(
                array_values,
                self.sim_params['n_simulations'],
                self.dir_simulation(f"[{self.nodi_sorgente_string}]__[{nodo_target}]"),
                self.nodi_sorgente,
                nodo_target,
            )
            print(array_values_C)
            self.plot_hist(
                array_values_C,
                self.sim_params['n_simulations'],
                self.dir_simulation(
                    f"[{self.nodi_sorgente_string}]__[{nodo_target}]_cumulative"
                ),
                self.nodi_sorgente,
                nodo_target,
            )

            # Faccio la media degli step impiegati per raggiungere quel nodo
            temp = np.repeat(np.arange(len(array_values)) + 1, array_values)
            avg_steps_raggiungimento = (
                round(sum(temp) / len(temp), 2) if len(temp) > 0 else None
            )

            raggiungimento_last_step = round(
                ((sum(array_values) / self.sim_params['n_simulations']) * 100), 2
            )

            return_data.append(
                {
                    **info,
                    "nodi_sorgente": self.nodi_sorgente_string,
                    "nodi_target": nodo_target,
                    "Raggiungimento Last Step (%)": raggiungimento_last_step,
                    "Steps Raggiungimento (Media)": avg_steps_raggiungimento,
                    self.config["series"][self.serie]["simulation"][
                        "column_array_values_excel"
                    ]: array_values,
                    self.config["series"][self.serie]["simulation"][
                        "column_array_values_excel_P"
                    ]: array_values_P,
                    self.config["series"][self.serie]["simulation"][
                        "column_array_values_excel_C"
                    ]: array_values_C,
                    self.config["series"][self.serie]["simulation"][
                        "column_array_values_excel_CP"
                    ]: array_values_CP,
                }
            )
        return return_data

    def start_simulation(self):
        # ad ogni step conteggio i nodi che ho infettato (nuovi)
        count_reached_nodes = [0] * self.sim_params['steps']

        # per ogni nodo target conteggio quante volte in un determinato step è stato infettato
        count_reached_target_nodes = {
            target_node: [0] * self.sim_params['steps']
            for target_node in self.nodi_target
        }

        # vado ad eseguire le n simulations
        for _ in range(self.sim_params['n_simulations']):
            G2 = self.G.copy()

            # vado ad assegnare ai nodi infetti la proprietà infected = True
            for infected_node in self.nodi_sorgente:
                G2.nodes[infected_node]["infected"] = True

            # inizialmente assegno al primo step i nodi che sono già infetti
            count_reached_nodes[0] += len(self.nodi_sorgente)

            # per ogni simulazione eseguo n steps
            for step in range(self.sim_params['steps']):
                infected_nodes = [
                    node
                    for node, data in G2.nodes(data=True)
                    if data.get("infected", False) == True
                ]

                # ciclo su tutti i nodi infetti
                for node in infected_nodes:
                    # Estraggo gli edge validi in base al tipo di grafo (diretto o non diretto)
                    edges = (
                        G2.out_edges(node, data=True)
                        if G2.is_directed()
                        else G2.edges(node, data=True)
                    )

                    for edge in edges:
                        targetNode = edge[1]
                        # considero solamente i nodi che non sono già infettati
                        if G2.nodes[targetNode].get("infected", False) == False:
                            infected = self.infection_test(edge)

                            # Se il messaggio è passato vado ad infattare il nodo e
                            # aumento il contatore degli infettati in quello step
                            if infected:
                                G2.nodes[targetNode]["infected"] = True
                                count_reached_nodes[step] += 1

                            # Se il messaggio è passato ed ha infettato un nodo target incremento il contatore
                            if infected and targetNode in self.nodi_target:
                                count_reached_target_nodes[targetNode][step] += 1

        self.sim_params['count_reached_nodes'] = count_reached_nodes
        self.sim_params['count_reached_target_nodes'] = count_reached_target_nodes

    def execute_simulation(self):
        # Ad ogni simulation aggiunto un dictionary agli array con le info da inserire nel excel
        output_data = {
            "Array_Nuovi_Nodi_Raggiunti": [],
            "Array_Steps_Raggiungimento": [],
        }

        sim_config = self.config["series"][self.serie]["simulation"]
        # Vado a eseguire tutte le combinazioni dei parametri
        combinations = list(
            itertools.product(
                sim_config["list_steps"],
                sim_config["list_intensita_messaggi"],
                sim_config["list_simulazioni"],
            )
        )
        for steps, intensita_messaggio, n_simulations in combinations:
            self.sim_params = {
                'steps':steps,
                'intensita_messaggio':intensita_messaggio,
                'n_simulations':n_simulations
            }


            # -----------------------------------
            info = {
                "Numero Step":  self.sim_params['steps'],
                "Numero Simulazioni":  self.sim_params['n_simulations'],
                "Intensità messaggio": self.sim_params['intensita_messaggio'],
                "Graph Type": self.graph_type.name,
                "Metodologia diffusione": self.diffusion_method.name,
                "Threshold_random_percentage_pass": self.threshold_random_percentage_pass,
                "Threshold": self.threshold,
            }

            # varibili assegnate all'oggetto simulation una volta completata la simulazione
            # simulation.count_reached_nodes
            # simulation.count_reached_target_nodes
            self.start_simulation()

            # Quanti nodi mediamente sono infettati ad ogni steps
            output_data["Array_Nuovi_Nodi_Raggiunti"].append(
                self.array_nuovi_nodi_raggiunti(info)
            )

            # Per ogni nodo target ho un array che mi indica quante volte quel nodo
            # è stato raggiunto nel determinato steps (posizione nell'array)
            output_data["Array_Steps_Raggiungimento"].extend(
                self.array_raggiungimento_steps(info)
            )

        # generate_files_nodi_iniziali_finali(nodi_sorgente, nodi_target)
        self.generate_excel(output_data)