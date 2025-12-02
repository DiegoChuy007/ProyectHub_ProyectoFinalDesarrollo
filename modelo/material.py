# material.py
class Material():
    def __init__(self):
        # PK: Se autogenera en la BD (o se maneja de otra forma si no es IDENTITY)
        self.id_material = 0 
        # Tipo corresponde al 'Material' en la UI
        self.tipo = "" 
        self.cantidad = "" 
        # FK: id_gasto es el ID generado que une al material con el gasto
        self.id_gasto = 0
        # GASTO: importe_total mapea al campo 'Gasto' (el monto) de la UI
        self.importe_total = 0.0