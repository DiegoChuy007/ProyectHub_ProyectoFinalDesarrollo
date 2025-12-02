from modelo.proyecto import Proyecto
from modelo.conexionbd import ConexionBD

class ProyectoDAO:

    def __init__(self):
        self.proyecto = Proyecto()
        self.bd = ConexionBD()
        
    # --- Métodos de Ayuda (Buscar por ID de Proyecto) ---
    def buscarProyectoPorId(self, id_proyecto):
        """Busca proyecto por ID (clave primaria) y devuelve una tupla de 11 campos o None."""
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 
        # SP: sp_buscar_proyecto_por_id (asume que devuelve 11 campos: P.*, U.*)
        sp = 'EXEC [dbo].[sp_buscar_proyecto_por_id] @id_proyecto=?'
        param = (id_proyecto,)
        cursor.execute(sp, param)
        fila = cursor.fetchone() # Usamos fetchone()
        self.bd.cerrarConexion()
        return fila # Retorna tupla o None

    # --- CRUD Implementado ---
        
# modelo/proyectodao.py

# ... (código anterior) ...
    def guardarProyecto(self):
        self.bd.establecerConexionBD()
        
        # CAMBIO CLAVE: Agregar @id_proyecto=? al SP y al tuple de parámetros
        sp = "EXEC [dbo].[sp_insertar_proyecto] @id_proyecto=?, @fecha_inicio=?, @fecha_aprox_finalizacion=?, @estatus_obra=?, @precio_venta=?, @rentabilidad=?, @id_ubicacion=?"
        
        param = (
            self.proyecto.id_proyecto, # <-- AÑADIDO
            self.proyecto.fecha_inicio, 
            self.proyecto.fecha_aprox_finalizacion, 
            self.proyecto.estatus_obra, 
            self.proyecto.precio_venta, 
            self.proyecto.rentabilidad, 
            self.proyecto.id_ubicacion
        )
        
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

# ... (código posterior) ... 
        
    def listarProyectos(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        # SP: sp_listar_proyectos (asume 10 campos: id_proyecto + 5 propios + 4 de ubicación)
        sp = "EXEC [dbo].[sp_listar_proyectos]"
        cursor.execute(sp)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    def buscarProyectoPorIdProyecto(self):
        return self.buscarProyectoPorId(self.proyecto.id_proyecto)

    def actualizarProyecto(self):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_actualizar_proyecto] @id_proyecto=?, @fecha_inicio=?, @fecha_aprox_finalizacion=?, @estatus_obra=?, @precio_venta=?, @rentabilidad=?, @id_ubicacion=?"
        param = (self.proyecto.id_proyecto, self.proyecto.fecha_inicio, self.proyecto.fecha_aprox_finalizacion, 
                 self.proyecto.estatus_obra, self.proyecto.precio_venta, self.proyecto.rentabilidad, 
                 self.proyecto.id_ubicacion)
        
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

    def eliminarProyecto(self):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_eliminar_proyecto] @id_proyecto=?"
        param = (self.proyecto.id_proyecto,)
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()
    
    def obtenerResumenGlobal(self):
        """
        Llama al SP para obtener (ProyectosActivos, TotalProyectos, CostosAcumulados, RentabilidadGlobal)
        y maneja la limpieza del cursor de manera agresiva.
        """
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        
        sp = "EXEC [dbo].[sp_obtener_resumen_global]"
        
        try:
            # 1. Limpieza antes de la ejecución (para limpiar residuos de comandos anteriores)
            self._limpiar_cursor(cursor)
            
            cursor.execute(sp)
            
            # 2. Limpieza de Resultados Intermedios (Si el SP tiene INSERTs/UPDATEs/PRINTs)
            # Aunque ya está en _limpiar_cursor, a veces es necesario hacerlo de forma más visible:
            
            while True:
                # Intentamos consumir el resultado, si no es el final.
                resumen = cursor.fetchone()
                
                # Si encontramos un resultado, asumimos que es la tupla final (lo que acabas de ver)
                if resumen is not None:
                    # Nos aseguramos de limpiar cualquier conjunto de resultados restante
                    self._limpiar_cursor(cursor)
                    return resumen 
                
                # Si no hay filas, intentamos pasar al siguiente conjunto de resultados (nextset)
                if not cursor.nextset():
                    break # Salir si no hay más conjuntos de resultados

            # Si el código llega aquí sin devolver, significa que el SP no devolvió la tupla final.
            raise Exception("El SP no devolvió el conjunto de resultados esperado (tupla de 4).")

        except Exception as e:
            raise Exception(f"Error al ejecutar el SP de resumen: {e}")
        finally:
            self.bd.cerrarConexion()
    
    def _limpiar_cursor(self, cursor):
        """Descarta todos los conjuntos de resultados intermedios y pendientes."""
        try:
             # Iterar y descartar todos los result sets pendientes (filas afectadas, mensajes, etc.)
             while cursor.nextset():
                 pass
        except Exception:
             # Ignorar errores si no hay más result sets
             pass