# load_ui_gasto.py
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox

from modelo.gastodao import GastoDAO 
# Importa GastoDAO

class Load_ui_gastos(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ui_gastos.ui", self) 
        self.show()
        self.gastodao = GastoDAO()

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
            
        if hasattr(self, "accion_guardar"): self.accion_guardar.clicked.connect(self.guardar_gasto)
        if hasattr(self, "accion_actualizar"): self.accion_actualizar.clicked.connect(self.actualizar_gasto)
        if hasattr(self, "accion_eliminar"): self.accion_eliminar.clicked.connect(self.eliminar_gasto)
        if hasattr(self, "accion_limpiar"): self.accion_limpiar.clicked.connect(lambda: self.limpiar_formulario(page=None)) 
        if hasattr(self, "refresh"): self.refresh.clicked.connect(self.actualizar_tabla)
        
        if hasattr(self, "buscar_actualizar"): self.buscar_actualizar.clicked.connect(self.buscar_gasto_por_id_gasto)
        if hasattr(self, "buscar_eliminar"): self.buscar_eliminar.clicked.connect(self.buscar_gasto_por_id_gasto)
        if hasattr(self, "buscar_buscar"): self.buscar_buscar.clicked.connect(self.buscar_gasto_por_id_gasto)


    # ----------------------------------------------------------------------
    # --- FUNCIONES DE UTILIDAD (Validación) ---
    # ----------------------------------------------------------------------

    def validar_id_entero(self, id_text, field_name="ID"):
        """Valida si un texto es un ID entero no negativo."""
        try:
            val = int(id_text)
            if val < 0:
                 return False, f"El {field_name} no puede ser negativo."
            return True, val
        except ValueError:
            return False, f"El {field_name} debe ser un número entero válido."

    def validar_decimal(self, text):
        """Valida si un texto es un valor decimal positivo."""
        try:
            val = float(text)
            if val < 0: 
                 return False, "El Importe total no puede ser negativo."
            return True, val
        except ValueError:
            return False, "El Importe total debe ser un número decimal válido."


    # ----------------------------------------------------------------------
    # --- FUNCIONES CRUD (MODIFICACIÓN GUARDAR) ---
    # ----------------------------------------------------------------------

    def guardar_gasto(self):
        """Inserta o actualiza un gasto de forma flexible, asegurando la FK de Proyecto."""
        # 1. Obtención de datos
        id_gasto_text = self.idgasto_agregar.text().strip() 
        tipo = self.tipo_agregar.text().strip()
        fecha = self.fecha_agregar.text().strip()
        id_proyecto_text = self.idproyecto_agregar.text().strip()
        importe_total_text = self.importetotal_agregar.text().strip()

        # 2. Validación de campos obligatorios
        if not tipo or not fecha or not id_proyecto_text or not importe_total_text:
            QMessageBox.warning(self, "Error de Validación", "Tipo, Fecha, ID Proyecto e Importe total son obligatorios.")
            return

        # 3. Validación de ID Gasto (0 o existente)
        id_gasto = 0
        if id_gasto_text:
            es_valido_g, id_gasto_valor = self.validar_id_entero(id_gasto_text, "ID Gasto")
            if not es_valido_g:
                QMessageBox.warning(self, "Error de Validación", id_gasto_valor)
                return
            id_gasto = id_gasto_valor
        
        # 4. Validación de ID Proyecto
        es_valido_p, id_proyecto = self.validar_id_entero(id_proyecto_text, "ID Proyecto")
        if not es_valido_p or id_proyecto <= 0:
            QMessageBox.warning(self, "Error de Validación", id_proyecto if not es_valido_p else "El ID Proyecto debe ser positivo.")
            return

        # 5. Validación de Importe Total
        es_valido_i, importe_total = self.validar_decimal(importe_total_text)
        if not es_valido_i:
            QMessageBox.warning(self, "Error de Validación", importe_total)
            return

        try:
            # 🔑 PASO CLAVE: Asegurar que el proyecto exista ANTES de guardar el gasto
            self.gastodao.asegurarProyectoExistente(id_proyecto)
            
            # 6. Asignar y ejecutar el DAO
            self.gastodao.gasto.id_gasto = id_gasto         
            self.gastodao.gasto.tipo = tipo
            self.gastodao.gasto.fecha = fecha
            self.gastodao.gasto.id_proyecto = id_proyecto 
            self.gastodao.gasto.importe_total = importe_total
            
            id_gasto_final = self.gastodao.upsertGastoFlexible()
            
            QMessageBox.information(self, "Éxito", f"Gasto guardado/actualizado correctamente.\nID Gasto: {id_gasto_final}")
            self.limpiar_formulario(page='agregar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar el gasto.\nDetalle: {e}")


    def actualizar_gasto(self):
        """Actualiza un gasto existente (usa ID_GASTO)."""
        # (El resto del código CRUD estándar para actualizar, eliminar, buscar y tabla se mantiene igual)
        id_gasto_text = self.idgasto_actualizar.text().strip()
        id_proyecto_text = self.idproyecto_actualizar.text().strip()
        tipo = self.tipo_actualizar.text().strip()
        fecha = self.fecha_actualizar.text().strip()
        importe_total_text = self.importetotal_actualizar.text().strip()

        # Validación de campos
        if not id_gasto_text or not tipo or not fecha or not id_proyecto_text or not importe_total_text:
            QMessageBox.warning(self, "Error de Validación", "Todos los campos son obligatorios.")
            return

        es_valido_g, id_gasto = self.validar_id_entero(id_gasto_text, "ID Gasto")
        if not es_valido_g:
            QMessageBox.warning(self, "Error de Validación", id_gasto)
            return

        es_valido_p, id_proyecto = self.validar_id_entero(id_proyecto_text, "ID Proyecto")
        if not es_valido_p:
            QMessageBox.warning(self, "Error de Validación", id_proyecto)
            return

        es_valido_i, importe_total = self.validar_decimal(importe_total_text)
        if not es_valido_i:
            QMessageBox.warning(self, "Error de Validación", importe_total)
            return

        try:
            # Asegurar Proyecto Existente antes de actualizar
            self.gastodao.asegurarProyectoExistente(id_proyecto)

            self.gastodao.gasto.id_gasto = id_gasto
            self.gastodao.gasto.tipo = tipo
            self.gastodao.gasto.fecha = fecha
            self.gastodao.gasto.id_proyecto = id_proyecto
            self.gastodao.gasto.importe_total = importe_total
            
            self.gastodao.actualizarGasto()
            
            QMessageBox.information(self, "Éxito", f"Gasto ID {id_gasto} actualizado correctamente.")
            self.limpiar_formulario(page='actualizar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar gasto.\nDetalle: {e}")


    def eliminar_gasto(self):
        """Elimina un gasto por ID_GASTO."""
        id_gasto_text = self.idgasto_eliminar.text().strip() 
        
        es_valido, id_gasto = self.validar_id_entero(id_gasto_text, "ID Gasto")
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_gasto)
            return

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Está seguro de eliminar el Gasto con ID {id_gasto}?",
                                            QMessageBox.Yes | QMessageBox.No)
        
        if confirmacion == QMessageBox.Yes:
            try:
                self.gastodao.gasto.id_gasto = id_gasto
                self.gastodao.eliminarGasto()
                
                QMessageBox.information(self, "Éxito", f"Gasto ID {id_gasto} eliminado correctamente.")
                self.limpiar_formulario(page='eliminar')
                self.actualizar_tabla()

            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo eliminar el gasto.\nDetalle: {e}")


    def buscar_gasto_por_id_gasto(self):
        """Busca un único gasto por ID_GASTO para la página actual."""
        current_page = self.stackedWidget.currentWidget().objectName()
        page_name = current_page.replace('page_', '')
        
        id_field = getattr(self, f"idgasto_{page_name}")
        id_text = id_field.text().strip()

        es_valido, id_gasto = self.validar_id_entero(id_text, "ID Gasto")
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_gasto)
            return
        
        try:
            self.gastodao.gasto.id_gasto = id_gasto
            # Datos: (ID_Gasto=0, Tipo=1, Fecha=2, ID_Proyecto=3, Importe_Total=4)
            datos = self.gastodao.buscarGastoPorId() 
            
            if datos:
                d = datos[0] 
                
                getattr(self, f"idgasto_{page_name}").setText(str(d[0]))
                getattr(self, f"tipo_{page_name}").setText(d[1])
                getattr(self, f"fecha_{page_name}").setText(str(d[2])) 
                getattr(self, f"idproyecto_{page_name}").setText(str(d[3]))
                getattr(self, f"importetotal_{page_name}").setText(str(d[4]))

                QMessageBox.information(self, "Éxito", f"Gasto ID {id_gasto} encontrado.")
            else:
                QMessageBox.warning(self, "No Encontrado", f"No se encontró un Gasto con ID {id_gasto}.")
                self.limpiar_formulario(page=page_name, clear_id_gasto=False) 

        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al buscar el gasto.\nDetalle: {e}")


    def actualizar_tabla(self):
        """Carga todos los gastos en la tabla de consulta."""
        try:
            # Datos: (ID_Gasto=0, Tipo=1, Fecha=2, ID_Proyecto=3, Importe_Total=4)
            datos = self.gastodao.listarGastos() 
            
            self.tabla_consulta.setRowCount(0)
            
            if datos:
                self.tabla_consulta.setRowCount(len(datos))
                
                for fila_idx, item in enumerate(datos):
                    # Se asume que la tabla_consulta tiene 5 columnas:
                    # 0: ID gasto, 1: ID proyecto, 2: Tipo, 3: Fecha, 4: Importe total
                    self.tabla_consulta.setItem(fila_idx, 0, QtWidgets.QTableWidgetItem(str(item[0]))) 
                    self.tabla_consulta.setItem(fila_idx, 1, QtWidgets.QTableWidgetItem(str(item[3]))) 
                    self.tabla_consulta.setItem(fila_idx, 2, QtWidgets.QTableWidgetItem(item[1]))      
                    self.tabla_consulta.setItem(fila_idx, 3, QtWidgets.QTableWidgetItem(str(item[2]))) 
                    self.tabla_consulta.setItem(fila_idx, 4, QtWidgets.QTableWidgetItem(str(item[4]))) 
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Tabla", f"Error al cargar la lista de gastos.\nDetalle: {e}")


    def cargar_datos_desde_tabla(self):
        """Carga los datos de la fila seleccionada a los formularios de Actualizar y Eliminar."""
        fila_seleccionada = self.tabla_consulta.currentRow()
        if fila_seleccionada < 0: return

        try:
            # Índice de columna de la tabla (UI): 
            # 0: ID gasto, 1: ID proyecto, 2: Tipo, 3: Fecha, 4: Importe total
            id_gasto = self.tabla_consulta.item(fila_seleccionada, 0).text()
            id_proyecto = self.tabla_consulta.item(fila_seleccionada, 1).text()
            tipo = self.tabla_consulta.item(fila_seleccionada, 2).text()
            fecha = self.tabla_consulta.item(fila_seleccionada, 3).text()
            importe_total = self.tabla_consulta.item(fila_seleccionada, 4).text()
            
            # Llenar Actualizar
            if hasattr(self, 'idgasto_actualizar'): self.idgasto_actualizar.setText(id_gasto)
            if hasattr(self, 'idproyecto_actualizar'): self.idproyecto_actualizar.setText(id_proyecto)
            if hasattr(self, 'tipo_actualizar'): self.tipo_actualizar.setText(tipo)
            if hasattr(self, 'fecha_actualizar'): self.fecha_actualizar.setText(fecha)
            if hasattr(self, 'importetotal_actualizar'): self.importetotal_actualizar.setText(importe_total)
            
            # Llenar Eliminar
            if hasattr(self, 'idgasto_eliminar'): self.idgasto_eliminar.setText(id_gasto)
            if hasattr(self, 'idproyecto_eliminar'): self.idproyecto_eliminar.setText(id_proyecto)
            if hasattr(self, 'tipo_eliminar'): self.tipo_eliminar.setText(tipo)
            if hasattr(self, 'fecha_eliminar'): self.fecha_eliminar.setText(fecha)
            if hasattr(self, 'importetotal_eliminar'): self.importetotal_eliminar.setText(importe_total)

            self.stackedWidget.setCurrentWidget(self.page_actualizar)
                
        except Exception as e:
             QMessageBox.critical(self, "Error de Carga", f"Error al cargar datos desde la tabla.\nDetalle: {e}")


    def limpiar_formulario(self, page=None, clear_id_gasto=True):
        """Limpia los LineEdits en todas las páginas, o en una específica."""
        pages = ['agregar', 'actualizar', 'eliminar', 'buscar']
        
        if page is not None:
            pages = [page]
            
        for p in pages:
            if hasattr(self, f'idgasto_{p}') and (clear_id_gasto or p == 'agregar'): 
                getattr(self, f'idgasto_{p}').clear()
            if hasattr(self, f'idproyecto_{p}'): getattr(self, f'idproyecto_{p}').clear()
            if hasattr(self, f'tipo_{p}'): getattr(self, f'tipo_{p}').clear()
            if hasattr(self, f'fecha_{p}'): getattr(self, f'fecha_{p}').clear()
            if hasattr(self, f'importetotal_{p}'): getattr(self, f'importetotal_{p}').clear()

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