from reportlab.pdfgen import canvas
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus import ListFlowable, ListItem
from reportlab.platypus.frames import Frame
from reportlab.platypus.flowables import Image
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from codebase.modules.Project import Project
import re
import ast

def styles_pdf():
    fontSizeSmallSmall = 8
    fontSizeSmall = 11
    fontSizeMedium = 12
    fontSizeLarge = 15
    fontMainTitle = 24

    return {
        # Se utilizzati h1 e h2 viengono messi nel summary
        "h1": PS(
            name="h1",
            fontSize=fontSizeLarge,
            leading=fontSizeLarge,
            alignment=TA_CENTER,
        ),
        "h2": PS(
            name="h2",
            fontSize=fontSizeMedium,
            leading=fontSizeMedium,
            alignment=TA_CENTER,
        ),
        # ------------------------------------------------
        "main_title": PS(
            name="main_title",
            fontSize=fontMainTitle,
            alignment=TA_CENTER,
            leading=fontMainTitle,
        ),
        "body": PS(
            name="body",
            fontSize=fontSizeSmall,
            alignment=TA_JUSTIFY,
        ),
        "body_center": PS(
            name="body_center",
            fontSize=fontSizeSmall,
            alignment=TA_CENTER,
        ),
        "body_center_small": PS(
            name="body_center",
            fontSize=fontSizeSmallSmall,
            alignment=TA_CENTER,
        ),
        "body_list": PS(
            name="body_list",
            fontSize=fontSizeSmall,
            alignment=TA_LEFT,
            leading=20,
        ),
    }

styles = styles_pdf()
logo_width, logo_height = ImageReader("images/logo_baia.png").getSize()

class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page_number = "Page %s of %s" % (self._pageNumber, page_count)
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        self.line(66, 78, A4[0] - 66, 78)
        self.setFont("Times-Roman", 10)
        self.drawString(A4[0] - x, 65, page_number)

        paragraph1 = Paragraph(
            "<b>Baia S.r.L</b> | Sede Legale Via Brera 3, 20121 Milano | Sede Operativa Viale Italia 230/232, 20099 Sesto San Giovanni (MI) | T +39 02 944336.20 info@baiaintelligence.it | pec_baia@legalmail.it I www.baia.tech | Partita IVA e C.F 12852780969 | Capitale sociale €10.000,00",
            style=PS(name="footer_style", alignment=TA_JUSTIFY, fontSize=8),
        )

        # Set the width of the paragraph
        paragraph1.width = 20 * cm

        # Set the position of the paragraph on the page
        paragraph1.wrapOn(self, 465, 50)
        paragraph1.drawOn(self, 65, 10)

        paragraph2 = Paragraph("NATO NCAGE CODE: AV635", style=styles["body"])
        paragraph2.width = 6 * cm
        paragraph2.wrapOn(self, 6 * cm, 1 * cm)
        paragraph2.drawOn(self, A4[0] - 6 * cm, A4[1] - 1.35 * cm)

        self.drawImage(
            "images/logo_baia.png",
            1 * cm,
            A4[1] - 2 * cm,
            logo_width * 0.1,
            logo_height * 0.1,
            mask="auto",
        )
        self.restoreState()

class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        margin = 2.5 * cm
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate(
            "normal",
            [
                Frame(
                    margin,
                    margin,
                    21 * cm - 2 * margin,
                    29.7 * cm - 2 * margin,
                    id="F1",
                )
            ],
        )
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == "Paragraph":
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == "h1":
                self.notify("TOCEntry", (0, text, self.page))
            if style == "h2":
                self.notify("TOCEntry", (1, text, self.page))

class PDF_Sostituzioni():
    def __init__(self, project:Project, language:str) -> None:
        self.project = project
        self.language = language
        self.config = project.config
        self.static_info = project.config["pdf"][language]["static"]
        self.custom_info = project.config["pdf"][language]["custom"]
        self.dynamic_info = project.dynamic_info


    def settore(self, **kwargs):
        return self.custom_info["settore"]

    def next_Art(self, **kwargs):
        return self.custom_info["next_Art"]

    def next_art(self, **kwargs):
        return self.custom_info["next_art"]

    def forecasting_range(self, **kwargs):
        return self.custom_info["forecasting_range"]

    def forecasting_unit(self, **kwargs):
        return self.custom_info["forecasting_unit"]

    def forecasting_target_art(self, **kwargs):
        return self.custom_info["forecasting_target_art"]

    def forecasting_target(self, **kwargs):
        return self.custom_info["forecasting_target"]

    def table_price_unit(self, **kwargs):
        return self.custom_info["table_price_unit"]

    # ------------------------ Dynamic Info  ------------------------

    def andamento_prezzo_desc(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["andamento_prezzo_desc"][
            self.language
        ]

    def andamento_prezzo_desc1(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["andamento_prezzo_desc1"][
            self.language
        ]

    def andamento_prezzo_value(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["andamento_prezzo_value"]

    def andamento_prezzo_errore(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["andamento_prezzo_errore"]

    def low_range(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["low_range"]

    def high_range(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["high_range"]

    def raggiungimento_nodo_target(self, **kwargs):
        return self.dynamic_info[kwargs["serie"]]["shock"][kwargs["index"]][
            "raggiungimento_nodo_target"
        ]

    # ------------------------ Config Info  ------------------------
    def settore_art(self, **kwargs):
        return self.config["series"][kwargs["serie"]]["pdf"][self.language]["settore"][
            0
        ]

    def settore_art2(self, **kwargs):
        return self.config["series"][kwargs["serie"]]["pdf"][self.language]["settore"][
            1
        ]

    def nodi_sorgente_desc(self, **kwargs):
        return self.config["series"][kwargs["serie"]]["simulation"]["settings"][
            kwargs["index"]
        ]["nodi_sorgente_desc"][self.language]

    def overview_year1(self, **kwargs):
        return self.config["series"][kwargs["serie"]]["overview"][0]["year_back"]

    def overview_year2(self, **kwargs):
        return self.config["series"][kwargs["serie"]]["overview"][2]["year_back"]

    def n_simulation(self, **kwargs):
        return self.config["series"][kwargs["serie"]]["simulation"]["list_simulazioni"][
            0
        ]

    # --------------------------------------------------------------

    def create_paragraph(self, input_string, style):
        return Paragraph(input_string, styles[style])

    def access_nested_dict(self, dic, keys):
        for key in keys:
            dic = dic[key]
        return dic

    def sostituzioni1(self, string_input, changes):
        if changes != None:
            assert len(re.findall(r"{\d?}", string_input)) == len(changes)
            string_input = string_input.format(*changes)

        return string_input

    def sostituzioni2(self, string_input, info):
        # Definisci la regex per estrarre le stringhe tra << e >>
        regex_pattern = r"<<(.*?)>>"

        # Funzione di sostituzione che restituisce la stringa desiderata
        def substitution(match):
            patter_value = ast.literal_eval(match.group(1))

            if isinstance(patter_value, str):
                funzione = getattr(self, patter_value)
                return str(funzione(**info))

            print("<<...>> Non riconosciuto come lista")
            exit()

        # Sostituisci tutte le corrispondenze nella stringa di input utilizzando la funzione di sostituzione
        result = re.sub(regex_pattern, substitution, string_input)

        return result

    def get_static(self, key, style, info={}, changes=[]):
        string_data = self.static_info[key]
        string_data = self.sostituzioni1(string_data, changes)
        string_data = self.sostituzioni2(string_data, info)
        return self.create_paragraph(string_data, style)

class PDF_Utils:
    def __init__(self, project:Project, language:str) -> None:
        self.config = project.config
        self.language = language

        self.space_s = 10
        self.space_m = 15
        self.space_b = 20
        self.space_bb = 30

    def get_bullet_list_forcasting(self, serie):
        items = self.config["series"][serie]["pdf"][self.language][
            "series_utilized_training_nn"
        ]
        return ListFlowable(
            [ListItem(Paragraph(x, styles["body_list"])) for x in items],
            bulletType="bullet",
            bulletOffsetY=2,
        )

    def image_resize(self, path, ratio):
        # Apri l'immagine utilizzando l'oggetto ImageReader
        image_reader = ImageReader(path)

        # Ottieni la larghezza e l'altezza dell'immagine
        width, height = image_reader.getSize()

        desired_ratio = ratio
        resized_width = width * desired_ratio
        resized_height = height * desired_ratio
        return Image(path, width=resized_width, height=resized_height, hAlign="CENTER")

    def create_toc(self):
        toc = TableOfContents()
        toc.levelStyles = [
            PS(
                fontName="Times-Bold",
                fontSize=10,
                name="TOCHeading1",
                leftIndent=20,
                firstLineIndent=-20,
                spaceBefore=2,
                leading=5,
            ),
            PS(
                fontName="Times-Bold",
                fontSize=10,
                name="TOCHeading2",
                leftIndent=40,
                firstLineIndent=-20,
                spaceBefore=2,
                leading=5,
            ),
        ]

        return toc