# load_ui_salarios.py
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox
from modelo.salariodao import SalarioDAO 
from modelo.salario import Salario 
import decimal 

# Tarifa base por día usada para calcular el Importe Total en el Gasto asociado.
TARIFA_BASE_POR_DIA = 100.00 

class Load_ui_salarios(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ui_salarios.ui", self) 
        self.show()
        self.salariodao = SalarioDAO()
        self.current_id_salario = None 

        # --- Configuración Inicial y Conexiones (Se mantiene igual) ---
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        if hasattr(self, "tabla_consulta"):
            self.tabla_consulta.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tabla_consulta.clicked.connect(self.cargar_datos_desde_tabla)

        if hasattr(self, "boton_salir"): self.boton_salir.clicked.connect(lambda: self.close())
        if hasattr(self, "frame_superior"): self.frame_superior.mouseMoveEvent = self.mover_ventana
        if hasattr(self, "boton_menu"): self.boton_menu.clicked.connect(self.mover_menu)

        if hasattr(self, "stackedWidget"):
            self.boton_agregar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_agregar))
            self.boton_consultar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_consultar))
            self.boton_consultar.clicked.connect(self.actualizar_tabla)
            self.boton_buscar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_buscar))
            self.boton_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
            self.boton_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
            self.actualizar_tabla() 
            
        if hasattr(self, "accion_guardar"): self.accion_guardar.clicked.connect(self.guardar_salario)
        if hasattr(self, "accion_actualizar"): self.accion_actualizar.clicked.connect(self.actualizar_salario)
        if hasattr(self, "accion_eliminar"): self.accion_eliminar.clicked.connect(self.eliminar_salario)
        if hasattr(self, "accion_limpiar"): self.accion_limpiar.clicked.connect(self.limpiar_formulario)
        if hasattr(self, "refresh"): self.refresh.clicked.connect(self.actualizar_tabla)
        
        if hasattr(self, "buscar_actualizar"): self.buscar_actualizar.clicked.connect(lambda: self.buscar_salario('actualizar'))
        if hasattr(self, "buscar_eliminar"): self.buscar_eliminar.clicked.connect(lambda: self.buscar_salario('eliminar'))
        if hasattr(self, "buscar_buscar"): self.buscar_buscar.clicked.connect(lambda: self.buscar_salario('buscar'))


    # ----------------------------------------------------------------------
    # --- FUNCIONES DE VALIDACIÓN Y UTILIDAD ---
    # ----------------------------------------------------------------------

    def validar_campos_numericos(self, dias_text, descuentos_text, bonos_text, id_empleado_text, id_gasto_text):
        """Valida y convierte los campos numéricos."""
        try:
            dias = int(dias_text)
            desc = float(descuentos_text)
            bonos = float(bonos_text)
            
            id_emp = int(id_empleado_text)
            if id_emp <= 0:
                 return False, "El ID de Empleado debe ser un número entero positivo."
            
            id_g = int(id_gasto_text)
            if id_g < 0:
                 return False, "El ID de Gasto no puede ser negativo."

            if dias < 0 or desc < 0 or bonos < 0:
                return False, "Días trabajados, Descuentos y Bonos no pueden ser negativos."
                
            return True, (dias, desc, bonos, id_emp, id_g)
        except ValueError:
            return False, "Días, Descuentos, Bonos e IDs deben ser números válidos."
        except Exception as e:
            return False, f"Error inesperado en la validación: {e}"
    
    # ----------------------------------------------------------------------
    # --- FUNCIONES CRUD (GUARDAR CORREGIDO CON TRANSACCIÓN MAESTRA) ---
    # ----------------------------------------------------------------------

    def guardar_salario(self):
        """Inserta un nuevo registro de salario, asegurando Empleado y Gasto mediante transacción maestra."""
        # 1. Obtener y validar datos de la UI
        id_empleado = self.idempleado_agregar.text().strip()
        id_gasto = self.idgasto_agregar.text().strip()
        dias_trabajados = self.diastrabajados_agregar.text().strip()
        descuentos = self.descuentos_agregar.text().strip()
        bonos = self.bonos_agregar.text().strip()
        nombre_empleado = self.nombre_agregar_2.text().strip()
        
        if not nombre_empleado:
             QMessageBox.warning(self, "Error de Validación", "El Nombre del empleado es obligatorio.")
             return
        
        es_valido, datos = self.validar_campos_numericos(dias_trabajados, descuentos, bonos, id_empleado, id_gasto)
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", datos)
            return

        dias, desc, bonos, id_emp, id_g = datos

        try:
            # 2. Asignar todos los campos al objeto DAO (incluyendo el Nombre para el SP de Empleado)
            self.salariodao.salario.dias_trabajados = dias
            self.salariodao.salario.descuentos = desc
            self.salariodao.salario.bonos = bonos
            self.salariodao.salario.id_empleado = id_emp 
            self.salariodao.salario.id_gasto = id_g
            self.salariodao.salario.nombre_empleado = nombre_empleado 
            
            # 3. Ejecutar el DAO que maneja la transacción maestra para las 3 tablas.
            # Devuelve los IDs REALES y confirmados.
            id_empleado_final, id_gasto_final = self.salariodao.guardarSalario()
            
            QMessageBox.information(self, "Éxito", f"Salario guardado correctamente. ID Empleado final: {id_empleado_final}, ID Gasto final: {id_gasto_final}.")
            self.limpiar_formulario(page='agregar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar el salario.\nDetalle: {e}")

    # --- El resto de funciones CRUD (actualizar_salario, eliminar_salario, buscar_salario, etc.) se mantienen igual ---
    
    def buscar_salario(self, page_name):
        """Busca un salario por ID_Empleado y ID_Gasto y rellena los campos."""
        
        id_empleado_field = getattr(self, f"idempleado_{page_name}")
        id_gasto_field = getattr(self, f"idgasto_{page_name}")
        
        id_empleado_text = id_empleado_field.text().strip()
        id_gasto_text = id_gasto_field.text().strip()
        
        try:
            id_empleado = int(id_empleado_text)
            id_gasto = int(id_gasto_text)
            if id_empleado <= 0 or id_gasto <= 0:
                QMessageBox.warning(self, "Error de Validación", "Los IDs deben ser enteros positivos.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error de Validación", "Los IDs deben ser números enteros válidos.")
            return

        try:
            self.salariodao.salario.id_empleado = id_empleado
            self.salariodao.salario.id_gasto = id_gasto
            
            datos = self.salariodao.buscarSalarioPorIds() 
            
            if datos:
                d = datos[0] 
                self.current_id_salario = d[0] 
                
                getattr(self, f"diastrabajados_{page_name}").setText(str(d[1]))
                getattr(self, f"descuentos_{page_name}").setText(f"{float(d[2]):.2f}")
                getattr(self, f"bonos_{page_name}").setText(f"{float(d[3]):.2f}")
                
                if hasattr(self, f"nombre_{page_name}"):
                    getattr(self, f"nombre_{page_name}").setText(d[6])
                
                QMessageBox.information(self, "Éxito", f"Salario encontrado. PK (ID Salario): {self.current_id_salario}.")
                
            else:
                QMessageBox.warning(self, "No Encontrado", f"No se encontró un salario para el Empleado {id_empleado} y Gasto {id_gasto}.")
                self.limpiar_formulario(page=page_name, preserve_ids=True) 
                self.current_id_salario = None
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al buscar el salario.\nDetalle: {e}")

    def actualizar_salario(self):
        """Actualiza un salario existente."""
        if self.current_id_salario is None:
            QMessageBox.warning(self, "Error de Operación", "Debe buscar un salario (usando ID Empleado y ID Gasto) primero para actualizar.")
            return

        id_empleado = self.idempleado_actualizar.text().strip()
        id_gasto = self.idgasto_actualizar.text().strip()
        dias_trabajados = self.diastrabajados_actualizar.text().strip()
        descuentos = self.descuentos_actualizar.text().strip()
        bonos = self.bonos_actualizar.text().strip()

        es_valido, datos = self.validar_campos_numericos(dias_trabajados, descuentos, bonos, id_empleado, id_gasto)
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", datos)
            return

        dias, desc, bonos, id_emp, id_g = datos

        try:
            # Nota: El id_empleado ya debe existir antes de actualizar.
            self.salariodao.salario.dias_trabajados = dias
            self.salariodao.salario.descuentos = desc
            self.salariodao.salario.bonos = bonos
            
            self.salariodao.actualizarSalario(self.current_id_salario)
            
            QMessageBox.information(self, "Éxito", f"Salario (PK: {self.current_id_salario}) actualizado correctamente.")
            self.limpiar_formulario(page='actualizar')
            self.actualizar_tabla()
            self.current_id_salario = None
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar salario.\nDetalle: {e}")

    def eliminar_salario(self):
        """Elimina un salario por su PK (obtenido tras la búsqueda)."""
        if self.current_id_salario is None:
            QMessageBox.warning(self, "Error de Operación", "Debe buscar un salario primero para eliminar.")
            return

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Está seguro de eliminar el salario (PK: {self.current_id_salario})?",
                                            QMessageBox.Yes | QMessageBox.No)
        
        if confirmacion == QMessageBox.Yes:
            try:
                self.salariodao.eliminarSalario(self.current_id_salario)
                
                QMessageBox.information(self, "Éxito", f"Salario (PK: {self.current_id_salario}) eliminado correctamente.")
                self.limpiar_formulario(page='eliminar')
                self.actualizar_tabla()
                self.current_id_salario = None

            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo eliminar el salario.\nDetalle: {e}")

    def actualizar_tabla(self):
        """Carga todos los salarios en la tabla de consulta (6 columnas)."""
        try:
            datos = self.salariodao.listarSalarios() 
            self.tabla_consulta.setRowCount(0)
            
            if self.tabla_consulta.columnCount() != 6:
                 QMessageBox.warning(self, "Error de Configuración", "La tabla de consulta debe tener exactamente 6 columnas.")
                 return

            if datos:
                self.tabla_consulta.setRowCount(len(datos))
                
                for fila_idx, item in enumerate(datos):
                    try:
                        id_empleado = str(item[0])
                        id_gasto = str(item[1])
                        dias_trabajados = int(item[2])
                        descuentos = float(item[3]) 
                        bonos = float(item[4])
                        nombre = str(item[5])
                    except (ValueError, TypeError) as e:
                        QMessageBox.critical(self, "Error de Conversión de Datos", f"Error en la fila {fila_idx+1} al convertir datos. Detalle: {e}")
                        continue 

                    self.tabla_consulta.setItem(fila_idx, 0, QtWidgets.QTableWidgetItem(id_empleado))
                    self.tabla_consulta.setItem(fila_idx, 1, QtWidgets.QTableWidgetItem(id_gasto))
                    self.tabla_consulta.setItem(fila_idx, 2, QtWidgets.QTableWidgetItem(str(dias_trabajados)))
                    self.tabla_consulta.setItem(fila_idx, 3, QtWidgets.QTableWidgetItem(f"{descuentos:.2f}"))
                    self.tabla_consulta.setItem(fila_idx, 4, QtWidgets.QTableWidgetItem(f"{bonos:.2f}"))
                    self.tabla_consulta.setItem(fila_idx, 5, QtWidgets.QTableWidgetItem(nombre))
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Tabla", f"Error al cargar la lista de salarios.\nDetalle: {e}")


    def cargar_datos_desde_tabla(self):
        """Carga los datos visibles de la fila seleccionada a los formularios de Actualizar y Eliminar."""
        fila_seleccionada = self.tabla_consulta.currentRow()
        if fila_seleccionada < 0: return
        
        try:
            id_empleado_str = self.tabla_consulta.item(fila_seleccionada, 0).text()
            id_gasto_str = self.tabla_consulta.item(fila_seleccionada, 1).text()
            dias_trabajados = self.tabla_consulta.item(fila_seleccionada, 2).text()
            descuentos = self.tabla_consulta.item(fila_seleccionada, 3).text()
            bonos = self.tabla_consulta.item(fila_seleccionada, 4).text()
            nombre = self.tabla_consulta.item(fila_seleccionada, 5).text()
            
            if hasattr(self, 'idempleado_actualizar'): self.idempleado_actualizar.setText(id_empleado_str)
            if hasattr(self, 'idgasto_actualizar'): self.idgasto_actualizar.setText(id_gasto_str)
            if hasattr(self, 'diastrabajados_actualizar'): self.diastrabajados_actualizar.setText(dias_trabajados)
            if hasattr(self, 'descuentos_actualizar'): self.descuentos_actualizar.setText(descuentos)
            if hasattr(self, 'bonos_actualizar'): self.bonos_actualizar.setText(bonos)
            if hasattr(self, 'nombre_actualizar'): self.nombre_actualizar.setText(nombre)
            
            if hasattr(self, 'idempleado_eliminar'): self.idempleado_eliminar.setText(id_empleado_str)
            if hasattr(self, 'idgasto_eliminar'): self.idgasto_eliminar.setText(id_gasto_str)
            if hasattr(self, 'diastrabajados_eliminar'): self.diastrabajados_eliminar.setText(dias_trabajados)
            if hasattr(self, 'descuentos_eliminar'): self.descuentos_eliminar.setText(descuentos)
            if hasattr(self, 'bonos_eliminar'): self.bonos_eliminar.setText(bonos)
            if hasattr(self, 'nombre_eliminar'): self.nombre_eliminar.setText(nombre)
            
            self.current_id_salario = None 
            
            self.stackedWidget.setCurrentWidget(self.page_actualizar)
                
        except Exception as e:
             QMessageBox.critical(self, "Error de Carga", f"Error al cargar datos desde la tabla.\nDetalle: {e}")


    def limpiar_formulario(self, page=None, preserve_ids=False):
        """
        Limpia los campos de la página actual usando el patrón de mapeo por diccionario
        (similar a Proyecto), manejando la lógica de IDs de Salario.
        """
        
        # 1. Definición de campos por página para Salarios
        page_fields = {
            'agregar': [
                # ID Salario es IDENTITY, no se usa aquí.
                'idempleado_agregar', 'idgasto_agregar', 
                'diastrabajados_agregar', 'descuentos_agregar', 'bonos_agregar', 'nombre_agregar'
            ],
            'actualizar': [
                'idsalario_actualizar', 'idempleado_actualizar', 'idgasto_actualizar', 
                'diastrabajados_actualizar', 'descuentos_actualizar', 'bonos_actualizar', 'nombre_actualizar'
            ],
            'eliminar': [
                'idsalario_eliminar', 'idempleado_eliminar', 'idgasto_eliminar', 
                'diastrabajados_eliminar', 'descuentos_eliminar', 'bonos_eliminar', 'nombre_eliminar'
            ],
            'buscar': [
                'idsalario_buscar', # Criterio de búsqueda (si buscas por ID Salario)
                'idempleado_buscar', # Criterio de búsqueda (si buscas por ID Empleado)
                # Resultados que deben limpiarse después de una búsqueda:
                'idgasto_buscar', 'diastrabajados_buscar', 'descuentos_buscar', 'bonos_buscar', 'nombre_buscar'
            ] 
        }
        
        # 2. Determinar la página clave
        try:
            # Si 'page' es None, toma la clave del stackedWidget
            page_key = page if page else self.stackedWidget.currentWidget().objectName().replace('page_', '')
        except Exception:
            page_key = 'desconocido'
        
        # 3. Obtener la lista de campos a limpiar
        fields_to_clear = page_fields.get(page_key, [])

        # 4. Iterar y limpiar los LineEdits
        for field_name in fields_to_clear:
            # Manejo especial para IDs si preserve_ids=True (típico en buscar/actualizar)
            # Nota: Desactivamos la preservación si la página es 'agregar' o 'buscar' por defecto, 
            # ya que no tiene sentido dejar IDs viejos en esos formularios.
            if preserve_ids and page_key not in ['agregar', 'buscar']:
                 # Si el campo es un ID y se pide preservarlo, lo saltamos
                 if field_name.startswith('idsalario_') or field_name.startswith('idempleado_') or field_name.startswith('idgasto_'):
                     continue
            
            field = getattr(self, field_name, None)
            if field and hasattr(field, 'clear'): field.clear()
        
        # 5. Lógica adicional para Salarios
        if hasattr(self, 'tabla_buscar') and page_key == 'buscar':
             self.tabla_buscar.setRowCount(0)
             
        # Limpiar variable de estado de Salario (asumo que existe)
        if page_key in ['actualizar', 'eliminar'] or page is None:
             if hasattr(self, 'current_id_salario'):
                 self.current_id_salario = None


    # ----------------------------------------------------------------------
    # --- FUNCIONES DE VENTANA (Mover/Menú) ---
    # ----------------------------------------------------------------------

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def mover_ventana(self, event):
        if not self.isMaximized():			
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()

    def mover_menu(self):
        width = self.frame_lateral.width()
        extender = 200 if width == 0 else 0
        self.boton_menu.setText("Menú" if width == 0 else "")
            
        self.animacion = QPropertyAnimation(self.frame_lateral, b'minimumWidth')
        self.animacion.setDuration(300)
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacion.start()
        
        self.animacionb = QPropertyAnimation(self.boton_menu, b'minimumWidth')
        self.animacionb.setDuration(300)
        self.animacionb.setStartValue(width)
        self.animacionb.setEndValue(extender)
        self.animacionb.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacionb.start()