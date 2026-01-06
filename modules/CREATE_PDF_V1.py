from fpdf import FPDF
import os

class PDFHeaderFooter(FPDF):
    """
    PDF oficio horizontal con encabezado y pie de página (imágenes locales).
    """
    
    def __init__(self):
        # --- CONFIGURACIÓN BÁSICA DEL PDF ---
        super().__init__(orientation="L", unit="mm", format=(216, 340))  # L = horizontal, oficio 216x340 mm
        self.left_margin = 14
        self.right_margin = 14
        self.top_margin = 2
        self.bottom_margin = 2
        self.header_height = 18   # altura reservada para header
        self.footer_height = 16   # altura reservada para footer

        # --- RUTAS LOCALES DE LAS IMÁGENES ---
        # 🔧 Cambia estas rutas a donde realmente tienes tus imágenes
        self.header_img = "templates/ENCABEZADO/encabezado.jpeg"
        self.footer_img = "templates/FOOTER/footer.jpeg"

        # --- VALIDACIÓN DE EXISTENCIA ---
        if not os.path.isfile(self.header_img):
            raise FileNotFoundError(f"No se encontró la imagen de encabezado: {self.header_img}")
        if not os.path.isfile(self.footer_img):
            raise FileNotFoundError(f"No se encontró la imagen de pie de página: {self.footer_img}")

        # --- CONFIGURACIÓN DE MÁRGENES EFECTIVOS ---
        self.set_margins(left=self.left_margin,
                         top=self.top_margin + self.header_height,
                         right=self.right_margin)
        self.set_auto_page_break(auto=True,
                                 margin=self.bottom_margin + self.footer_height)

        # --- AGREGAR PÁGINA INICIAL ---
        self.add_page()

    # ------------------------------------------------------------------
    # Encabezado
    # ------------------------------------------------------------------
    def header(self):
        usable_width = self.w - self.left_margin - self.right_margin
        y = self.top_margin
        target_height = self.header_height * 0.98

        # Dibuja imagen centrada con márgenes laterales blancos
        self.image(self.header_img,
                   x=self.left_margin,
                   y=y,
                   w=usable_width)

        # Cursor justo debajo del encabezado
        self.set_y(self.top_margin + self.header_height)

    # ------------------------------------------------------------------
    # Pie de página
    # ------------------------------------------------------------------
    def footer(self):
        """
        Footer centrado y 50% más pequeño.
        """
        # Altura visual (ajustable)
        target_h = 10
        y = self.h - self.bottom_margin - target_h - 2

        page_width = self.w

        # 🔽 aquí está el cambio importante:
        # antes: footer_width = page_width * 0.45
        footer_width = page_width * 0.225  # 50% más pequeño que antes

        # Centrado horizontal
        x = (page_width - footer_width) / 2

        # Dibuja el footer centrado
        self.image(
            self.footer_img,
            x=x,
            y=y,
            w=footer_width
        )
    # ------------------------------------------------------------------
    # Portada informativa
    # ------------------------------------------------------------------

    @staticmethod
    def limpiar_texto_pdf(texto: str) -> str:
        """
        Elimina y reemplaza caracteres Unicode incompatibles con Helvetica en FPDF.
        """
        if texto is None:
            return ""
        reemplazos = {
            "–": "-",    # en dash
            "—": "-",    # em dash
            "’": "'",    # comilla curva derecha
            "‘": "'",    # comilla curva izquierda
            "“": '"',    # comilla doble curva izquierda
            "”": '"',    # comilla doble curva derecha
            "…": "...",  # puntos suspensivos unicode
            "•": "-",    # viñeta
        }
        for viejo, nuevo in reemplazos.items():
            texto = texto.replace(viejo, nuevo)
        return texto

    def agregar_portada(self, anio, nombre_mes, nombre_mes_anterior, fechas_mes, resumen_general):
        """
        Dibuja el bloque de texto informativo y el resumen general en la PRIMERA página del informe.
        """

        # Limpiar el texto recibido
        resumen_general = self.limpiar_texto_pdf(resumen_general)

        # Ir un poco debajo del encabezado
        self.set_y(self.top_margin + self.header_height + 6)

        # Título centrado
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "INFORME GENERAL DE ACTIVIDADES EJECUTADAS", ln=True, align="C")

        # Espacio
        self.ln(2)

        # Información principal del encabezado
        encabezado = (
            "Servicio: MANTENIMIENTO PERMANENTE DE CUBIERTAS Y REDES SANITARIAS\n"
            "Lugar de ejecución: SOCIEDAD PORTUARIA REGIONAL DE BUENAVENTURA - ZONAS CONCESIONADAS Y EXTERNAS\n"
            "Contratista: ALFA MONTAJES Y CUBIERTAS S.A.S.\n"
            f"Periodo reportado: Del {fechas_mes[0].day} de {nombre_mes_anterior} "
            f"al {fechas_mes[-1].day} de {nombre_mes} de {anio}"
        )

        # Limpiar también el encabezado
        encabezado = self.limpiar_texto_pdf(encabezado)

        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 7, encabezado, align="L")

        # Línea inferior separadora
        self.ln(3)
        self.set_draw_color(180, 180, 180)
        self.line(self.left_margin, self.get_y(), self.w - self.right_margin, self.get_y())

        # Espacio para separar la línea del resumen
        self.ln(5)

        # -----------------------------------------
        # 🔥 Agregar el RESUMEN GENERAL limpio
        # -----------------------------------------
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, resumen_general, align="J")

    def agregar_tabla_actividades_dia(
            self,
            num_dia,
            anio,
            fecha_dia,
            df_dia,
            titulo_dia=None,
            descripcion_servicio="",   # 👈 NUEVO
            nueva_pagina=True
        ):
        """
        Dibuja una tabla tipo Excel con las actividades de un día.

        Parámetros:
        - anio: int
        - fecha_dia: datetime.date (o str '2025-10-10')
        - df_dia: DataFrame con columnas:
          FECHA, ZONA, DESCRIPCION, UNIDAD_MEDIDA, CANTIDAD, VALOR_UNITARIO, VALOR_TOTAL
        - titulo_dia: texto opcional para el encabezado del bloque.
        - descripcion_servicio: texto que se mostrará luego del título.
        - nueva_pagina: si True, agrega una nueva página antes de dibujar la tabla.
        """

        # ------------------------------------------------
        # 1. Asegurar tipo de fecha
        # ------------------------------------------------
        if isinstance(fecha_dia, str):
            from datetime import datetime
            fecha_dia = datetime.strptime(fecha_dia, "%Y-%m-%d").date()

        # ------------------------------------------------
        # 2. Nueva página (si aplica) y posición inicial
        # ------------------------------------------------
        if nueva_pagina:
            self.add_page()

        # Dejamos un pequeño espacio bajo el encabezado
        self.set_y(self.get_y() + 10)

        # ------------------------------------------------
        # 3. Título de la sección EN ESPAÑOL
        # ------------------------------------------------
        self.set_font("Helvetica", "B", 11)

        if titulo_dia is None:
            dias_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            meses_es = [
                "enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
            ]
            nombre_dia = dias_es[fecha_dia.weekday()].capitalize()
            nombre_mes = meses_es[fecha_dia.month - 1]

            # Ej: "DÍA - Lunes 27 de octubre de 2025"
            titulo_dia = f"DÍA {num_dia} - {nombre_dia} {fecha_dia.day} de {nombre_mes} de {anio}"

        self.cell(0, 8, titulo_dia, ln=True, align="L")

        # ------------------------------------------------
        # 4. Descripción del servicio (texto configurable)
        # ------------------------------------------------
        self.set_font("Helvetica", "", 9)

        if descripcion_servicio:
            # Línea con etiqueta + texto
            self.multi_cell(
                0,
                5,
                f"Descripción del servicio: {descripcion_servicio}",
                ln=True
            )
        else:
            # Solo la etiqueta si no pasas descripción
            self.multi_cell(0, 5, "Descripción del servicio:", ln=True)

        # Total del día (suma VALOR_TOTAL)
        total_dia = float(df_dia["VALOR_TOTAL"].sum())
        total_dia_str = f"{total_dia:,.0f}".replace(",", ".")
        self.ln(2)
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 6, f"ACTIVIDADES EJECUTADAS - TOTAL: ${total_dia_str}", ln=True, align="L")
        self.ln(2)

        # ------------------------------------------------
        # 5. Configuración de columnas (ancho en mm)
        #    Usamos TODO el ancho útil: w - márgenes
        # ------------------------------------------------
        usable_width = self.w - self.left_margin - self.right_margin  # ≈ 312 mm

        # Antes:
        # 25 + 40 + 105 + 18 + 18 + 28 + 28 + 50 = 312
        # Ahora hacemos DESCRIPCION ~la mitad (52) y ese espacio se lo damos a FOTOS (103):
        # 25 + 40 + 52 + 18 + 18 + 28 + 28 + 103 = 312
        col_widths = {
            "FECHA": 20,         # reducido
            "ZONA": 40,          # igual
            "DESCRIPCION": 70,   # aumentado
            "UNIDAD": 13,        # reducido
            "CANTIDAD": 13,      # reducido
            "V_UNIT": 28,        # igual
            "V_TOTAL": 28,       # igual
            "FOTOS": 100         # ajustado para cuadrar total 312 mm
        }



        line_height = 5

        # ------------------------------------------------
        # 6. Encabezado de la tabla
        # ------------------------------------------------
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)

        y_inicio_tabla = self.get_y() + 4
        x_inicio_tabla = self.left_margin
        self.set_xy(x_inicio_tabla, y_inicio_tabla)

        headers = [
            "Fecha",
            "Área / Ubicación",
            "Actividad Realizada",
            "Unidad",
            "Cantidad",
            "Valor Unitario ($)",
            "Valor Total ($)",
            "Fotografías"
        ]

        widths_order = [
            col_widths["FECHA"],
            col_widths["ZONA"],
            col_widths["DESCRIPCION"],
            col_widths["UNIDAD"],
            col_widths["CANTIDAD"],
            col_widths["V_UNIT"],
            col_widths["V_TOTAL"],
            col_widths["FOTOS"]
        ]

        for header, w in zip(headers, widths_order):
            self.cell(w, line_height * 2, header, border=1, align="C", fill=True)
        self.ln(line_height * 2)

        # ------------------------------------------------
        # 7. Filas con datos del DataFrame
        # ------------------------------------------------
        self.set_font("Helvetica", "", 8)

        # ------------------------------------------------
        # 7. Filas con datos del DataFrame
        # ------------------------------------------------
        self.set_font("Helvetica", "", 8)

        def _dibujar_fila(celdas, widths, fotos_paths=None):
            """
            Dibuja UNA fila completa:
            - Calcula la altura que ocupa el texto
            - Si hay fotos, aumenta la altura de la fila para que quepan
              sin deformarse (se respeta la proporción de la imagen).
            - Dibuja el texto, los bordes y, si aplica, las fotografías
              en la última columna.
            """
            x_fila = self.get_x()
            y_fila = self.get_y()
            max_y = y_fila

            aligns = [
                "C",  # Fecha
                "L",  # Área / Ubicación
                "L",  # Actividad Realizada
                "C",  # Unidad
                "C",  # Cantidad
                "C",  # Valor Unitario
                "C",  # Valor Total
                "C",  # Fotografías (si hubiera texto)
            ]

            # 1️⃣ Escribimos el texto SIN bordes y medimos altura usada
            self.set_text_color(255, 255, 255)

            for texto, w, align in zip(celdas, widths, aligns):
                x_actual = self.get_x()
                y_actual = self.get_y()

                self.multi_cell(w, line_height, texto, border=0, align=align)

                max_y = max(max_y, self.get_y())
                self.set_xy(x_actual + w, y_actual)

            # Volvemos al texto negro para el dibujo real
            self.set_text_color(0, 0, 0)

            # Altura que pide solo el texto
            row_height_text = max_y - y_fila

            # Altura que pide solo el texto
            row_height_text = max_y - y_fila

            # 2️⃣ Si hay fotos, aseguramos una altura mínima para que quepan
            row_height = row_height_text

            if fotos_paths:
                # altura "tipo tarjeta" mínima para fotos
                altura_min_fotos = 25  # mm aprox
                if row_height < altura_min_fotos:
                    row_height = altura_min_fotos
                    max_y = y_fila + row_height

            # 🔥 2.1 (OPCIONAL) Límite máximo de altura para que la fila no sea gigante
            max_row_height_fotos = 80  # ajústalo 60–80 según veas
            if row_height > max_row_height_fotos:
                row_height = max_row_height_fotos
                max_y = y_fila + row_height

            # 3️⃣ Dibujamos los rectángulos de la fila con la altura final
            x_actual = x_fila
            for w in widths:
                self.rect(x_actual, y_fila, w, row_height)
                x_actual += w

            # 3.1️⃣ Segundo pase: escribir el texto centrado verticalmente
            # Desplazamiento de toda la "franja de texto" dentro de la altura final
            offset_fila = (row_height - row_height_text) / 2
            if offset_fila < 0:
                offset_fila = 0

            # Nos posicionamos al inicio de la fila, pero un poco más abajo
            self.set_xy(x_fila, y_fila + offset_fila)

            for texto, w, align in zip(celdas, widths, aligns):
                x_actual = self.get_x()
                y_actual = self.get_y()

                self.multi_cell(w, line_height, texto, border=0, align=align)

                # Pasar a la siguiente celda en la misma fila
                self.set_xy(x_actual + w, y_actual)

            # 4️⃣ Dibujar imágenes en la última columna (Fotografías),
            #     MISMA ALTURA, CON PEQUEÑA SEPARACIÓN ENTRE ELLAS
            if fotos_paths:
                from PIL import Image

                x_fotos = x_fila + sum(widths[:-1])
                w_fotos = widths[-1]

                margin_vertical = 2      # margen arriba/abajo
                margin_side = 0          # margen contra el borde de la celda
                gap = 2                  # 👈 separación ENTRE fotos (visible pero pequeña)

                # ancho útil descontando bordes y los gaps internos
                fotos_mostrar = fotos_paths[:3]
                num_fotos = len(fotos_mostrar)

                if num_fotos > 0:
                    disp_w = w_fotos - 2 * margin_side - (num_fotos - 1) * gap
                    disp_h = row_height - 2 * margin_vertical

                    h_base = disp_h

                    # calcular anchos en función de la altura
                    anchos = []
                    for foto in fotos_mostrar:
                        try:
                            with Image.open(foto) as img:
                                img_w, img_h = img.size
                            ratio = img_w / img_h      # ancho / alto
                            anchos.append(h_base * ratio)
                        except Exception as e:
                            print(f"⚠️ Error cargando imagen {foto}: {e}")
                            anchos.append(0)

                    suma_anchos = sum(anchos)

                    # escalar si no caben en el ancho útil
                    if suma_anchos > disp_w and suma_anchos > 0:
                        factor = disp_w / suma_anchos
                        anchos = [w * factor for w in anchos]
                        h_base = h_base * factor

                    # dibujar fotos con gap entre ellas
                    x_img = x_fotos + margin_side
                    y_img = y_fila + margin_vertical

                    for foto, w_obj in zip(fotos_mostrar, anchos):
                        if w_obj <= 0:
                            continue
                        try:
                            self.image(foto, x=x_img, y=y_img, w=w_obj, h=h_base)
                        except Exception as e:
                            print(f"⚠️ Error dibujando imagen {foto}: {e}")

                        # 👉 avanza ancho de la foto + separación
                        x_img += w_obj + gap



            # 5️⃣ Cursor al inicio de la siguiente fila
            self.set_xy(x_fila, max_y)



        # 🔁 AHORA SÍ: recorremos el DataFrame y dibujamos cada fila
        max_row_height = 25  # por ejemplo

        # 🔁 Recorremos el DataFrame y dibujamos cada fila
        for _, row in df_dia.iterrows():
        
            # ------------------------------------------------
            # 0. Comprobar espacio disponible en la página
            # ------------------------------------------------
            espacio_disponible = (
                self.h
                - self.bottom_margin
                - self.footer_height
                - self.get_y()
            )

            if espacio_disponible < max_row_height:
                # Nueva página
                self.add_page()

                # Redibujar encabezado de la tabla
                self.set_font("Helvetica", "B", 8)
                self.set_fill_color(230, 230, 230)
                self.set_text_color(0, 0, 0)

                y_inicio_tabla = self.get_y() + 10
                x_inicio_tabla = self.left_margin
                self.set_xy(x_inicio_tabla, y_inicio_tabla)

                for header, w in zip(headers, widths_order):
                    self.cell(w, line_height * 2, header, border=1, align="C", fill=True)
                self.ln(line_height * 2)

                # Fuente normal para las filas
                self.set_font("Helvetica", "", 8)

            # ------------------------------------------------
            # 1. FECHA en formato dd-mm-aaaa (siempre string)
            # ------------------------------------------------
            try:
                f = row["FECHA"]

                if isinstance(f, str):
                    fecha_str = f.strip()
                elif hasattr(f, "strftime"):
                    fecha_str = f.strftime("%d-%m-%Y")
                else:
                    fecha_str = fecha_dia.strftime("%d-%m-%Y")
            except Exception:
                fecha_str = fecha_dia.strftime("%d-%m-%Y")

            # ------------------------------------------------
            # 2. Valores numéricos formateados
            # ------------------------------------------------
            v_unit = float(row["VALOR_UNITARIO"])
            v_total = float(row["VALOR_TOTAL"])
            v_unit_str = f"{v_unit:,.0f}".replace(",", ".")
            v_total_str = f"{v_total:,.0f}".replace(",", ".")

            # ------------------------------------------------
            # 3. Celdas de texto
            # ------------------------------------------------
            celdas = [
                fecha_str,
                str(row["ZONA"]),
                str(row["DESCRIPCION"]),
                str(row["UNIDAD_MEDIDA"]),
                str(row["CANTIDAD"]),
                v_unit_str,
                v_total_str,
                ""  # texto en Fotografías (no lo usamos)
            ]

            # ------------------------------------------------
            # 4. Buscar fotos de la actividad (si ya tienes ID_ACTIVIDAD)
            # ------------------------------------------------
            fotos_paths = []
            if "ID_ACTIVIDAD" in df_dia.columns:
                id_act = str(row["ID_ACTIVIDAD"]).strip()
                carpeta_fotos = os.path.join("BD", "FOTOS", "ACTIVIDADES_FOTOS", id_act)
                if os.path.isdir(carpeta_fotos):
                    for nombre in sorted(os.listdir(carpeta_fotos)):
                        if nombre.lower().endswith((".jpg", ".jpeg", ".png")):
                            fotos_paths.append(os.path.join(carpeta_fotos, nombre))

            # ------------------------------------------------
            # 5. Dibujar la fila (texto + fotos)
            # ------------------------------------------------
            _dibujar_fila(celdas, widths_order, fotos_paths=fotos_paths)
