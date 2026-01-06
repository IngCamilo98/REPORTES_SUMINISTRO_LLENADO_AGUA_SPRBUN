import pandas as pd

class GENERATE_GENERAL_RESUME:
    """
    Clase que recibe un DataFrame de actividades de mantenimiento y 
    genera un texto resumen general con métricas automáticas.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._limpiar_valores()
        self.metricas = self._calcular_metricas()

    # ----------------------------------------------------
    # LIMPIEZA DE VALORES MONETARIOS
    # ----------------------------------------------------
    def _limpiar_valores(self):
        if "VALOR_TOTAL" in self.df.columns:
            self.df["VALOR_TOTAL_LIMPIO"] = (
                self.df["VALOR_TOTAL"]
                .astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.replace(" ", "", regex=False)
            )
            self.df["VALOR_TOTAL_LIMPIO"] = pd.to_numeric(
                self.df["VALOR_TOTAL_LIMPIO"], errors="coerce"
            )
        else:
            self.df["VALOR_TOTAL_LIMPIO"] = 0

    # ----------------------------------------------------
    # CÁLCULO DE MÉTRICAS DEL DATAFRAME
    # ----------------------------------------------------
    def _calcular_metricas(self):
        metricas = {}

        # Total de actividades
        metricas["total_actividades"] = len(self.df)

        # Total de zonas registradas
        metricas["total_zonas"] = self.df["ZONA"].nunique()

        # Zonas principales (top 3)
        zonas_top = (
            self.df["ZONA"]
            .value_counts()
            .head(3)
            .index
            .tolist()
        )
        metricas["zonas_principales"] = ", ".join(zonas_top)

        # Actividades HIDROSANITARIAS
        metricas["actividades_hidrosanitarias"] = \
            self.df[self.df["TIPO_ACT"] == "HIDROSANITARIO"].shape[0]

        # Actividades CUBIERTAS (coincidencia parcial)
        mask_cub = self.df["TIPO_ACT"].astype(str).str.contains("CUB", case=False, na=False)
        metricas["actividades_cubiertas"] = self.df[mask_cub].shape[0]

        # Valor económico total
        metricas["valor_global"] = self.df["VALOR_TOTAL_LIMPIO"].sum()

        # Resultado general genérico (puedes reemplazarlo luego si quieres)
        metricas["resultado_general"] = (
            "la estabilización operativa de zonas críticas y la reducción de eventos "
            "por filtraciones e incidencias hidrosanitarias"
        )

        return metricas

    # ----------------------------------------------------
    # GENERAR TEXTO DE RESUMEN GENERAL
    # ----------------------------------------------------
    def generate_text(self):
        m = self.metricas

        texto = f"""
Durante el periodo analizado se registraron un total de **{m['total_actividades']} actividades de mantenimiento** ejecutadas en las instalaciones de la **Sociedad Portuaria Regional de Buenaventura – Zonas Concesionadas y Externas**. Estas intervenciones se llevaron a cabo en **{m['total_zonas']} zonas operativas**, entre las cuales destacan **{m['zonas_principales']}**, por su mayor volumen de requerimientos.

El análisis del consolidado evidencia que las actividades se concentraron en dos líneas principales de trabajo:
- **Actividades hidrosanitarias:** {m['actividades_hidrosanitarias']} intervenciones.
- **Actividades en cubiertas:** {m['actividades_cubiertas']} intervenciones.

Las acciones ejecutadas permitieron {m['resultado_general']}, garantizando la continuidad operativa y la funcionalidad de las áreas intervenidas.

El valor económico consolidado del periodo asciende a **${m['valor_global']:,.0f}**, correspondiente a la ejecución total de las actividades registradas.

Este resumen refleja el cumplimiento integral de las labores de mantenimiento necesarias para asegurar la operatividad y las condiciones adecuadas de infraestructura en las zonas concesionadas y externas de la SPRBUN.
"""
        return texto.strip()
