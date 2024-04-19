
from reportlab.platypus import PageBreak, Spacer, Table
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from datetime import datetime
from reportlab.platypus import PageBreak, Spacer
from reportlab.lib.pagesizes import A4
from codebase.modules.PDF import FooterCanvas, MyDocTemplate
from codebase.modules.Project import Project

from codebase.modules.PDF import PDF_Sostituzioni, PDF_Utils


class PDFGenerationEurostat(PDF_Sostituzioni, PDF_Utils):
    def __init__(self, project:Project, language:str) -> None:
        project.serie = None
        PDF_Sostituzioni.__init__(self, project, language)
        PDF_Utils.__init__(self, project, language)
        self.project = project
        self.language = language

        # INFO ESTRATTE DA PROJECT
        self.config = project.config
        self.serie = project.serie
        self.dir_base_path = project.dir_base_path
        self.dir_forecasting = project.dir_forecasting
        self.dir_pdf = project.dir_pdf


    # PDF GENERATION
    def create_table(self, data):
        ts = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                # ("TEXTCOLOR", (0, 0), (-1, 0), colors.red),
                ("ALIGNMENT", (0, 0), (-1, -1), "CENTER"),
            ]
        )

        table = Table(data)
        table.setStyle(ts)

        return table

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
            story.append(Spacer(2, self.space_bb))
            story.append(Spacer(2, self.space_bb))
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

        def sintesi():
            pass

        def metodologia():
            story.append(self.get_static("premessa", "h1"))
            story.append(self.get_static("metodology_title1", "body"))
            story.append(self.get_static("metodology_data(E)", "body"))
            story.append(Spacer(1, self.space_s))
            story.append(self.get_static("metodology_title2", "body"))
            story.append(self.get_static("metodology_forcast(E)", "body"))
            story.append(PageBreak())

        def forecasting():
            for serie, title_suffix in zip(
                ["italy_vs_eu", "italy_vs_not_eu", "eu_vs_not_eu"], ["_1", "_2", "_3"]
            ):
                first_line_table = self.dynamic_info[serie][0]

                story.append(
                    self.get_static(f"forecasting_title{title_suffix}", "h1")
                )
                story.append(Spacer(1, self.space_b))
                story.append(
                    self.get_static(f"forecasting_desc{title_suffix}", "body")
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/forecasting.png"), 0.1
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.get_static(f"forecasting_table{title_suffix}", "body")
                )
                story.append(Spacer(1, self.space_s))
                story.append(self.create_table(self.dynamic_info[serie]))
                # Inserire tabella
                story.append(PageBreak())

                # INSERIMENTO BAR CHARTS
                story.append(
                    self.get_static(
                        f"forecasting_bar{title_suffix}",
                        "body_center",
                        changes=[first_line_table[1]],
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/bar_1_month.jpg"), 0.1
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.get_static(
                        f"forecasting_bar{title_suffix}",
                        "body_center",
                        changes=[first_line_table[2]],
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/bar_2_month.jpg"), 0.1
                    )
                )
                story.append(PageBreak())
                story.append(
                    self.get_static(
                        f"forecasting_bar{title_suffix}",
                        "body_center",
                        changes=[first_line_table[3]],
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/bar_3_month.jpg"), 0.1
                    )
                )
                story.append(Spacer(1, self.space_s))

                # INSERIMENTO PIE CHARTS
                story.append(
                    self.get_static(
                        f"forecasting_pie{title_suffix}",
                        "body_center",
                        changes=[first_line_table[1]],
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/pie_1_month.jpg"), 0.1
                    )
                )
                story.append(PageBreak())
                story.append(
                    self.get_static(
                        f"forecasting_pie{title_suffix}",
                        "body_center",
                        changes=[first_line_table[2]],
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/pie_2_month.jpg"), 0.1
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.get_static(
                        f"forecasting_pie{title_suffix}",
                        "body_center",
                        changes=[first_line_table[3]],
                    )
                )
                story.append(Spacer(1, self.space_s))
                story.append(
                    self.image_resize(
                        self.dir_forecasting(f"{serie}/pie_3_month.jpg"), 0.1
                    )
                )

                story.append(Spacer(1, self.space_s))
                story.append(PageBreak())

        first_page()
        sintesi()
        metodologia()
        forecasting()

        self.serie = None
        doc = MyDocTemplate(self.dir_pdf(f"Report_{self.language}.pdf"), pagesize=A4)
        doc.multiBuild(story, canvasmaker=FooterCanvas)
