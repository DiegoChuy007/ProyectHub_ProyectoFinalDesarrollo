# modelo/ubicaciondao.py (CORREGIDO)

from modelo.conexionbd import ConexionBD 

class UbicacionDAO:

    def __init__(self):
        self.bd = ConexionBD()

    def verificarOInsertar(self, ciudad, calle, colonia, numero):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 

        # 1. BÚSQUEDA (SELECT - NO CAMBIA)
        sql_select = """
            SELECT id_ubicacion FROM Ubicacion 
            WHERE ciudad = ? AND calle = ? AND colonia = ? AND numero = ?
        """
        params_select = (ciudad, calle, colonia, numero)
        cursor.execute(sql_select, params_select)
        fila = cursor.fetchone()

        if fila:
            self.bd.cerrarConexion()
            return int(fila[0])  # Retorna el ID existente
        
        # --- 2. INSERCIÓN (INSERT USANDO SP) ---
        else:
            try:
                # Llama al SP
                sp_insert = "EXEC [dbo].[sp_insertar_ubicacion] @calle=?, @colonia=?, @numero=?, @ciudad=?"
                params_insert = (calle, colonia, numero, ciudad)
                
                cursor.execute(sp_insert, params_insert)
                
                # --- CORRECCIÓN CRÍTICA ---
                # Forzar el avance del cursor al resultado del SELECT SCOPE_IDENTITY()
                cursor.nextset() 
                # -------------------------
                
                # El SP devuelve el ID generado, así que lo capturamos directamente
                id_result = cursor.fetchone() 
                
                if id_result is None or id_result[0] is None:
                    self.bd.conexion.rollback()
                    raise Exception("Fallo al obtener SCOPE_IDENTITY. La inserción fue rechazada por la DB.")
                
                id_generado = id_result[0]
                
                self.bd.conexion.commit()
                return int(id_generado)

            except Exception as ex:
                self.bd.conexion.rollback()
                # Relanzamos el error (que ahora contendrá el mensaje de violación de restricción del SP)
                raise Exception(f"Error de Transacción al insertar Ubicación (vía SP): {ex}")
            finally:
                self.bd.cerrarConexion()