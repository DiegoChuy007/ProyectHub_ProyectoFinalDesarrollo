# salariodao.py
from modelo.salario import Salario
from modelo.conexionbd import ConexionBD 
import decimal 

class SalarioDAO:

    def __init__(self):
        self.salario = Salario()
        self.bd = ConexionBD()

    def _limpiar_cursor(self, cursor):
        """Descarta todos los conjuntos de resultados intermedios y pendientes."""
        try:
             # Iterar y descartar todos los result sets pendientes (filas afectadas, etc.)
             while cursor.nextset():
                 pass
        except Exception:
             pass

    def _obtener_id_final(self, cursor, id_opt, nombre_entidad):
        """Intenta obtener el ID final (existente o generado) de la BD."""
        id_final = None
        
        # Leemos el resultado, que DEBE ser el ID final (ej: SCOPE_IDENTITY)
        while True:
            fila = cursor.fetchone()
            if fila is not None:
                id_final = fila[0]
                break
            # Intentar pasar al siguiente conjunto de resultados si no hay filas
            if not cursor.nextset():
                break
        
        # Validamos el resultado
        if id_final is None or id_final <= 0:
             # Si no se encontró el ID, la transacción falló
             raise Exception(f"Fallo al obtener el ID final de {nombre_entidad} desde la BD.")

        return id_final

    # ----------------------------------------------------------------------
    # --- MÉTODOS AUXILIARES DE FK (Transacción Única)
    # ----------------------------------------------------------------------
    
    def _asegurarEmpleado_aux(self, cursor, id_empleado_opt, nombre_empleado):
        """Inserta/Verifica el Empleado y devuelve el ID final."""
        
        # 1. Limpieza PREVIA (vital para despejar resultados del SP anterior)
        self._limpiar_cursor(cursor)

        sp = "EXEC [dbo].[sp_asegurar_empleado] @id_empleado_opt=?, @nombre_empleado=?"
        cursor.execute(sp, (id_empleado_opt, nombre_empleado))
        
        # 2. Lectura del ID final
        id_empleado_final = self._obtener_id_final(cursor, id_empleado_opt, 'Empleado')
        
        return id_empleado_final

    def _asegurarGasto_aux(self, cursor, id_gasto_opt, importe_gasto):
        """Inserta/Verifica el Gasto y devuelve el ID final."""
        
        # 1. Limpieza PREVIA 
        self._limpiar_cursor(cursor)

        sp = "EXEC [dbo].[sp_asegurar_gasto] @id_gasto_opt=?, @tipo_gasto=?, @importe_total=?"
        cursor.execute(sp, (id_gasto_opt, 'Salario', importe_gasto))
        
        # 2. Lectura del ID final
        id_gasto_final = self._obtener_id_final(cursor, id_gasto_opt, 'Gasto')
        
        return id_gasto_final

    # ----------------------------------------------------------------------
    # --- CREATE: Guardar un nuevo salario (TRANSACCIÓN MAESTRA)
    # ----------------------------------------------------------------------
    def guardarSalario(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        
        try:
            # 1. Obtener datos y calcular importe
            id_empleado_opt = self.salario.id_empleado
            id_gasto_opt = self.salario.id_gasto
            nombre_empleado = self.salario.nombre_empleado
            
            importe_base = self.salario.dias_trabajados * 100.00
            importe_gasto = float(decimal.Decimal(importe_base - self.salario.descuentos + self.salario.bonos))
            
            # 2. Asegurar FKs usando el cursor actual (misma transacción)
            id_empleado_final = self._asegurarEmpleado_aux(cursor, id_empleado_opt, nombre_empleado)
            id_gasto_final = self._asegurarGasto_aux(cursor, id_gasto_opt, importe_gasto)

            # 3. Insertar Salario
            sp = "EXEC [dbo].[sp_insertar_salario] @dias_trabajados=?, @descuentos=?, @bonos=?, @id_empleado=?, @id_gasto=?"
            
            param = (
                str(self.salario.dias_trabajados), 
                str(self.salario.descuentos),      
                str(self.salario.bonos),           
                id_empleado_final,                 
                id_gasto_final                     
            )
            
            # Limpieza del cursor antes de la inserción final del salario
            self._limpiar_cursor(cursor)
            
            cursor.execute(sp, param)
            
            # COMMIT ÚNICO: Todas las inserciones se confirman aquí.
            cursor.commit()
            return id_empleado_final, id_gasto_final 
            
        except Exception as e:
            self.bd.conexion.rollback()
            raise Exception(f"Error al guardar salario: {e}")
        finally:
             self.bd.cerrarConexion()

    # ----------------------------------------------------------------------
    # --- Los demás métodos CRUD (listado, búsqueda, actualización, eliminación)
    # ----------------------------------------------------------------------
    
    def listarSalarios(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor()
        sp = "EXEC [dbo].[sp_listar_salarios]"
        self._limpiar_cursor(cursor) # Limpiar por si acaso
        cursor.execute(sp)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    def buscarSalarioPorIds(self):
        self.bd.establecerConexionBD()
        cursor = self.bd.conexion.cursor() 
        sp = 'EXEC [dbo].[sp_buscar_salario_por_ids] @id_empleado=?, @id_gasto=?'
        param = (self.salario.id_empleado, self.salario.id_gasto) 
        self._limpiar_cursor(cursor) # Limpiar por si acaso
        cursor.execute(sp, param)
        filas = cursor.fetchall()
        self.bd.cerrarConexion()
        return filas

    def actualizarSalario(self, id_salario_pk):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_actualizar_salario] @id_salario=?, @dias_trabajados=?, @descuentos=?, @bonos=?"
        param = (
            id_salario_pk, 
            str(self.salario.dias_trabajados), 
            str(self.salario.descuentos), 
            str(self.salario.bonos)
        )
        cursor = self.bd.conexion.cursor()
        self._limpiar_cursor(cursor) # Limpiar por si acaso
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()

    def eliminarSalario(self, id_salario_pk):
        self.bd.establecerConexionBD()
        sp = "EXEC [dbo].[sp_eliminar_salario] @id_salario=?"
        param = (id_salario_pk,)

        cursor = self.bd.conexion.cursor()
        self._limpiar_cursor(cursor) # Limpiar por si acaso
        cursor.execute(sp, param)
        cursor.commit()
        self.bd.cerrarConexion()