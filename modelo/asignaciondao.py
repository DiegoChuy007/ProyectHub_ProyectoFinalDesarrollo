# asignaciondao.py
from modelo.asignacion import Asignacion
from modelo.conexionbd import ConexionBD 
# Importamos otros DAOs para verificación de FKs (Mantenemos la importación)
from modelo.proyectodao import ProyectoDAO 
from modelo.empleadodao import EmpleadoDAO 

class AsignacionDAO:

    def __init__(self):
        self.asignacion = Asignacion()
        self.bd = ConexionBD()
        self.proyectodao = ProyectoDAO()
        self.empleadodao = EmpleadoDAO()
        
    def _limpiar_cursor(self, cursor):
        """Descarta todos los conjuntos de resultados intermedios y pendientes."""
        try:
             while cursor.nextset():
                 pass
        except Exception:
             pass

    # ----------------------------------------------------------------------
    # --- CREATE: Guardar una nueva asignación (con validación de unicidad)
    # ----------------------------------------------------------------------
    def guardarAsignacion(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        
        id_proyecto = self.asignacion.id_proyecto
        id_empleado = self.asignacion.id_empleado
        
        try:
            # *******************************************************************
            # ** CAMBIO: Confiamos en que la BD maneje la restricción de FK. **
            # ** Si el ID no existe, la BD lanzará una excepción que capturamos. **
            # *******************************************************************
            
            # # 1. VERIFICACIÓN DE EXISTENCIA DE FK (Clave Externa)
            # # Esto es propenso a errores si los DAOs externos no funcionan.
            # # Lo comentamos para que la restricción FK de la BD tome el control.
            # if not self.proyectodao.buscarProyectoPorId(id_proyecto):
            #      raise Exception(f"El Proyecto con ID {id_proyecto} no existe.")
            
            # if not self.empleadodao.buscarEmpleadoPorId(id_empleado):
            #      raise Exception(f"El Empleado con ID {id_empleado} no existe.")

            # 2. VERIFICACIÓN DE UNICIDAD (No duplicar la asignación)
            # Si tienes un UNIQUE INDEX en la BD para (id_proyecto, id_empleado), 
            # puedes comentar esto también y confiar en la BD. 
            # Lo mantenemos por si la BD no tiene el índice.
            sql_check = "SELECT id_asignacion FROM asignacion_proyecto WHERE id_proyecto = ? AND id_empleado = ?"
            cursor.execute(sql_check, (id_proyecto, id_empleado))
            existe = cursor.fetchone()
            
            self._limpiar_cursor(cursor)
            
            if existe:
                raise Exception("Esta asignación (Empleado a Proyecto) ya existe en la base de datos.")

            # 3. INSERTAR (Omitimos id_asignacion porque es IDENTITY)
            sp = "EXEC [dbo].[sp_insertar_asignacion] @id_proyecto=?, @id_empleado=?"
            
            param = (id_proyecto, id_empleado)
            
            self._limpiar_cursor(cursor) # Limpiamos antes de la inserción del SP
            cursor.execute(sp, param)
            cursor.commit()
            self.bd.cerrarConexion()
            
        except Exception as e:
            self.bd.conexion.rollback()
            self.bd.cerrarConexion()
            # Mensaje mejorado para incluir la posible causa de FK
            raise Exception(f"No se pudo guardar la asignación. Verifique la validez de los IDs (FKs) o si la asignación ya existe.\nDetalle: {e}")

    # ----------------------------------------------------------------------
    # --- CRUD Estándar (Sin cambios, asumen correcto funcionamiento)
    # ----------------------------------------------------------------------

    def listarAsignaciones(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        # SP idealmente devuelve: ID Asignación, ID Proyecto, ID Empleado (o Nombres)
        sp = "EXEC [dbo].[sp_listar_asignaciones]" 
        
        self._limpiar_cursor(cursor)
        cursor.execute(sp)
        
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    def buscarAsignacionPorId(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 
        sp = 'EXEC [dbo].[sp_buscar_asignacion_por_id] @id_asignacion=?'
        param = (self.asignacion.id_asignacion,) 
        
        self._limpiar_cursor(cursor)
        cursor.execute(sp, param)
        
        fila = cursor.fetchone()
        self.bd.cerrarConexion()
        return fila

    def actualizarAsignacion(self):
        """Actualiza la asignación (cambia las FKs) usando id_asignacion (PK)."""
        self.bd.establecerConexionBD()
        # Puedes añadir aquí la validación de FKs si quieres hacerla explícita, 
        # pero es mejor confiar en la BD.
        sp = "EXEC [dbo].[sp_actualizar_asignacion] @id_asignacion=?, @id_proyecto=?, @id_empleado=?"
        
        param = (
            self.asignacion.id_asignacion,
            self.asignacion.id_proyecto,
            self.asignacion.id_empleado, 
        )
        cursor = self.bd.conexion.cursor()
        self._limpiar_cursor(cursor)
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

    def eliminarAsignacion(self):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_eliminar_asignacion] @id_asignacion=?"
        param = (self.asignacion.id_asignacion,)

        cursor = self.bd.conexion.cursor()
        self._limpiar_cursor(cursor)
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()