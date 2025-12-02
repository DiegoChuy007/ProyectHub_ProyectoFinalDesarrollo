# asignacion.py
class Asignacion():
    def __init__(self):
        # PK: Autogenerada por la BD (IDENTITY)
        self.id_asignacion = 0         
        # FKs: Claves obligatorias
        self.id_proyecto = 0
        self.id_empleado = 0