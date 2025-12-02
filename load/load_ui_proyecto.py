import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox

# Importar los DAOs necesarios
from modelo.proyectodao import ProyectoDAO 
from modelo.ubicaciondao import UbicacionDAO 

class Load_ui_proyecto(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/ui_proyectos.ui", self) 
        self.show()
        self.proyectodao = ProyectoDAO()
        self.ubicaciondao = UbicacionDAO() # Inicializar DAO de ubicación
        
        self.id_proyecto_seleccionado = 0 
        self.id_ubicacion_actual = 0 

        # --- Conexiones de la UI ---
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        if hasattr(self, "tabla_consulta"):
            self.tabla_consulta.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tabla_consulta.clicked.connect(self.cargar_datos_desde_tabla)

        if hasattr(self, "boton_salir"): self.boton_salir.clicked.connect(lambda: self.close())
        if hasattr(self, "frame_superior"): self.frame_superior.mouseMoveEvent = self.mover_ventana
        if hasattr(self, "boton_menu"): self.boton_menu.clicked.connect(self.mover_menu)

        if hasattr(self, "stackedWidget"):
            self.boton_agregar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_agregar))
            self.boton_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
            self.boton_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
            self.boton_buscar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_buscar))
            self.boton_consultar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_consultar))
            self.boton_consultar.clicked.connect(self.actualizar_tabla)
            self.actualizar_tabla() 
            
        if hasattr(self, "accion_guardar"): self.accion_guardar.clicked.connect(self.guardar_proyecto)
        if hasattr(self, "accion_actualizar"): self.accion_actualizar.clicked.connect(self.actualizar_proyecto)
        if hasattr(self, "accion_eliminar"): self.accion_eliminar.clicked.connect(self.eliminar_proyecto)
        if hasattr(self, "refresh"): self.refresh.clicked.connect(self.actualizar_tabla)
        
        if hasattr(self, "buscar_actualizar"): self.buscar_actualizar.clicked.connect(self.buscar_proyecto)
        if hasattr(self, "buscar_eliminar"): self.buscar_eliminar.clicked.connect(self.buscar_proyecto)
        if hasattr(self, "buscar_buscar"): self.buscar_buscar.clicked.connect(self.buscar_proyecto)
        
        if hasattr(self, "accion_limpiar"): self.accion_limpiar.clicked.connect(self.limpiar_formulario)

    
    def validar_id_entero(self, id_text):
        try:
            val = int(id_text)
            if val <= 0: return False, "El ID debe ser un número entero positivo."
            return True, val
        except ValueError:
            return False, "El ID debe ser un número entero válido."
            
    def limpiar_formulario(self, page=None):
        self.id_proyecto_seleccionado = 0
        self.id_ubicacion_actual = 0 
        
        page_fields = {
            'agregar': ['idproy_agregar', 'inicio_agregar', 'fin_agregar', 'estatus_agregar', 'precio_agregar', 'rent_agregar', 'ubi_agregar'],
            'actualizar': ['idproy_actualizar', 'inicio_actualizar', 'fin_actualizar', 'estatus_actualizar', 'venta_actualizar', 'renta_actualizar', 'ubi_actualizar'],
            'eliminar': ['idproy_eliminar', 'inicio_eliminar', 'fin_eliminar', 'estatus_eliminar', 'venta_eliminar', 'rent_eliminar', 'ubi_eliminar'],
            'buscar': ['idproy_buscar', 'inicio_buscar', 'fin_buscar', 'estatus_buscar', 'venta_buscar', 'rent_buscar', 'ubi_buscar'] 
        }
        
        page_key = page if page else self.stackedWidget.currentWidget().objectName().replace('page_', '')
        
        fields_to_clear = page_fields.get(page_key, [])

        for field_name in fields_to_clear:
            field = getattr(self, field_name, None)
            if field and hasattr(field, 'clear'): field.clear()

    def combinar_ubicacion(self, datos):
        """Combina los campos de ubicación (índices 7 a 10) en una sola cadena para visualización."""
        # Mapeo de SP de búsqueda: d[7]:ciudad, d[8]:calle, d[9]:colonia, d[10]:numero
        if len(datos) > 10 and datos[7] is not None:
            # Formato: Ciudad, Colonia, Calle #Número
            return f"{datos[7].strip()}, {datos[9].strip()}, {datos[8].strip()} #{datos[10].strip()}"
        return "Ubicación no disponible"

    # ----------------------------------------------------------------------
    # --- FUNCIONES CRUD ---
    # ----------------------------------------------------------------------

    def guardar_proyecto(self):
        # 1. CAPTURA DE CAMPOS
        id_proy_text = self.idproy_agregar.text().strip()
        fecha_inicio = self.inicio_agregar.text().strip()
        fecha_fin    = self.fin_agregar.text().strip()
        estatus      = self.estatus_agregar.text().strip()
        precio       = self.precio_agregar.text().strip()
        rentabilidad = self.rent_agregar.text().strip()
        
        # CAPTURA DE UBICACIÓN (CADENA ÚNICA)
        ubicacion_completa = self.ubi_agregar.text().strip() 
        
        # 2. PROCESAMIENTO y VALIDACIÓN DE UBICACIÓN
        try:
            partes_ubicacion = [p.strip() for p in ubicacion_completa.split(',')]
            
            # Debe tener exactamente 4 partes: Ciudad, Calle, Colonia, Número
            if len(partes_ubicacion) != 4:
                QMessageBox.warning(self, "Error de Formato", 
                    "El campo Ubicación debe contener 4 valores separados por coma, en el orden: Ciudad, Calle, Colonia, Número."); return
                    
            ciudad, calle, colonia, numero = partes_ubicacion
            
        except Exception:
            QMessageBox.warning(self, "Error de Formato", "Formato de ubicación inválido."); return
        
        # 3. VALIDACIÓN DE ID DE PROYECTO y CAMPOS DE PROYECTO
        valido_id, id_proyecto = self.validar_id_entero(id_proy_text)
        
        if not valido_id: 
            QMessageBox.warning(self, "Error de Validación", "El ID de Proyecto debe ser un número entero válido."); return
            
        if not all([fecha_inicio, fecha_fin, estatus, precio, rentabilidad, ciudad, calle, colonia, numero]):
            QMessageBox.warning(self, "Error de Validación", "Todos los campos (incluyendo las partes de la ubicación) deben estar llenos."); return

        try:
            # --- LÓGICA DE UPSERT: Obtener ID_UBICACION ---
            # Llama a la función del DAO con las 4 partes desglosadas
            id_ubicacion_generado = self.ubicaciondao.verificarOInsertar(ciudad, calle, colonia, numero)
            
            if id_ubicacion_generado == 0:
                 raise Exception("Fallo al generar ID de Ubicación.")

            # 4. ASIGNACIÓN DE VALORES al OBJETO DAO (Proyecto)
            self.proyectodao.proyecto.id_proyecto = id_proyecto # <--- ID MANUAL
            self.proyectodao.proyecto.fecha_inicio = fecha_inicio
            self.proyectodao.proyecto.fecha_aprox_finalizacion = fecha_fin
            self.proyectodao.proyecto.estatus_obra = estatus
            self.proyectodao.proyecto.precio_venta = precio
            self.proyectodao.proyecto.rentabilidad = rentabilidad
            self.proyectodao.proyecto.id_ubicacion = id_ubicacion_generado # <-- Usamos el ID generado

            # 5. EJECUCIÓN DEL DAO
            self.proyectodao.guardarProyecto()
            QMessageBox.information(self, "Éxito", "Proyecto guardado correctamente.")
            self.limpiar_formulario(page='agregar')
            self.actualizar_tabla()
            
        except Exception as ex:
            print("ERROR SQL DETALLADO:", ex)
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar el proyecto. Detalle: {ex}")

    def buscar_proyecto(self):
        """Busca proyecto por ID de Proyecto y llena los formularios."""
        current_page = self.stackedWidget.currentWidget().objectName()
        page_name = current_page.replace('page_', '')
        
        id_field = getattr(self, f"idproy_{page_name}")
        valido, id_proyecto = self.validar_id_entero(id_field.text().strip())
        
        if not valido: 
            QMessageBox.warning(self, "Error de ID", id_proyecto); return

        try:
            self.proyectodao.proyecto.id_proyecto = id_proyecto
            datos = self.proyectodao.buscarProyectoPorIdProyecto() 
            
            if datos:
                d = datos 
                # Mapeo: 0:id_proy... 6:id_ubicacion, 7:ciudad, 8:calle, 9:colonia, 10:numero
                
                self.id_proyecto_seleccionado = d[0]
                self.id_ubicacion_actual = d[6]
                ubicacion_combinada = self.combinar_ubicacion(d)
                
                # 3. Llenar los campos de la página actual
                getattr(self, f"inicio_{page_name}").setText(d[1])
                getattr(self, f"fin_{page_name}").setText(d[2])
                getattr(self, f"estatus_{page_name}").setText(d[3])
                
                # Precio_venta (d[4]) usa 'venta_' para actualizar/eliminar/buscar
                getattr(self, f"venta_{page_name}").setText(d[4]) 
                
                # Rentabilidad (d[5]) usa 'rent_' para agregar/eliminar/buscar y 'renta_' para actualizar
                rentabilidad_field = f"rent_{page_name}" if page_name in ['agregar', 'eliminar', 'buscar'] else f"renta_{page_name}"
                getattr(self, rentabilidad_field).setText(d[5])

                # El campo de ubicación en la UI muestra la combinación de campos
                getattr(self, f"ubi_{page_name}").setText(ubicacion_combinada)

                QMessageBox.information(self, "Éxito", f"Proyecto ID {id_proyecto} encontrado.")
            else:
                QMessageBox.warning(self, "No Encontrado", f"Proyecto con ID '{id_proyecto}' no encontrado.")
                self.limpiar_formulario(page=page_name)
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al buscar proyecto.\nDetalle: {e}")

    def actualizar_proyecto(self):
        if self.id_proyecto_seleccionado == 0:
             QMessageBox.warning(self, "Aviso", "Primero debe buscar el proyecto a actualizar."); return
             
        fecha_inicio = self.inicio_actualizar.text().strip()
        fecha_fin = self.fin_actualizar.text().strip()
        estatus = self.estatus_actualizar.text().strip()
        precio = self.venta_actualizar.text().strip() 
        rentabilidad = self.renta_actualizar.text().strip()
        
        id_proy_text = self.idproy_actualizar.text().strip()
        valido_id, id_proyecto = self.validar_id_entero(id_proy_text)
        
        if not valido_id: 
            QMessageBox.warning(self, "Error", "El ID de Proyecto es inválido."); return
            
        if id_proyecto != self.id_proyecto_seleccionado:
            QMessageBox.critical(self, "Error", "El ID del proyecto en el formulario no coincide con el ID buscado."); return

        ubicacion_text = self.ubi_actualizar.text().strip() # Cadena de ubicación
        
        # VALIDACIÓN Y PROCESAMIENTO DE UBICACIÓN (requerido para actualizar si se modifica)
        try:
            partes_ubicacion = [p.strip() for p in ubicacion_text.split(',')]
            if len(partes_ubicacion) != 4:
                QMessageBox.warning(self, "Error de Formato", "El formato de Ubicación es incorrecto (Ciudad, Calle, Colonia, Número)."); return
            ciudad, calle, colonia, numero = partes_ubicacion
        except Exception:
             QMessageBox.warning(self, "Error de Formato", "Formato de ubicación inválido."); return

        if not all([fecha_inicio, fecha_fin, estatus, precio, rentabilidad]):
            QMessageBox.warning(self, "Error de Validación", "Todos los campos principales deben estar llenos."); return

        try:
            # Si el usuario modificó la dirección, verificamos/insertamos la nueva y obtenemos el nuevo ID_UBICACION
            id_ubicacion_actualizada = self.ubicaciondao.verificarOInsertar(ciudad, calle, colonia, numero)

            self.proyectodao.proyecto.id_proyecto = self.id_proyecto_seleccionado
            self.proyectodao.proyecto.fecha_inicio = fecha_inicio
            self.proyectodao.proyecto.fecha_aprox_finalizacion = fecha_fin
            self.proyectodao.proyecto.estatus_obra = estatus
            self.proyectodao.proyecto.precio_venta = precio
            self.proyectodao.proyecto.rentabilidad = rentabilidad
            self.proyectodao.proyecto.id_ubicacion = id_ubicacion_actualizada 
            
            self.proyectodao.actualizarProyecto()
            QMessageBox.information(self, "Éxito", "Proyecto actualizado correctamente.")
            self.limpiar_formulario(page='actualizar')
            self.actualizar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar proyecto.\nDetalle: {e}")

    def eliminar_proyecto(self):
        if self.id_proyecto_seleccionado == 0:
             QMessageBox.warning(self, "Aviso", "Primero debe buscar el proyecto a eliminar."); return

        respuesta = QMessageBox.question(self, 'Confirmación', 
            f"¿Está seguro de eliminar el Proyecto ID: {self.id_proyecto_seleccionado}?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            try:
                self.proyectodao.proyecto.id_proyecto = self.id_proyecto_seleccionado
                self.proyectodao.eliminarProyecto()
                QMessageBox.information(self, "Éxito", "Proyecto eliminado correctamente.")
                self.limpiar_formulario(page='eliminar')
                self.actualizar_tabla()
            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"Error al eliminar proyecto.\nDetalle: {e}")


    def actualizar_tabla(self):
        try:
            datos = self.proyectodao.listarProyectos()
            self.tabla_consulta.setRowCount(len(datos))
            
            # SP de Listar devuelve 11 campos: 0:id_proyecto... 10:numero
            
            for fila_idx, item in enumerate(datos):
                
                # --- VERIFICACIÓN Y COMBINACIÓN DE UBICACIÓN (Índices 7, 8, 9, 10) ---
                
                # Check 1: Ensure we received the expected number of columns (11)
                if len(item) < 11:
                    ubicacion_combinada = f"ERROR: Faltan columnas del SP ({len(item)})"
                
                # Check 2: Process data safely
                else:
                    # Use a helper function or expression to safely get the value or an empty string
                    def get_safe_str(index):
                        val = item[index]
                        return val.strip() if val is not None else ""

                    ciudad  = get_safe_str(7)
                    calle   = get_safe_str(8)
                    colonia = get_safe_str(9)
                    numero  = get_safe_str(10)
                    
                    if not ciudad and not calle and not colonia:
                        # Si todos los campos están vacíos/nulos, la ubicación no está definida
                        ubicacion_combinada = "Ubicación No Definida"
                    else:
                        # Formato: Ciudad, Colonia, Calle #Número
                        ubicacion_combinada = f"{ciudad}, {colonia}, {calle} #{numero}"
                
                
                # Mapeo a las 7 columnas de la tabla de la UI (Índices 0 a 6)
                self.tabla_consulta.setItem(fila_idx, 0, QtWidgets.QTableWidgetItem(str(item[0]))) 
                self.tabla_consulta.setItem(fila_idx, 1, QtWidgets.QTableWidgetItem(item[1]))      
                self.tabla_consulta.setItem(fila_idx, 2, QtWidgets.QTableWidgetItem(item[2]))      
                self.tabla_consulta.setItem(fila_idx, 3, QtWidgets.QTableWidgetItem(item[3]))      
                self.tabla_consulta.setItem(fila_idx, 4, QtWidgets.QTableWidgetItem(item[4]))      
                self.tabla_consulta.setItem(fila_idx, 5, QtWidgets.QTableWidgetItem(item[5]))      
                self.tabla_consulta.setItem(fila_idx, 6, QtWidgets.QTableWidgetItem(ubicacion_combinada)) # Índice 6
            
        except IndexError as ie:
             QMessageBox.critical(self, "Error de Mapeo de Columna", 
                                  f"El SP no devuelve los 11 campos esperados o hay un índice de columna incorrecto. Detalle: {ie}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Tabla", f"Error al cargar la lista de proyectos.\nDetalle: {e}")

    def cargar_datos_desde_tabla(self):
        fila_seleccionada = self.tabla_consulta.currentRow()
        if fila_seleccionada < 0: return

        try:
            id_proy_text = self.tabla_consulta.item(fila_seleccionada, 0).text()
            valido, id_proyecto = self.validar_id_entero(id_proy_text)
            
            if valido:
                self.proyectodao.proyecto.id_proyecto = id_proyecto
                datos = self.proyectodao.buscarProyectoPorIdProyecto()
                
                if datos:
                    d = datos 
                    ubicacion_combinada = self.combinar_ubicacion(d)
                    
                    self.id_proyecto_seleccionado = d[0]
                    self.id_ubicacion_actual = d[6]
                    
                    # Llenar Actualizar
                    self.idproy_actualizar.setText(str(d[0])); self.inicio_actualizar.setText(d[1]); self.fin_actualizar.setText(d[2])
                    self.estatus_actualizar.setText(d[3]); self.venta_actualizar.setText(d[4]); self.renta_actualizar.setText(d[5])
                    self.ubi_actualizar.setText(ubicacion_combinada)
                    
                    # Llenar Eliminar
                    self.idproy_eliminar.setText(str(d[0])); self.inicio_eliminar.setText(d[1]); self.fin_eliminar.setText(d[2])
                    self.estatus_eliminar.setText(d[3]); self.venta_eliminar.setText(d[4]); self.rent_eliminar.setText(d[5])
                    self.ubi_eliminar.setText(ubicacion_combinada)

                    self.stackedWidget.setCurrentWidget(self.page_actualizar)
                
        except Exception as e:
             QMessageBox.critical(self, "Error de Carga", f"Error al cargar datos desde la tabla.\nDetalle: {e}")


    # --- Funciones de Ventana (Mover/Menú) ---
    def mousePressEvent(self, event): self.clickPosition = event.globalPos()
    def mover_ventana(self, event):
        if not self.isMaximized() and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()

    def mover_menu(self):
        width = self.frame_lateral.width()
        extender = 200 if width == 0 else 0
        self.boton_menu.setText("Menú" if width == 0 else "")
            
        self.animacion = QPropertyAnimation(self.frame_lateral, b'minimumWidth')
        self.animacion.setDuration(300); self.animacion.setStartValue(width); self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart); self.animacion.start()
        
        self.animacionb = QPropertyAnimation(self.boton_menu, b'minimumWidth')
        self.animacionb.setStartValue(width); self.animacionb.setEndValue(extender)
        self.animacionb.setEasingCurve(QtCore.QEasingCurve.InOutQuart); self.animacionb.start()