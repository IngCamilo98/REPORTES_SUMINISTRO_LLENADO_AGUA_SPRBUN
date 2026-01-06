from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import pandas as pd
import os

# Importar la clase desde la carpeta modules
from modules.GENERATE_RESUMS_DAILY import GenerateText 

class CREATE_TABLE_RESUMS:
    """
    Guarda resúmenes diarios en un archivo Excel evitando duplicados por fecha.
    """

    def __init__(self, ruta_archivo="BD/EXCEL/RESUMENES/resumenes_mensuales.xlsx"):
        """
        Inicializa la clase indicando la ruta donde se guardarán los resúmenes.
        Crea la carpeta si no existe.
        """
        self.ruta_archivo = Path(ruta_archivo)
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

        # Si el archivo existe, lo carga; si no, crea un DataFrame vacío.
        if self.ruta_archivo.exists():
            try:
                self.df_resumenes = pd.read_excel(self.ruta_archivo)
            except Exception:
                # Si el archivo está corrupto, reinicia.
                self.df_resumenes = pd.DataFrame(columns=["FECHA", "RESUMEN"])
        else:
            self.df_resumenes = pd.DataFrame(columns=["FECHA", "RESUMEN"])

    def guardar_resumen(self, fecha: str, resumen: str):
        """
        Guarda el resumen en el archivo Excel si la fecha no existe.
        """

        # Validación por si viene vacío
        if not resumen or not isinstance(resumen, str):
            print(f"⚠️ No se pudo guardar resumen para {fecha} (vacío o inválido).")
            return
        
        # Verificar si la fecha ya existe
        if fecha in self.df_resumenes["FECHA"].astype(str).values:
            print(f"⏭️ Resumen para {fecha} ya existe. Se omite.")
            return

        # Agregar registro
        nuevo_registro = {
            "FECHA": fecha,
            "RESUMEN": resumen
        }

        self.df_resumenes = pd.concat(
            [self.df_resumenes, pd.DataFrame([nuevo_registro])],
            ignore_index=True
        )

        # Guardar en el archivo
        self.df_resumenes.to_excel(self.ruta_archivo, index=False)

        print(f"💾 Resumen guardado correctamente para: {fecha}")
