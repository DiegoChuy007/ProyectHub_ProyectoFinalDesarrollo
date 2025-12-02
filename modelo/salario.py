class Salario():
    def __init__(self):
        self.id_salario = 0          # PK (Identity)
        self.dias_trabajados = 0
        self.descuentos = 0.00
        self.bonos = 0.00
        self.id_empleado = 0         # FK
        self.id_gasto = 0            # FK
        self.nombre_empleado = ""    # Campo extra para la UI