import pyodbc

class ConexionBD():
    def __init__(self):
        self.conexion = ""

    def establecerConexionBD(self):
        try:
            self.conexion = pyodbc.connect('DRIVER={SQL Server};SERVER=DIEGOJR;DATABASE=Empresa_Construccion;UID=sa;PWD=Diego!2025')
            print('Conexión establecida')
        except Exception as ex:
            print('No se pudo establecer conexión')
            print("Error=", ex)

    def cerrarConexion(self):
        self.conexion.close()