import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox

from modelo.empleadodao import EmpleadoDAO 

class Load_ui_empleados(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ui_empleados.ui", self) 
        self.show()
        self.empleadodao = EmpleadoDAO()

        # --- Configuración Inicial ---
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        if hasattr(self, "tabla_consulta"):
            self.tabla_consulta.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tabla_consulta.clicked.connect(self.cargar_datos_desde_tabla)

        # --- Conexiones de la UI ---
        if hasattr(self, "boton_salir"): self.boton_salir.clicked.connect(lambda: self.close())
        if hasattr(self, "frame_superior"): self.frame_superior.mouseMoveEvent = self.mover_ventana
        if hasattr(self, "boton_menu"): self.boton_menu.clicked.connect(self.mover_menu)

        if hasattr(self, "stackedWidget"):
            # Navegación (Corregido 'page_consulta' a 'page_consultar')
            self.boton_agregar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_agregar))
            self.boton_consultar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_consultar))
            self.boton_consultar.clicked.connect(self.actualizar_tabla)
            self.boton_buscar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_buscar))
            self.boton_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
            self.boton_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
            self.actualizar_tabla() 
            
        # Acciones CRUD y Búsqueda (Conexión de la Lupa)
        if hasattr(self, "accion_guardar"): self.accion_guardar.clicked.connect(self.guardar_empleado)
        if hasattr(self, "accion_actualizar"): self.accion_actualizar.clicked.connect(self.actualizar_empleado)
        if hasattr(self, "accion_eliminar"): self.accion_eliminar.clicked.connect(self.eliminar_empleado)
        if hasattr(self, "accion_limpiar"): self.accion_limpiar.clicked.connect(self.limpiar_formulario)
        if hasattr(self, "refresh"): self.refresh.clicked.connect(self.actualizar_tabla)
        
        # Conexión de los botones de la lupa para buscar por ID (Criterio: ID_empleado)
        if hasattr(self, "buscar_actualizar"): self.buscar_actualizar.clicked.connect(self.buscar_empleado)
        if hasattr(self, "buscar_eliminar"): self.buscar_eliminar.clicked.connect(self.buscar_empleado)
        if hasattr(self, "buscar_buscar"): self.buscar_buscar.clicked.connect(self.buscar_empleado)


    # ----------------------------------------------------------------------
    # --- FUNCIONES CRUD (CON IDENTITY) ---
    # ----------------------------------------------------------------------

    def validar_id_entero(self, id_text):
        """Valida si un texto es un ID entero positivo (usado para UPDATE/SEARCH/DELETE)."""
        try:
            empleado_id = int(id_text)
            if empleado_id <= 0:
                 return False, "El ID debe ser un número entero positivo."
            return True, empleado_id
        except ValueError:
            return False, "El ID debe ser un número entero válido."


    def guardar_empleado(self):
        """Inserta un nuevo empleado, dejando que la DB genere el ID."""
        nombre = self.nombre_agregar.text().strip()
        cargo = self.cargo_agregar.text().strip()
        
        if not nombre or not cargo:
            QMessageBox.warning(self, "Error de Validación", "Nombre y Cargo son obligatorios.")
            return

        try:
            self.empleadodao.empleado.nombre = nombre
            self.empleadodao.empleado.cargo = cargo
            
            self.empleadodao.guardarEmpleado()
            
            QMessageBox.information(self, "Éxito", "Empleado guardado correctamente (ID generado por DB).")
            self.limpiar_formulario(page='agregar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar el empleado.\nDetalle: {e}")


    def actualizar_empleado(self):
        """Actualiza un empleado existente."""
        id_text = self.idempleado_actualizar.text().strip()
        nombre = self.nombre_actualizar.text().strip()
        cargo = self.cargo_actualizar.text().strip()

        es_valido, id_empleado = self.validar_id_entero(id_text)
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_empleado)
            return

        if not nombre or not cargo:
            QMessageBox.warning(self, "Error de Validación", "Nombre y Cargo son obligatorios.")
            return

        try:
            self.empleadodao.empleado.id_empleado = id_empleado
            self.empleadodao.empleado.nombre = nombre
            self.empleadodao.empleado.cargo = cargo
            
            self.empleadodao.actualizarEmpleado()
            
            QMessageBox.information(self, "Éxito", f"Empleado ID {id_empleado} actualizado correctamente.")
            self.limpiar_formulario(page='actualizar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar empleado.\nDetalle: {e}")


    def eliminar_empleado(self):
        """Elimina un empleado por ID."""
        id_text = self.idempleado_eliminar.text().strip()
        
        es_valido, id_empleado = self.validar_id_entero(id_text)
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_empleado)
            return

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Está seguro de eliminar al empleado con ID {id_empleado}?",
                                            QMessageBox.Yes | QMessageBox.No)
        
        if confirmacion == QMessageBox.Yes:
            try:
                self.empleadodao.empleado.id_empleado = id_empleado
                
                self.empleadodao.eliminarEmpleado()
                
                QMessageBox.information(self, "Éxito", f"Empleado ID {id_empleado} eliminado correctamente.")
                self.limpiar_formulario(page='eliminar')
                self.actualizar_tabla()

            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo eliminar el empleado.\nDetalle: {e}")


    def buscar_empleado(self):
        """Busca un empleado por ID y rellena los campos de la página actual (Actualizar/Eliminar/Buscar)."""
        
        # Determinar de qué página se llama y qué campo de ID usar
        current_page = self.stackedWidget.currentWidget().objectName()
        page_name = current_page.replace('page_', '')
        
        # Obtener el campo de ID específico de la página actual
        id_field = getattr(self, f"idempleado_{page_name}")
        id_text = id_field.text().strip()

        es_valido, id_empleado = self.validar_id_entero(id_text)
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_empleado)
            return

        try:
            self.empleadodao.empleado.id_empleado = id_empleado
            datos = self.empleadodao.buscarEmpleadoPorId() # Devuelve [(ID, Nombre, Cargo)]
            
            if datos:
                d = datos[0] 
                
                # Llenar los campos de la página actual (Nombre y Cargo)
                getattr(self, f"nombre_{page_name}").setText(d[1])
                getattr(self, f"cargo_{page_name}").setText(d[2])
                
                QMessageBox.information(self, "Éxito", f"Empleado ID {id_empleado} encontrado.")
                
                # Si la página es 'Buscar', también mostramos el resultado en la tabla_buscar (si existe)
                if page_name == 'buscar':
                    if hasattr(self, "tabla_buscar"):
                         self.tabla_buscar.setRowCount(1)
                         self.tabla_buscar.setItem(0, 0, QtWidgets.QTableWidgetItem(str(d[0]))) 
                         self.tabla_buscar.setItem(0, 1, QtWidgets.QTableWidgetItem(d[1]))       
                         self.tabla_buscar.setItem(0, 2, QtWidgets.QTableWidgetItem(d[2]))  
            else:
                QMessageBox.warning(self, "No Encontrado", f"No se encontró un empleado con ID {id_empleado}.")
                self.limpiar_formulario(page=page_name) # Limpiar si no se encuentra
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al buscar el empleado.\nDetalle: {e}")


    def actualizar_tabla(self):
        """Carga todos los empleados en la tabla de consulta."""
        try:
            datos = self.empleadodao.listarEmpleados()
            
            self.tabla_consulta.setRowCount(0)
            
            if datos:
                self.tabla_consulta.setRowCount(len(datos))
                
                for fila_idx, item in enumerate(datos):
                    self.tabla_consulta.setItem(fila_idx, 0, QtWidgets.QTableWidgetItem(str(item[0]))) # ID
                    self.tabla_consulta.setItem(fila_idx, 1, QtWidgets.QTableWidgetItem(item[1]))       # Nombre
                    self.tabla_consulta.setItem(fila_idx, 2, QtWidgets.QTableWidgetItem(item[2]))       # Cargo
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Tabla", f"Error al cargar la lista de empleados.\nDetalle: {e}")


    def cargar_datos_desde_tabla(self):
        """Carga los datos de la fila seleccionada a los formularios de Actualizar y Eliminar."""
        fila_seleccionada = self.tabla_consulta.currentRow()
        if fila_seleccionada < 0: return

        try:
            id_empleado = self.tabla_consulta.item(fila_seleccionada, 0).text()
            nombre = self.tabla_consulta.item(fila_seleccionada, 1).text()
            cargo = self.tabla_consulta.item(fila_seleccionada, 2).text()
            
            # Llenar Actualizar
            if hasattr(self, 'idempleado_actualizar'): self.idempleado_actualizar.setText(id_empleado)
            if hasattr(self, 'nombre_actualizar'): self.nombre_actualizar.setText(nombre)
            if hasattr(self, 'cargo_actualizar'): self.cargo_actualizar.setText(cargo)
            
            # Llenar Eliminar
            if hasattr(self, 'idempleado_eliminar'): self.idempleado_eliminar.setText(id_empleado)
            if hasattr(self, 'nombre_eliminar'): self.nombre_eliminar.setText(nombre)
            if hasattr(self, 'cargo_eliminar'): self.cargo_eliminar.setText(cargo)

            self.stackedWidget.setCurrentWidget(self.page_actualizar)
                
        except Exception as e:
             QMessageBox.critical(self, "Error de Carga", f"Error al cargar datos desde la tabla.\nDetalle: {e}")


    def limpiar_formulario(self, page=None):
        """Limpia los LineEdits en todas las páginas, o en una específica, usando mapeo."""

        # 1. Definición de todos los campos por página para la interfaz de Empleados
        page_fields = {
            'agregar': ['nombre_agregar', 'cargo_agregar'],
            'actualizar': ['idempleado_actualizar', 'nombre_actualizar', 'cargo_actualizar'],
            'eliminar': ['idempleado_eliminar', 'nombre_eliminar', 'cargo_eliminar'],
            # Aquí se añaden los campos de Nombre y Cargo que quieres borrar tras la búsqueda
            'buscar': ['idempleado_buscar', 'nombre_buscar', 'cargo_buscar'] 
        }
        
        # 2. Determinar la página clave
        try:
            page_key = page if page else self.stackedWidget.currentWidget().objectName().replace('page_', '')
        except AttributeError:
            # Esto maneja el caso donde stackedWidget o currentWidget no está inicializado, 
            # aunque no debería pasar si se llama desde un botón de la UI activa.
            page_key = 'desconocido'
        
        # 3. Obtener la lista de campos a limpiar
        fields_to_clear = page_fields.get(page_key, [])

        # 4. Iterar y limpiar los LineEdits
        for field_name in fields_to_clear:
            field = getattr(self, field_name, None)
            if field and hasattr(field, 'clear'): field.clear()
            
        # 5. Lógica adicional para 'buscar' (limpiar la tabla de resultados)
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