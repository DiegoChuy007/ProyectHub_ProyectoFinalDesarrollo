class Proyecto():
    def __init__(self):
        self.id_proyecto = 0
        self.fecha_inicio = ""
        self.fecha_aprox_finalizacion = ""
        self.estatus_obra = ""
        self.precio_venta = ""
        self.rentabilidad = ""
        
        # Clave foránea que se guarda en la DB
        self.id_ubicacion = 0
        
        # Campos de ubicación combinada (solo para visualización/interfaz)
        self.ciudad = ""
        self.calle = ""
        self.colonia = ""
        self.numero = ""