from modelo.empleado import Empleado
from modelo.conexionbd import ConexionBD 

class EmpleadoDAO:

    def __init__(self):
        self.empleado = Empleado()
        self.bd = ConexionBD()

    # ----------------------------------------------------------------------
    # --- CREATE: Guardar un nuevo empleado (IDENTITY ACTIVO)
    # ----------------------------------------------------------------------
    def guardarEmpleado(self):
        self.bd.establecerConexionBD()
        
        # El SP modificado solo espera Nombre y Cargo
        sp = "EXEC [dbo].[sp_insertar_empleado] @Nombre=?, @Cargo=?"
        
        param = (self.empleado.nombre, self.empleado.cargo)
        
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()
        
    # ----------------------------------------------------------------------
    # --- READ (All): Listar todos los empleados (para tabla de consulta)
    # ----------------------------------------------------------------------
    def listarEmpleados(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        sp = "EXEC [dbo].[sp_listar_empleados]"
        cursor.execute(sp)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    # ----------------------------------------------------------------------
    # --- READ (One): Buscar un empleado por ID
    # ----------------------------------------------------------------------
    def buscarEmpleadoPorId(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 
        sp = 'EXEC [dbo].[sp_buscar_empleado_por_id] @id_empleado=?'
        param = (self.empleado.id_empleado,) 
        cursor.execute(sp, param)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    # ----------------------------------------------------------------------
    # --- UPDATE: Actualizar un empleado existente
    # ----------------------------------------------------------------------
    def actualizarEmpleado(self):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_actualizar_empleado] @id_empleado=?, @Nombre=?, @Cargo=?"
        param = (
            self.empleado.id_empleado, 
            self.empleado.nombre, 
            self.empleado.cargo
        )
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

    # ----------------------------------------------------------------------
    # --- DELETE: Eliminar un empleado
    # ----------------------------------------------------------------------
    def eliminarEmpleado(self):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_eliminar_empleado] @id_empleado=?"
        param = (self.empleado.id_empleado,)

        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()