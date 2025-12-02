# materialdao.py
from modelo.material import Material
from modelo.conexionbd import ConexionBD 
import decimal 

class MaterialDAO:

    def __init__(self):
        self.material = Material()
        self.bd = ConexionBD()

    # ----------------------------------------------------------------------
    # --- CREATE/UPSERT FLEXIBLE: Maneja ID de Gasto y Material (4 Casos)
    # ----------------------------------------------------------------------
    def guardarMaterialFlexible(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()

        try:
            # 1. Declaraciones iniciales
            tipo = self.material.tipo
            # Convertimos a INT para la lógica interna y operaciones de suma/monto
            cantidad_int = int(self.material.cantidad) 
            importe_nuevo = decimal.Decimal(self.material.importe_total)
            id_gasto_entrada = self.material.id_gasto 
            id_gasto_a_usar = None
            
            # Como la columna 'cantidad' en la BD es VARCHAR(50),
            # convertimos a string SÓLO para la inserción final.
            cantidad_str = str(cantidad_int) 

            # ------------------------------------------------------------------
            # 1. --- Caso: EL MATERIAL YA EXISTE CON ESE MISMO ID DE GASTO ---
            #
            # Criterio de existencia: Tipo (Material) Y id_gasto (Clave Compuesta)
            # ------------------------------------------------------------------
            
            # --- Búsqueda Corregida (Incluye @id_gasto) ---
            # NOTA: Este SP debe estar creado en la BD y buscar por id_gasto y tipo.
            sp_buscar_mat = "EXEC sp_obtener_material_existente_por_gasto_y_tipo @Tipo=?, @id_gasto=?"
            # Usamos id_gasto_entrada para la búsqueda
            cursor.execute(sp_buscar_mat, (tipo, id_gasto_entrada)) 
            existente = cursor.fetchone()

            # Limpieza de cursor después del SELECT
            try: cursor.nextset()
            except Exception: pass

            if existente:
                # El material con ese ID de Gasto y Tipo ya existe. 
                # Se reutiliza el id_gasto existente y se suman los valores.
                id_gasto_existente = existente[0] # Será igual a id_gasto_entrada
                
                # Ejecutar la suma de cantidad e importe
                sp_sumar = "EXEC sp_sumar_material_y_gasto @id_gasto=?, @cantidad_sumar=?, @importe_sumar=?"
                cursor.execute(sp_sumar, (id_gasto_existente, cantidad_int, importe_nuevo))
                
                # Limpiar cursor después del EXEC
                try: cursor.nextset()
                except Exception: pass
                
                cursor.commit()
                self.bd.cerrarConexion()
                return id_gasto_existente

            # ------------------------------------------------------------------
            # 2. --- Caso: MATERIAL NO EXISTE (Manejo de Gasto) ---
            # ------------------------------------------------------------------

            # A. Si se proporcionó un ID de Gasto (> 0) Y el material NO existía en ese Gasto
            if id_gasto_entrada > 0:
                sp_verificar_gasto = "SELECT id_gasto FROM gastos WHERE id_gasto = ?"
                cursor.execute(sp_verificar_gasto, (id_gasto_entrada,))
                gasto_existe = cursor.fetchone()

                # Limpieza de cursor después del SELECT
                try: cursor.nextset()
                except Exception: pass

                if gasto_existe:
                    # Gasto existente. Lo reutilizamos y actualizamos su importe.
                    id_gasto_a_usar = id_gasto_entrada
                    sp_actualizar_gasto = "UPDATE gastos SET importe_total = importe_total + ? WHERE id_gasto = ?"
                    cursor.execute(sp_actualizar_gasto, (importe_nuevo, id_gasto_a_usar))
                    
                    # Limpiar cursor después del UPDATE
                    try: cursor.nextset() 
                    except Exception: pass
                    
                else:
                    # Gasto no existente. Creamos el Gasto con ID forzado (si la BD lo permite).
                    sp_insert_gasto = "EXEC sp_insertar_gasto_material_con_id @id_gasto=?, @TipoGasto=?, @ImporteTotal=?"
                    
                    # Limpiamos cursores (antes de un EXEC)
                    try: cursor.nextset()
                    except Exception: pass
                    
                    cursor.execute(sp_insert_gasto, (id_gasto_entrada, tipo, importe_nuevo))
                    id_gasto_a_usar = id_gasto_entrada

            # B. Si NO se proporcionó un ID de Gasto (id_gasto_entrada == 0)
            else:
                # Gasto nuevo y autogenerado
                sp_insert_gasto = "EXEC sp_insertar_gasto_material @TipoGasto=?, @ImporteTotal=?"
                
                # Limpiamos cursores (antes de un EXEC)
                try: cursor.nextset()
                except Exception: pass
                    
                cursor.execute(sp_insert_gasto, (tipo, importe_nuevo))

                # Lógica para obtener el ID autogenerado (desde el SP)
                id_gasto_a_usar = None
                while True:
                    fila = cursor.fetchone()
                    if fila is not None:
                        id_gasto_a_usar = fila[0]
                        break
                    if not cursor.nextset():
                        break
                
                if not id_gasto_a_usar:
                    raise Exception("No se obtuvo el ID del gasto autogenerado.")


            # 3. Finalmente, se inserta el nuevo material (INSERCIÓN DIRECTA)
            
            # Comando SQL que especifica las columnas (tipo, cantidad, id_gasto)
            sql_insert_material = "INSERT INTO Materiales (tipo, cantidad, id_gasto) VALUES (?, ?, ?)"
            
            # Limpieza de cursor antes de la última inserción
            try:
                cursor.nextset()
            except Exception:
                pass 
                
            # Ejecutar el INSERT SQL directo
            cursor.execute(sql_insert_material, (tipo, cantidad_str, id_gasto_a_usar))

            cursor.commit()
            self.bd.cerrarConexion()
            return id_gasto_a_usar

        except Exception as e:
            self.bd.conexion.rollback()
            self.bd.cerrarConexion()
            raise Exception(f"Error guardar material flexible: {e}")
            
    # ----------------------------------------------------------------------
    # --- Los demás métodos se mantienen sin cambios ---
    # ----------------------------------------------------------------------
    def listarMateriales(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        # SP debe devolver: (id_gasto, tipo, cantidad, importe_total)
        sp = "EXEC [dbo].[sp_listar_materiales]"
        cursor.execute(sp)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    def buscarMaterialPorIdGastoYMaterial(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 
        # SP debe devolver: (id_gasto, tipo, cantidad, importe_total)
        sp = 'EXEC [dbo].[sp_buscar_material_por_idgasto] @id_gasto=?, @tipo=?'
        
        # Los parámetros son: (id_gasto, tipo)
        param = (self.material.id_gasto, self.material.tipo) 
        
        cursor.execute(sp, param)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    def actualizarMaterial(self):
        self.bd.establecerConexionBD()
        # SP debe recibir: @id_gasto (clave), @tipo (clave), @cantidad_nueva
        sp = "EXEC [dbo].[sp_actualizar_material_cantidad] @id_gasto=?, @tipo=?, @cantidad_nueva=?"
        
        param = (
            self.material.id_gasto, 
            self.material.tipo, 
            self.material.cantidad # Nueva cantidad
        )
        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

    def eliminarMaterial(self):
        self.bd.establecerConexionBD()
        # SP debe recibir: @id_gasto (clave), @tipo (clave)
        sp = "EXEC [dbo].[sp_eliminar_material_individual] @id_gasto=?, @tipo=?"
        param = (self.material.id_gasto, self.material.tipo)

        cursor = self.bd.conexion.cursor()
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()