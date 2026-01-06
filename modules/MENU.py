import pandas as pd

class AdminFechas:
    MESES_NOMBRE_A_NUM = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    MESES_NUM_A_NOMBRE = {v: k for k, v in MESES_NOMBRE_A_NUM.items()}

    def __init__(self):
        self.anio = None
        self.mes = None

    # --- Solicitar año ---
    def solicitar_anio(self):
        while True:
            anio_str = input("Ingrese el año (4 dígitos, ej. 2025): ").strip()
            if anio_str.isdigit() and len(anio_str) == 4:
                anio = int(anio_str)
                if 1900 <= anio <= 2100:
                    self.anio = anio
                    return
            print("⚠️  Año inválido. Intente de nuevo (ej. 2025).")

    # --- Mostrar menú de meses ---
    def mostrar_menu_meses(self):
        print("\nElija el mes (número o nombre):")
        for i in range(1, 13):
            print(f"{i:>2}. {self.MESES_NUM_A_NOMBRE[i].capitalize()}")

    # --- Convertir entrada a número de mes ---
    def parsear_mes(self, opcion: str) -> int:
        op = opcion.strip().lower()
        # Si es número válido
        if op.isdigit():
            mes = int(op)
            if 1 <= mes <= 12:
                return mes
        # Si es nombre
        if op in self.MESES_NOMBRE_A_NUM:
            return self.MESES_NOMBRE_A_NUM[op]
        # Si es abreviatura
        for nombre, num in self.MESES_NOMBRE_A_NUM.items():
            if nombre.startswith(op) and len(op) >= 3:
                return num
        raise ValueError("Mes inválido.")

    # --- Solicitar mes ---
    def solicitar_mes(self):
        while True:
            self.mostrar_menu_meses()
            opcion = input("Mes: ")
            try:
                self.mes = self.parsear_mes(opcion)
                return
            except ValueError:
                print("⚠️  Entrada de mes no válida. Intente de nuevo (ej. 11 o 'noviembre').")

    # --- Obtener rango de fechas ---
    def rango_fechas_25a25(self) -> pd.DatetimeIndex:
        if self.anio is None or self.mes is None:
            raise ValueError("Debe definir año y mes antes de generar el rango.")
        if self.mes == 1:
            anio_ant, mes_ant = self.anio - 1, 12
        else:
            anio_ant, mes_ant = self.anio, self.mes - 1
        inicio = pd.Timestamp(anio_ant, mes_ant, 26)
        fin = pd.Timestamp(self.anio, self.mes, 25)
        return pd.date_range(start=inicio, end=fin, freq='D')

    # --- Ejecutar menú interactivo ---
    def ejecutar(self):
        print("=== Menú de selección de fechas ===")
        self.solicitar_anio()
        self.solicitar_mes()
        print(f"\n✔ Año: {self.anio} | Mes: {self.mes} ({self.MESES_NUM_A_NOMBRE[self.mes].capitalize()})")

        fechas = self.rango_fechas_25a25()
        print(f"Rango: {fechas[0].date()} → {fechas[-1].date()} ({len(fechas)} días)")
        return fechas

    # --- nombre del mes anterior ---
    def nombre_mes_anterior(self) -> str:
        if self.mes == 1:
            mes_ant = 12
        else:
            mes_ant = self.mes - 1
        return self.MESES_NUM_A_NOMBRE[mes_ant].capitalize()
    
    # --- nombre del mes actual ---
    def nombre_mes_actual(self) -> str:
        return self.MESES_NUM_A_NOMBRE[self.mes].capitalize()
    
