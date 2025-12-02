# gastodao.py
from modelo.gasto import Gasto
from modelo.conexionbd import ConexionBD 
import decimal 

class GastoDAO:

    def __init__(self):
        self.gasto = Gasto()
        self.bd = ConexionBD()

    # ----------------------------------------------------------------------
    # --- FK CONTROL: Asegura que el proyecto exista para evitar errores
    # ----------------------------------------------------------------------
    def asegurarProyectoExistente(self, id_proyecto):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()

        try:
            # 1. Verificar si el proyecto existe
            sql_check = "SELECT id_proyecto FROM Proyecto WHERE id_proyecto = ?"
            cursor.execute(sql_check, (id_proyecto,))
            existe = cursor.fetchone()
            
            try: cursor.nextset()
            except Exception: pass
            
            if not existe:
                # 2. Si NO existe, insertarlo
                # Usaremos la fecha actual (o una cadena simple) para fecha_inicio, ya que Proyecto no tiene 'nombre'
                fecha_defecto = "Proyecto agregado automáticamente" 
                
                sp_insert_proyecto = "EXEC [dbo].[sp_insertar_proyecto_desde_gasto] @id_proyecto=?, @nombre_proyecto=?"
                cursor.execute(sp_insert_proyecto, (id_proyecto, fecha_defecto))
                
                try: cursor.nextset()
                except Exception: pass
            
            cursor.commit()

        except Exception as e:
            self.bd.conexion.rollback()
            raise Exception(f"Error al asegurar la existencia del Proyecto: {e}")
        finally:
             self.bd.cerrarConexion()

    # ----------------------------------------------------------------------
    # --- CREATE/UPSERT FLEXIBLE
    # ----------------------------------------------------------------------
    def upsertGastoFlexible(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        
        id_gasto_entrada = self.gasto.id_gasto
        
        try:
            # 1. Verificar si el Gasto ya existe (solo si se proporciona un ID > 0)
            if id_gasto_entrada > 0:
                sql_check = "SELECT id_gasto FROM gastos WHERE id_gasto = ?"
                cursor.execute(sql_check, (id_gasto_entrada,))
                existe = cursor.fetchone()
                
                try: cursor.nextset()
                except Exception: pass
                
                if existe:
                    # Caso A: El Gasto existe, lo actualizamos.
                    self.actualizarGasto() 
                    return id_gasto_entrada
                
            # 2. Inserción (Gasto nuevo o ID forzado no existente)
            sp_insert = "EXEC [dbo].[sp_insertar_gasto] @id_gasto_opt=?, @tipo=?, @fecha=?, @id_proyecto=?, @importe_total=?"
            
            param = (
                id_gasto_entrada, 
                self.gasto.tipo,
                self.gasto.fecha,
                self.gasto.id_proyecto,
                self.gasto.importe_total
            )
            
            cursor.execute(sp_insert, param)
            
            id_gasto_final = id_gasto_entrada 
            
            # Si se envió 0, obtener el ID autogenerado/generado por el SP
            if id_gasto_entrada == 0:
                while True:
                    fila = cursor.fetchone()
                    if fila is not None:
                        id_gasto_final = fila[0]
                        break
                    if not cursor.nextset():
                        break
                
                if id_gasto_final == 0:
                    raise Exception("El Gasto fue insertado con ID 0. El SP no devolvió un ID final.")

            cursor.commit()
            self.bd.cerrarConexion()
            return id_gasto_final
            
        except Exception as e:
            self.bd.conexion.rollback()
            self.bd.cerrarConexion()
            raise Exception(f"Error al ejecutar upsert flexible de gasto: {e}")

    # ----------------------------------------------------------------------
    # --- CRUD Estándar (Los demás métodos CRUD permanecen igual)
    # ----------------------------------------------------------------------
    
    def actualizarGasto(self):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_actualizar_gasto] @id_gasto=?, @tipo=?, @fecha=?, @id_proyecto=?, @importe_total=?"
        param = (
            self.gasto.id_gasto, 
            self.gasto.tipo,
            self.gasto.fecha,
            self.gasto.id_proyecto,
            self.gasto.importe_total
        )
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

    def listarGastos(self):
        # ... (código listarGastos)
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        sp = "EXEC [dbo].[sp_listar_gastos]"
        cursor.execute(sp)
        filas = cursor.fetchall() 
        self.bd.cerrarConexion()
        return filas

    def buscarGastoPorId(self):
        # ... (código buscarGastoPorId)
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 
        sp = 'EXEC [dbo].[sp_buscar_gasto_por_id] @id_gasto=?'
        param = (self.gasto.id_gasto,) 
        cursor.execute(sp, param)
        filas = cursor.fetchall() 
        self.bd.cerrarConexion()
        return filas

    def eliminarGasto(self):
        # ... (código eliminarGasto)
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_eliminar_gasto] @id_gasto=?"
        param = (self.gasto.id_gasto,)

        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()