from reportlab.platypus import PageBreak, Spacer, Table
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from datetime import datetime
from reportlab.platypus import PageBreak, Spacer
from reportlab.lib.pagesizes import A4
from codebase.modules.PDF import FooterCanvas, MyDocTemplate
from codebase.modules.Project import Project
from codebase.modules.PDF import PDF_Sostituzioni, PDF_Utils


class PDFGenerationAgridata(PDF_Sostituzioni, PDF_Utils):
    def __init__(self, project:Project, language:str) -> None:
        project.serie = None
        PDF_Utils.__init__(self, project, language)
        PDF_Sostituzioni.__init__(self, project, language)
        self.project = project
        self.language = language

        # INFO ESTRATTE DA PROJECT
        self.config = project.config
        self.serie = project.serie
        self.dir_base_path = project.dir_base_path
        self.dir_overview = project.dir_overview
        self.dir_forecasting = project.dir_forecasting
        self.dir_network = project.dir_network
        self.dir_pdf = project.dir_pdf


    def create_table(self, serie, key):
        ts = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                # ("TEXTCOLOR", (0, 0), (-1, 0), colors.red),
                ("ALIGNMENT", (0, 0), (-1, -1), "CENTER"),
            ]
        )
        self.dynamic_info[serie][key].insert(
            0,
            [
                self.config["pdf"][self.language]["custom"]["table_date"],
                self.config["pdf"][self.language]["custom"]["table_price_unit"],
            ],
        )
        table = Table(self.dynamic_info[serie][key])
        table.setStyle(ts)

        return table

    # PDF GENERATION
    def create_pdf(self):
        print(self.language)
        self.serie = None
        # Build story.
        story = []
        toc = self.create_toc()

        def first_page():
            story.append(self.get_static("title(E)", "main_title"))
            story.append(Spacer(2, self.space_bb))
            story.append(Spacer(2, self.space_bb))
            story.append(
                self.image_resize(self.dir_base_path("copertina.jpg"), 0.5)
            )
            story.append(self.get_static("image_desc", "body_center_small"))
            story.append(PageBreak())
            story.append(toc)
            story.append(Spacer(2, self.space_bb))
            story.append(
                self.get_static(
                    "date_report",
                    "body_center",
                    changes=[datetime.today().strftime("%d-%b-%Y")],
                )
            )
            story.append(PageBreak())

        def metodologia():
            story.append(self.get_static("metodology_title1", "body"))
            story.append(self.get_static("metodology_data(E)", "body"))
            story.append(Spacer(1, self.space_s))
            story.append(self.get_static("metodology_title2", "body"))
            story.append(self.get_static("metodology_forcast(E)", "body"))
            story.append(Spacer(1, self.space_s))
            story.append(self.get_static("metodology_title3", "body"))
            story.append(self.get_static("metodology_risk(E)", "body"))
            story.append(PageBreak())

        def summary():
            story.append(self.get_static("summary_title", "h1"))
            story.append(Spacer(1, self.space_s))
            story.append(self.get_static("summary_desc", "body"))
            story.append(Spacer(1, self.space_s))

            story.append(self.get_static("summary_title2", "h2"))
            story.append(Spacer(1, self.space_s))
            for serie in self.config["series"]:
                info = {"serie": serie}
                story.append(self.get_static("summary_prev", "body", info))
                story.append(Spacer(1, self.space_s))

            for serie in self.config["series"]:
                simulation_settings = self.config["series"][serie]["simulation"][
                    "settings"
                ]
                story.append(
                    self.get_static("summary_title3", "h2", {"serie": serie})
                )
                story.append(Spacer(1, self.space_s))
                for index in range(len(simulation_settings)):
                    info = {"serie": serie, "index": index}
                    story.append(
                        self.get_static(
                            "summary_risk1", "body", info, changes=[index + 1]
                        )
                    )
                    story.append(self.get_static("summary_risk2", "body", info))
                    story.append(Spacer(1, self.space_b))

            story.append(PageBreak())

        def overview():
            for serie in self.config["series"]:
                info = {"serie": serie}
                story.append(self.get_static("overview_title", "h1", info))
                story.append(Spacer(1, self.space_s))
                story.append(self.get_static("overview_desc(E)", "body", info))
                story.append(Spacer(1, self.space_s))

                # story.append(pdf_info.get_static("overview_title1", "h2", info))
                # story.append(Spacer(1, self.space_s))
                # story.append(pdf_info.image_resize(self.dir_overview(f"{serie}/image_0.png"), 0.09))
                # story.append(pdf_info.get_static("overview_img1_desc(E)", "body_center", info))
                # story.append(Spacer(1, self.space_s))
                # story.append(pdf_info.image_resize(self.dir_overview(f"{serie}/image_1.png"), 0.09))
                # story.append(pdf_info.get_static("overview_img2_desc(E)", "body_center", info))
                # story.append(PageBreak())

                story.append(self.get_static("overview_title2", "h2", info))
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_overview(f"{serie}/image_2.png"), 0.09
                    )
                )
                story.append(
                    self.get_static("overview_img3_desc(E)", "body_center", info)
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_overview(f"{serie}/image_3.png"), 0.09
                    )
                )
                story.append(
                    self.get_static("overview_img4_desc(E)", "body_center", info)
                )
                story.append(PageBreak())

        def forecasting():
            for serie in self.config["series"]:
                info = {"serie": serie}
                story.append(self.get_static("forecasting_title", "h1", info))
                story.append(Spacer(1, self.space_s))

                story.append(self.get_static("forecasting_desc1", "body", info))
                story.append(Spacer(1, self.space_s))
                story.append(self.get_bullet_list_forcasting(serie))
                story.append(self.get_static("forecasting_desc2", "body", info))
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.get_static("forecasting_graph_desc", "body", info)
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/forecasting.png"), 0.1
                    )
                )
                story.append(
                    self.get_static("forecasting_spiegazione", "body", info)
                )
                story.append(PageBreak())

                story.append(self.get_static("forecasting_tabella", "body", info))
                story.append(Spacer(1, self.space_s))
                story.append(self.create_table(serie, "data_prediction_old"))

                story.append(self.get_static("forecasting_tabella_2", "body", info))
                story.append(Spacer(1, self.space_s))
                story.append(self.create_table(serie, "data_prediction_new"))

                story.append(PageBreak())

        def network():
            for serie in self.config["series"]:
                info = {"serie": serie}
                story.append(self.get_static("network_title1", "h1", info))
                story.append(Spacer(1, self.space_s))

                story.append(self.get_static("netwrok_correlation_title", "h2"))
                story.append(Spacer(1, self.space_s))
                story.append(self.get_static("network_pps_desc", "body"))
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(self.dir_network(f"{serie}/heatmap.png"), 0.1)
                )
                story.append(self.get_static("network_heatmap_desc", "body"))
                story.append(PageBreak())

                story.append(self.get_static("network_title2", "h2"))
                story.append(Spacer(1, self.space_s))
                story.append(self.get_static("network_desc", "body"))
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_network(f"{serie}/graph_network.png"), 0.1
                    )
                )
                story.append(PageBreak())

        def simulation():
            story.append(self.get_static("simulation_title", "h1"))
            story.append(Spacer(1, self.space_s))
            story.append(self.get_static("simulation_desc", "body"))
            story.append(PageBreak())

            for serie in self.config["series"]:
                story.append(
                    self.get_static("simulation_title2", "h2", {"serie": serie})
                )
                for index in range(
                    len(self.config["series"][serie]["simulation"]["settings"])
                ):
                    info = {"serie": serie, "index": index}
                    story.append(Spacer(1, self.space_s))
                    story.append(
                        self.get_static(
                            "simulation_shock_title", "body", info, changes=[index + 1]
                        )
                    )
                    story.append(Spacer(1, self.space_s))
                    story.append(
                        self.get_static("simulation_shock_desc1", "body", info)
                    )
                    story.append(Spacer(1, self.space_s))
                    story.append(
                        self.image_resize(
                            self.dynamic_info[serie]["shock"][index]["img_path"], 0.08
                        )
                    )
                    story.append(
                        self.get_static("simulation_shock_desc2", "body", info)
                    )
                    story.append(Spacer(1, self.space_s))
                    story.append(
                        self.image_resize(
                            self.dynamic_info[serie]["shock"][index]["img_path_2"], 0.08
                        )
                    )
                    story.append(PageBreak())

        first_page()
        metodologia()
        summary()
        overview()
        forecasting()
        network()
        simulation()

        doc = MyDocTemplate(self.dir_pdf(f"Report_{self.language}.pdf"), pagesize=A4)
        doc.multiBuild(story, canvasmaker=FooterCanvas)
