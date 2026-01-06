import pandas as pd
from google import genai
import os 
from typing import Optional

class GenerateText:
    """
    Clase para interactuar con la API de Gemini y generar resúmenes
    de reportes de mantenimiento, utilizando la columna ZONA como contexto.
    """

    def __init__(self):
        """
        Inicializa el cliente de la API de Gemini. 
        Requiere que la variable de entorno 'GEMINI_API_KEY' esté cargada.
        """
        try:
            # El cliente busca automáticamente la clave en el entorno
            self.client = genai.Client()
            # print("🤖 Cliente de Gemini inicializado.")
        except Exception as e:
            # Si la clave no está, lanzamos un error claro
            raise ConnectionError(
                "No se pudo inicializar el cliente de Gemini. "
                "Asegúrate de que 'GEMINI_API_KEY' esté configurada y sea válida."
            ) from e

    def generate_summary(self, df: pd.DataFrame) -> Optional[str]:
        """
        Genera un resumen de la columna 'DESCRIPCION', añadiendo 
        el contexto de las ubicaciones de la columna 'ZONA'.

        Args:
            df: DataFrame de Pandas con las columnas 'DESCRIPCION' y 'ZONA'.

        Returns:
            La cadena de texto con el resumen generado por Gemini, o None en caso de error.
        """
        if df.empty:
            return "El DataFrame está vacío. No hay descripciones para resumir."
            
        if 'DESCRIPCION' not in df.columns or 'ZONA' not in df.columns:
            return "ERROR: El DataFrame debe contener las columnas 'DESCRIPCION' y 'ZONA'."
            
        # --- 1. Preparar el Contexto de las Zonas ---
        # Obtener las zonas únicas para dar contexto al modelo
        zonas_unicas = df['ZONA'].astype(str).unique()
        zonas_str = ", ".join(zonas_unicas)

        # --- 2. Preparar el Texto Completo de Descripciones ---
        # Unir todas las descripciones en una sola cadena para el modelo
        descripciones_series = df['DESCRIPCION'].dropna()
        texto_descripciones = '\n---\n'.join(descripciones_series.astype(str))

        # --- 3. Definir el Prompt (Instrucción) ---
        prompt_instruccion = f"""
        **INSTRUCCIÓN:**
        A continuación, se te proporcionarán varias descripciones de mantenimiento y reportes, 
        separadas por el delimitador '---'.

        Estas descripciones están asociadas a las siguientes ubicaciones (Zonas): **{zonas_str}**.
        Tu tarea es generar un resumen único de maximo 150 palabras, coherente y conciso de estos reportes y debe que la información es un resumen de los reportes de las zonas listadas ({zonas_str}) ignora los nan. 
        El resumen debe estar en español.

        --- DESCRIPCIONES DE ENTRADA ---
        {texto_descripciones}
        """

        # --- 4. Llamar a la API de Gemini ---
        print(f"\n⏳ Enviando {len(descripciones_series)} descripciones a Gemini para resumen de zonas: {zonas_str}...")
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",  # Modelo ideal para tareas de texto y resumen
                contents=[prompt_instruccion]
            )
            
            return response.text

        except Exception as e:
            print(f"❌ Error al llamar a la API de Gemini durante el resumen: {e}")
            return None
        




















