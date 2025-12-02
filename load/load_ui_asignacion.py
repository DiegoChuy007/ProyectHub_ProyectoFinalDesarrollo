# load_ui_asignacion.py
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox

from modelo.asignaciondao import AsignacionDAO 
from modelo.asignacion import Asignacion 

class Load_ui_asignacion(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ui_asignacion.ui", self) 
        self.show()
        self.asignaciondao = AsignacionDAO()

        # --- Configuración Inicial ---
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        if hasattr(self, "tabla_consulta"):
            self.tabla_consulta.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tabla_consulta.clicked.connect(self.cargar_datos_desde_tabla)

        # --- Conexiones de la UI ---
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
            
        # Acciones CRUD y Búsqueda
        if hasattr(self, "accion_guardar"): self.accion_guardar.clicked.connect(self.guardar_asignacion)
        if hasattr(self, "accion_actualizar"): self.accion_actualizar.clicked.connect(self.actualizar_asignacion)
        if hasattr(self, "accion_eliminar"): self.accion_eliminar.clicked.connect(self.eliminar_asignacion)
        if hasattr(self, "accion_limpiar"): self.accion_limpiar.clicked.connect(self.limpiar_formulario)
        if hasattr(self, "refresh"): self.refresh.clicked.connect(self.actualizar_tabla)
        
        # Criterio de búsqueda: id_asignacion
        if hasattr(self, "buscar_actualizar"): self.buscar_actualizar.clicked.connect(lambda: self.buscar_asignacion('actualizar'))
        if hasattr(self, "buscar_eliminar"): self.buscar_eliminar.clicked.connect(lambda: self.buscar_asignacion('eliminar'))
        if hasattr(self, "buscar_buscar"): self.buscar_buscar.clicked.connect(lambda: self.buscar_asignacion('buscar'))


    # ----------------------------------------------------------------------
    # --- FUNCIONES DE UTILIDAD ---
    # ----------------------------------------------------------------------
    
    def validar_id_entero_positivo(self, id_text, field_name="ID"):
        """Valida si un texto es un ID entero positivo."""
        try:
            val = int(id_text)
            if val <= 0:
                 return False, f"El {field_name} debe ser un número entero positivo."
            return True, val
        except ValueError:
            return False, f"El {field_name} debe ser un número entero válido."

    # ----------------------------------------------------------------------
    # --- FUNCIONES CRUD ---
    # ----------------------------------------------------------------------

    def guardar_asignacion(self):
        """Inserta una nueva asignación."""
        # id_asignacion (idasignacion_agregar) no se usa ya que es IDENTITY.
        id_proyecto_text = self.idproyecto_agregar.text().strip()
        id_empleado_text = self.idempleado_agregar.text().strip()

        # Validación de campos
        if not id_proyecto_text or not id_empleado_text:
            QMessageBox.warning(self, "Error de Validación", "ID Proyecto y ID Empleado son obligatorios.")
            return

        es_valido_p, id_proyecto = self.validar_id_entero_positivo(id_proyecto_text, "ID Proyecto")
        if not es_valido_p:
            QMessageBox.warning(self, "Error de Validación", id_proyecto)
            return

        es_valido_e, id_empleado = self.validar_id_entero_positivo(id_empleado_text, "ID Empleado")
        if not es_valido_e:
            QMessageBox.warning(self, "Error de Validación", id_empleado)
            return

        try:
            self.asignaciondao.asignacion.id_proyecto = id_proyecto
            self.asignaciondao.asignacion.id_empleado = id_empleado
            
            self.asignaciondao.guardarAsignacion()
            
            QMessageBox.information(self, "Éxito", "Asignación guardada correctamente.")
            self.limpiar_formulario(page='agregar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar la asignación.\nDetalle: {e}")


    def actualizar_asignacion(self):
        """Actualiza una asignación existente (usa ID_ASIGNACION)."""
        idasignacion_text = self.idasignacion_actualizar.text().strip()
        id_proyecto_text = self.idproyecto_actualizar.text().strip()
        id_empleado_text = self.idempleado_actualizar.text().strip()

        # Validación de campos
        if not idasignacion_text or not id_proyecto_text or not id_empleado_text:
            QMessageBox.warning(self, "Error de Validación", "Todos los campos son obligatorios.")
            return

        es_valido_a, id_asignacion = self.validar_id_entero_positivo(idasignacion_text, "ID Asignación")
        if not es_valido_a:
            QMessageBox.warning(self, "Error de Validación", id_asignacion)
            return

        es_valido_p, id_proyecto = self.validar_id_entero_positivo(id_proyecto_text, "ID Proyecto")
        if not es_valido_p:
            QMessageBox.warning(self, "Error de Validación", id_proyecto)
            return

        es_valido_e, id_empleado = self.validar_id_entero_positivo(id_empleado_text, "ID Empleado")
        if not es_valido_e:
            QMessageBox.warning(self, "Error de Validación", id_empleado)
            return

        try:
            self.asignaciondao.asignacion.id_asignacion = id_asignacion
            self.asignaciondao.asignacion.id_proyecto = id_proyecto
            self.asignaciondao.asignacion.id_empleado = id_empleado
            
            self.asignaciondao.actualizarAsignacion()
            
            QMessageBox.information(self, "Éxito", f"Asignación ID {id_asignacion} actualizada correctamente.")
            self.limpiar_formulario(page='actualizar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar asignación.\nDetalle: {e}")


    def eliminar_asignacion(self):
        """Elimina una asignación por ID_ASIGNACION."""
        idasignacion_text = self.idasignacion_eliminar.text().strip() 
        
        es_valido, id_asignacion = self.validar_id_entero_positivo(idasignacion_text, "ID Asignación")
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_asignacion)
            return

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Está seguro de eliminar la Asignación con ID {id_asignacion}?",
                                            QMessageBox.Yes | QMessageBox.No)
        
        if confirmacion == QMessageBox.Yes:
            try:
                self.asignaciondao.asignacion.id_asignacion = id_asignacion
                self.asignaciondao.eliminarAsignacion()
                
                QMessageBox.information(self, "Éxito", f"Asignación ID {id_asignacion} eliminada correctamente.")
                self.limpiar_formulario(page='eliminar')
                self.actualizar_tabla()

            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo eliminar la asignación.\nDetalle: {e}")


    def buscar_asignacion(self, page_name):
        """Busca una asignación por ID_ASIGNACION (criterio principal)."""
        
        idasignacion_field = getattr(self, f"idasignacion_{page_name}")
        idasignacion_text = idasignacion_field.text().strip()

        es_valido, id_asignacion = self.validar_id_entero_positivo(idasignacion_text, "ID Asignación")
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_asignacion)
            return
        
        try:
            self.asignaciondao.asignacion.id_asignacion = id_asignacion
            # Datos: (ID_Asignacion=0, ID_Proyecto=1, ID_Empleado=2)
            datos = self.asignaciondao.buscarAsignacionPorId() 
            
            if datos:
                # El DAO devuelve una tupla directamente
                d = datos 
                
                # Llenar los campos de la página actual
                getattr(self, f"idasignacion_{page_name}").setText(str(d[0]))
                getattr(self, f"idproyecto_{page_name}").setText(str(d[1]))
                getattr(self, f"idempleado_{page_name}").setText(str(d[2]))

                QMessageBox.information(self, "Éxito", f"Asignación ID {id_asignacion} encontrada.")
            else:
                QMessageBox.warning(self, "No Encontrado", f"No se encontró Asignación con ID {id_asignacion}.")
                self.limpiar_formulario(page=page_name, clear_id_asignacion=False) 

        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al buscar la asignación.\nDetalle: {e}")


    def actualizar_tabla(self):
        """Carga todas las asignaciones en la tabla de consulta."""
        try:
            # Datos: (ID_Asignacion=0, ID_Proyecto=1, ID_Empleado=2)
            datos = self.asignaciondao.listarAsignaciones() 
            
            if not hasattr(self, 'tabla_consulta'): return
            self.tabla_consulta.setRowCount(0)
            
            if datos:
                self.tabla_consulta.setRowCount(len(datos))
                
                for fila_idx, item in enumerate(datos):
                    # Se asume que la tabla_consulta tiene 3 columnas
                    self.tabla_consulta.setItem(fila_idx, 0, QtWidgets.QTableWidgetItem(str(item[0]))) # ID_ASIGNACION
                    self.tabla_consulta.setItem(fila_idx, 1, QtWidgets.QTableWidgetItem(str(item[1]))) # ID_PROYECTO
                    self.tabla_consulta.setItem(fila_idx, 2, QtWidgets.QTableWidgetItem(str(item[2]))) # ID_EMPLEADO
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Tabla", f"Error al cargar la lista de asignaciones.\nDetalle: {e}")


    def cargar_datos_desde_tabla(self):
        """Carga los datos de la fila seleccionada a los formularios de Actualizar y Eliminar."""
        if not hasattr(self, 'tabla_consulta'): return
        fila_seleccionada = self.tabla_consulta.currentRow()
        if fila_seleccionada < 0: return

        try:
            # Índice de columna de la tabla (UI): 0: ID asignación, 1: ID proyecto, 2: ID empleado
            idasignacion = self.tabla_consulta.item(fila_seleccionada, 0).text()
            id_proyecto = self.tabla_consulta.item(fila_seleccionada, 1).text()
            id_empleado = self.tabla_consulta.item(fila_seleccionada, 2).text()
            
            # Llenar Actualizar
            if hasattr(self, 'idasignacion_actualizar'): self.idasignacion_actualizar.setText(idasignacion)
            if hasattr(self, 'idproyecto_actualizar'): self.idproyecto_actualizar.setText(id_proyecto)
            if hasattr(self, 'idempleado_actualizar'): self.idempleado_actualizar.setText(id_empleado)
            
            # Llenar Eliminar
            if hasattr(self, 'idasignacion_eliminar'): self.idasignacion_eliminar.setText(idasignacion)
            if hasattr(self, 'idproyecto_eliminar'): self.idproyecto_eliminar.setText(id_proyecto)
            if hasattr(self, 'idempleado_eliminar'): self.idempleado_eliminar.setText(id_empleado)

            self.stackedWidget.setCurrentWidget(self.page_actualizar)
                
        except Exception as e:
             QMessageBox.critical(self, "Error de Carga", f"Error al cargar datos desde la tabla.\nDetalle: {e}")


    def limpiar_formulario(self, page=None, clear_id_asignacion=True):
        """
        Limpia los campos de la página actual usando el patrón de mapeo por diccionario,
        manteniendo la lógica de 'clear_id_asignacion' para búsquedas.
        """

        # 1. Definición de campos por página para Asignación
        # Note que 'idasignacion' solo se incluye si clear_id_asignacion es True (ver paso 4)
        page_fields = {
            'agregar': [
                'idproyecto_agregar', 
                'idempleado_agregar'
            ],
            'actualizar': [
                'idasignacion_actualizar', 
                'idproyecto_actualizar', 
                'idempleado_actualizar'
            ],
            'eliminar': [
                'idasignacion_eliminar', 
                'idproyecto_eliminar', 
                'idempleado_eliminar'
            ],
            'buscar': [
                'idasignacion_buscar', 
                'idproyecto_buscar', 
                'idempleado_buscar'
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
            
            # Lógica especial para 'clear_id_asignacion' (Usado en buscar_asignacion)
            if 'idasignacion' in field_name and not clear_id_asignacion:
                 # Si es el ID principal y se pide preservarlo (e.g., al no encontrar la búsqueda), lo saltamos
                 continue

            field = getattr(self, field_name, None)
            if field and hasattr(field, 'clear'): field.clear()
            
        # 5. Lógica adicional (Limpiar tabla si es necesario)
        if page_key == 'buscar' and hasattr(self, 'tabla_buscar'):
             self.tabla_buscar.setRowCount(0)

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