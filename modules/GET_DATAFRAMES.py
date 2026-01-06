import pandas as pd
from datetime import datetime
import unicodedata

class DATAFRAMES_ACTIVIDADES_SPRBUN:

    def __init__(self, ruta_excel):

        self.ruta_excel = ruta_excel
        self.df_excel = pd.ExcelFile(ruta_excel)
        self.df_actividades = pd.read_excel(self.df_excel, sheet_name='BD')
       
    def get_dataframe_diario(self, fecha):
        df_actividades_diario = self.df_actividades[self.df_actividades['FECHA'] == fecha]
        return df_actividades_diario

    def _to_latin1(self, text):
        """
        Asegura que el texto sea compatible con latin-1
        (core fonts de FPDF), reemplazando guiones largos,
        comillas curvas, viñetas, etc., y eliminando lo que
        no se pueda codificar.
        """
        if text is None:
            return ""

        text = str(text)

        reemplazos = {
            "–": "-",   # en dash
            "—": "-",   # em dash
            "“": '"',
            "”": '"',
            "’": "'",
            "´": "'",
            "•": "-",   # viñetas
        }

        for raro, simple in reemplazos.items():
            text = text.replace(raro, simple)

        # filtro final: quitar cualquier cosa fuera de latin-1
        text = text.encode("latin-1", "ignore").decode("latin-1")
        return text

    @staticmethod
    def limpiar_texto_pdf(texto):
        """
        Limpia de forma profunda caracteres que FPDF (latin-1) no soporta.
        Ideal para textos que vienen de ChatGPT, Word, WhatsApp o correos.
        """

        if pd.isna(texto):
            return ""

        texto = str(texto)

        # 1️⃣ ELIMINAR saltos raros, espacios invisibles, caracteres ocultos
        textos_raros = [
            "\u200b",  # zero-width space
            "\u200c",  # non-joiner
            "\u200d",  # joiner
            "\ufeff",  # BOM
            "\xa0",    # espacio duro
            "\t",      # tabulaciones
            "\r",      # retorno de carro
        ]
        for t in textos_raros:
            texto = texto.replace(t, " ")

        # 2️⃣ REEMPLAZOS DE CARACTERES PROBLEMÁTICOS
        reemplazos = {
            "–": "-",    # en dash
            "—": "-",    # em dash
            "―": "-",    # horizontal bar
            "•": "-",    # viñetas
            "∙": "-",    # viñetas pequeñas
            "·": "-",    # bullet punto medio
            "“": '"',
            "”": '"',
            "„": '"',
            "‟": '"',
            "’": "'",
            "‘": "'",
            "´": "'",
            "`": "'",
            "¨": "",
            "…": "...",  # puntos suspensivos Unicode
            "¶": "",     # símbolo de párrafo
            "°": "°",    # mantenemos grados pero normalizados
        }

        for raro, simple in reemplazos.items():
            texto = texto.replace(raro, simple)

        # 3️⃣ REMOVER EMOJIS Y SÍMBOLOS NO LATIN-1
        import re
        texto = re.sub(r'[^\x00-\xFF]', '', texto)

        # 4️⃣ NORMALIZAR UNICODE → quitar diacríticos raros
        import unicodedata
        texto = unicodedata.normalize("NFKD", texto)

        # 5️⃣ FILTRO FINAL: eliminar cualquier cosa fuera de latin-1
        texto = texto.encode("latin-1", "ignore").decode("latin-1")

        # 6️⃣ QUITAR ESPACIOS EXTRA GENERADOS
        texto = " ".join(texto.split())

        return texto

    def get_dataframe_actividades(self) -> pd.DataFrame:
        """
        Limpia directamente self.df_actividades sin crear copias.
        Modifica el DataFrame original dentro de la clase.
        """
    
        columnas_a_liminar = ["DESCRIPCION"]
    
        for col in columnas_a_liminar:
            if col in self.df_actividades.columns:
                self.df_actividades[col] = (
                    self.df_actividades[col]
                    .astype(str)
                    .apply(self.limpiar_texto_pdf)
                )
    
        return self.df_actividades

