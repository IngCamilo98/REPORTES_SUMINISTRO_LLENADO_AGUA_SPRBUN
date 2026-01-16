from modules.GET_DATAFRAMES import DATAFRAMES_ACTIVIDADES_SPRBUN
from modules.CREATE_PDF_V1 import PDFHeaderFooter
from modules.MENU import AdminFechas 
from modules.CREATE_TABLE_RESUMS import CREATE_TABLE_RESUMS
from modules.GENERATE_GENERAL_RESUME import GENERATE_GENERAL_RESUME
from modules.CREATE_EXCEL_RESUME import CREATE_EXCEL_RESUME

from dotenv import load_dotenv # Importar para cargar el .env
import os
from google import genai
from dotenv import load_dotenv
import pandas as pd


#---------------------------ejecutemos el menu---------------------------#
menu = AdminFechas()
fechas = menu.ejecutar()

anio = menu.anio
mes = menu.mes

nombre_mes = AdminFechas.MESES_NUM_A_NOMBRE[mes]
nombre_mes_anterior = menu.nombre_mes_anterior()

fechas_mes = menu.rango_fechas_25a25()
#print("Rango de fechas (27 a 26):", fechas[0].date(), "→", fechas[-1].date())
#print("Total de días en el rango:", len(fechas))

#print(fechas)

#---------------------------creemos los dataframes---------------------------#

ruta_excel = '/home/sr_camilot/Documents/AMC/TEC/REPORTES_SUMINISTRO_LLENADO_AGUA_SPRBUN/BD/EXCEL/ACTIVIDADES/BD_ACTIVIDADES_HIDROSANITARIAS_CUBIERTAS.xlsx'

create_dataframe = DATAFRAMES_ACTIVIDADES_SPRBUN(ruta_excel)

df_informe_actividades = create_dataframe.get_dataframe_actividades()

#---------------------------generemos los resúmenes diarios---------------------------#

df_resumenes = pd.read_excel("BD/EXCEL/RESUMENES/resumenes_mensuales.xlsx")
#---------------------------generemos el resumen mensual---------------------------#
resumen_general = GENERATE_GENERAL_RESUME(df_informe_actividades)
texto = resumen_general.generate_text()


#---------------------------creemos el docuemtno pdf---------------------------#
pdf = PDFHeaderFooter()
pdf.agregar_portada(anio, nombre_mes, nombre_mes_anterior, fechas_mes, texto)  #  se dibuja solo en la primera página

# (opcional) agrega páginas extra para probar repetición del header/footer
for i in range(len(fechas_mes) - 1):

    # Buscar el resumen correspondiente a la fecha actual
    resumen_fila = df_resumenes[df_resumenes["FECHA"] == fechas_mes[i]]

    if not resumen_fila.empty:
        resumen_diario = resumen_fila["RESUMEN"].iloc[0]
    else:
        resumen_diario = "Sin resumen disponible."

    pdf.agregar_tabla_actividades_dia(
        num_dia=i+1,
        anio=anio,
        fecha_dia=fechas_mes[i],
        df_dia=create_dataframe.get_dataframe_diario(fechas_mes[i]),
        descripcion_servicio=resumen_diario,
        nueva_pagina=True
    )

# Ruta de salida
output_dir = "BD/INFORMES/SPRBUN"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "INFORME_HEADER_FOOTER.pdf")
pdf.output(output_path)
print(f"✅ PDF generado correctamente en: {output_path}")

#---------------------------creemos el documento excel---------------------------#
generador = CREATE_EXCEL_RESUME()


fecha_inicio = fechas_mes[0]
fecha_fin = fechas_mes[-1]

excel_path = generador.crear_informe(
    df_informe_actividades,
    fecha_inicio,
    fecha_fin
)





