# load_ui_materiales.py
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic  
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox

from modelo.materialdao import MaterialDAO 
# Debes tener tu clase Material importada
from modelo.material import Material 

class Load_ui_materiales(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Carga la UI del archivo ui_materiales.ui
        uic.loadUi("ui/ui_materiales.ui", self) 
        self.show()
        self.materialdao = MaterialDAO()

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
            # Navegación
            self.boton_agregar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_agregar))
            self.boton_consultar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_consultar))
            self.boton_consultar.clicked.connect(self.actualizar_tabla)
            self.boton_buscar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_buscar))
            self.boton_actualizar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_actualizar))
            self.boton_eliminar.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_eliminar))
            self.actualizar_tabla() 
            
        # Acciones CRUD y Búsqueda (Conexión de la Lupa)
        # Se ha modificado para llamar a la función corregida
        if hasattr(self, "accion_guardar"): self.accion_guardar.clicked.connect(self.guardar_material)
        if hasattr(self, "accion_actualizar"): self.accion_actualizar.clicked.connect(self.actualizar_material)
        if hasattr(self, "accion_eliminar"): self.accion_eliminar.clicked.connect(self.eliminar_material)
        if hasattr(self, "accion_limpiar"): self.accion_limpiar.clicked.connect(self.limpiar_formulario)
        if hasattr(self, "refresh"): self.refresh.clicked.connect(self.actualizar_tabla)
        
        # Conexión de los botones de la lupa para buscar por ID_Gasto y Material (Clave Compuesta)
        if hasattr(self, "buscar_actualizar"): self.buscar_actualizar.clicked.connect(self.buscar_material)
        if hasattr(self, "buscar_eliminar"): self.buscar_eliminar.clicked.connect(self.buscar_material)
        if hasattr(self, "buscar_buscar"): self.buscar_buscar.clicked.connect(self.buscar_material)


    # ----------------------------------------------------------------------
    # --- FUNCIONES DE VALIDACIÓN ---
    # ----------------------------------------------------------------------
    
    def validar_id_entero(self, id_text, campo_nombre="ID de Gasto"):
        """Valida si un texto es un ID entero positivo."""
        try:
            id_entero = int(id_text)
            if id_entero <= 0:
                 return False, f"El {campo_nombre} debe ser un número entero positivo."
            return True, id_entero
        except ValueError:
            return False, f"El {campo_nombre} debe ser un número entero válido."

    def validar_datos_material(self, material, cantidad, importe):
        """Valida campos obligatorios y que Importe (Gasto) sea un número válido."""
        if not material or not cantidad or not importe:
            return False, "Material, Cantidad y Gasto (monto) son obligatorios."
        
        try:
            # Validación de cantidad como número entero positivo
            if int(cantidad) <= 0:
                return False, "La Cantidad debe ser un número entero positivo."
            
            # Validación de importe como número flotante positivo
            importe_float = float(importe)
            if importe_float <= 0:
                return False, "El Gasto (monto) debe ser un número positivo."
            return True, importe_float
        except ValueError:
            return False, "Cantidad y Gasto deben ser números válidos."

    # ----------------------------------------------------------------------
    # --- FUNCIONES CRUD (CLAVE COMPUESTA) ---
    # ----------------------------------------------------------------------

    def guardar_material(self):
        """
        Inserta/Actualiza un material, respetando el ID de Gasto dado o generando uno nuevo.
        """
        
        # 1. Obtención de los valores de la UI:
        # CORRECCIÓN: Usar el objectName real del LineEdit del ID Gasto.
        id_gasto_text = self.gasto_agregar_2.text().strip() # <--- ¡CORREGIDO!
        tipo = self.material_agregar.text().strip()        
        cantidad = self.cantidad_agregar.text().strip()    
        importe_total_text = self.gasto_agregar.text().strip() 
        
        # 2. Validaciones
        # Si se proporciona ID Gasto, validarlo
        id_gasto_valor = 0
        if id_gasto_text:
            es_valido_idgasto, id_gasto_valor = self.validar_id_entero(id_gasto_text, "ID de Gasto")
            if not es_valido_idgasto:
                QMessageBox.warning(self, "Error de Validación", id_gasto_valor)
                return
            
        es_valido, valor_o_mensaje = self.validar_datos_material(tipo, cantidad, importe_total_text)
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", valor_o_mensaje)
            return

        importe_total_float = valor_o_mensaje 
        
        try:
            # 3. Asignar valores al objeto MaterialDAO
            self.materialdao.material.id_material = 0 
            
            self.materialdao.material.id_gasto = id_gasto_valor 
            self.materialdao.material.tipo = tipo
            self.materialdao.material.cantidad = cantidad
            self.materialdao.material.importe_total = importe_total_float 
            
            # 4. Ejecutar el DAO: usa el nuevo método flexible
            id_gasto_final = self.materialdao.guardarMaterialFlexible()
            
            QMessageBox.information(self, "Éxito", f"Material '{tipo}' y Gasto guardado/actualizado.\nID Gasto final: {id_gasto_final}.")
            self.limpiar_formulario(page='agregar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo guardar el material.\nDetalle: {e}")


    def actualizar_material(self):
        """Actualiza la CANTIDAD de un material existente usando ID de Gasto y Material (Clave compuesta)."""
        # Clave: ID gasto (idgasto_actualizar), Material (material_actualizar)
        id_gasto_text = self.idgasto_actualizar.text().strip() 
        tipo = self.material_actualizar.text().strip()
        # Valor a actualizar: Cantidad
        cantidad_text = self.cantidad_actualizar.text().strip()

        # Validaciones de clave
        if not tipo or not id_gasto_text:
            QMessageBox.warning(self, "Error de Validación", "ID de Gasto y Material son obligatorios para actualizar.")
            return
        es_valido_idgasto, id_gasto = self.validar_id_entero(id_gasto_text, "ID de Gasto")
        if not es_valido_idgasto:
            QMessageBox.warning(self, "Error de Validación", id_gasto)
            return
            
        # Validación de cantidad
        es_valido_cant, cantidad_nueva = self.validar_id_entero(cantidad_text, "Cantidad")
        if not es_valido_cant:
            QMessageBox.warning(self, "Error de Validación", cantidad_nueva)
            return
        
        try:
            self.materialdao.material.id_gasto = id_gasto
            self.materialdao.material.tipo = tipo
            self.materialdao.material.cantidad = cantidad_nueva # Nueva cantidad
            
            self.materialdao.actualizarMaterial()
            
            QMessageBox.information(self, "Éxito", f"Cantidad del Material '{tipo}' para Gasto ID {id_gasto} actualizada.")
            self.limpiar_formulario(page='actualizar')
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar material.\nDetalle: {e}")


    def eliminar_material(self):
        """Elimina un material individual usando ID de Gasto y Material (Clave compuesta)."""
        # Clave: ID gasto (idgasto_eliminar), Material (material_eliminar)
        id_gasto_text = self.idgasto_eliminar.text().strip() 
        tipo = self.material_eliminar.text().strip()
        
        # Validaciones de clave
        if not tipo or not id_gasto_text:
            QMessageBox.warning(self, "Error de Validación", "ID de Gasto y Material son obligatorios para eliminar.")
            return
        es_valido, id_gasto = self.validar_id_entero(id_gasto_text, "ID de Gasto")
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_gasto)
            return

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Está seguro de eliminar el material '{tipo}' asociado al Gasto con ID {id_gasto}?",
                                            QMessageBox.Yes | QMessageBox.No)
        
        if confirmacion == QMessageBox.Yes:
            try:
                self.materialdao.material.id_gasto = id_gasto
                self.materialdao.material.tipo = tipo
                
                self.materialdao.eliminarMaterial()
                
                QMessageBox.information(self, "Éxito", f"Material '{tipo}' del Gasto ID {id_gasto} eliminado correctamente.")
                self.limpiar_formulario(page='eliminar')
                self.actualizar_tabla()

            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo eliminar el material.\nDetalle: {e}")


    def buscar_material(self):
        """Busca un material por ID de Gasto Y Material (Clave compuesta) y rellena los campos de la página actual."""
        
        current_page = self.stackedWidget.currentWidget().objectName()
        page_name = current_page.replace('page_', '')
        
        # 1. Obtener ID de Gasto (Campo 'ID gasto')
        id_gasto_field = getattr(self, f"idgasto_{page_name}") 
        id_gasto_text = id_gasto_field.text().strip()
        
        # 2. Obtener Material (Campo 'Material')
        material_field = getattr(self, f"material_{page_name}") 
        material_text = material_field.text().strip()

        # Validaciones de clave
        es_valido, id_gasto = self.validar_id_entero(id_gasto_text, "ID de Gasto")
        if not es_valido:
            QMessageBox.warning(self, "Error de Validación", id_gasto)
            return

        if not material_text:
            QMessageBox.warning(self, "Error de Validación", "El campo Material es obligatorio para la búsqueda.")
            return

        try:
            # Establecer ambos parámetros de búsqueda en el modelo
            self.materialdao.material.id_gasto = id_gasto
            self.materialdao.material.tipo = material_text
            
            # Usar el método que busca por ambos (devuelve: id_gasto, tipo, cantidad, importe_total)
            datos = self.materialdao.buscarMaterialPorIdGastoYMaterial() 
            
            if datos:
                d = datos[0] 
                importe_total = d[3]
                
                # Rellenar Cantidad
                if hasattr(self, f"cantidad_{page_name}"):
                    getattr(self, f"cantidad_{page_name}").setText(str(d[2]))
                
                # Rellenar Gasto (Importe Total)
                if hasattr(self, f"gasto_{page_name}"):
                    getattr(self, f"gasto_{page_name}").setText(str(importe_total)) 
                
                QMessageBox.information(self, "Éxito", f"Material '{material_text}' para Gasto ID {id_gasto} encontrado.")
                
            else:
                QMessageBox.warning(self, "No Encontrado", f"No se encontró material '{material_text}' para el Gasto con ID {id_gasto}.")
                # Limpiamos solo los campos de resultado
                if hasattr(self, f"cantidad_{page_name}"):
                    getattr(self, f"cantidad_{page_name}").clear()
                if hasattr(self, f"gasto_{page_name}"):
                     getattr(self, f"gasto_{page_name}").clear()
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al buscar el material.\nDetalle: {e}")


    def actualizar_tabla(self):
        """Carga todos los materiales en la tabla de consulta, incluyendo el importe total del Gasto."""
        try:
            # SP devuelve: (id_gasto, tipo, cantidad, importe_total)
            datos = self.materialdao.listarMateriales()
            
            if hasattr(self, 'tabla_consulta'):
                self.tabla_consulta.setRowCount(0)
                
                if datos:
                    self.tabla_consulta.setRowCount(len(datos))
                    
                    for fila_idx, item in enumerate(datos):
                        # Columna 0: id_gasto
                        self.tabla_consulta.setItem(fila_idx, 0, QtWidgets.QTableWidgetItem(str(item[0]))) 
                        # Columna 1: tipo (Material)
                        self.tabla_consulta.setItem(fila_idx, 1, QtWidgets.QTableWidgetItem(item[1]))       
                        # Columna 2: cantidad
                        self.tabla_consulta.setItem(fila_idx, 2, QtWidgets.QTableWidgetItem(str(item[2])))
                        # Columna 3: importe_total (Gasto)
                        self.tabla_consulta.setItem(fila_idx, 3, QtWidgets.QTableWidgetItem(str(item[3])))
                    
        except Exception as e:
            QMessageBox.critical(self, "Error de Tabla", f"Error al cargar la lista de materiales.\nDetalle: {e}")


    def cargar_datos_desde_tabla(self):
        """Carga los datos de la fila seleccionada a los formularios de Actualizar y Eliminar."""
        if not hasattr(self, 'tabla_consulta'): return
        
        fila_seleccionada = self.tabla_consulta.currentRow()
        if fila_seleccionada < 0: return

        try:
            # Columnas en la tabla: 0: ID gasto, 1: Material (tipo), 2: Cantidad, 3: Gasto (importe_total)
            id_gasto_key = self.tabla_consulta.item(fila_seleccionada, 0).text() 
            material_key = self.tabla_consulta.item(fila_seleccionada, 1).text() 
            cantidad = self.tabla_consulta.item(fila_seleccionada, 2).text() 
            
            # Llenar Actualizar (usa clave compuesta: ID gasto + Material)
            if hasattr(self, 'idgasto_actualizar'): self.idgasto_actualizar.setText(id_gasto_key)
            if hasattr(self, 'material_actualizar'): self.material_actualizar.setText(material_key) 
            if hasattr(self, 'cantidad_actualizar'): self.cantidad_actualizar.setText(cantidad)
            if hasattr(self, 'gasto_actualizar'): self.gasto_actualizar.clear() 
            
            # Llenar Eliminar (usa clave compuesta: ID gasto + Material)
            if hasattr(self, 'idgasto_eliminar'): self.idgasto_eliminar.setText(id_gasto_key)
            if hasattr(self, 'material_eliminar'): self.material_eliminar.setText(material_key) 
            if hasattr(self, 'cantidad_eliminar'): self.cantidad_eliminar.setText(cantidad)
            if hasattr(self, 'gasto_eliminar'): self.gasto_eliminar.clear() 

            self.stackedWidget.setCurrentWidget(self.page_actualizar)
                
        except Exception as e:
             QMessageBox.critical(self, "Error de Carga", f"Error al cargar datos desde la tabla.\nDetalle: {e}")


    def limpiar_formulario(self, page=None):
        """
        Limpia los campos de la página actual usando el patrón de mapeo por diccionario.
        """
        
        # El ID de Material (id_material) no se guarda en el controlador, solo se usa en el DAO si aplica.
        # No hay variables de estado similares a las de Proyecto que deban resetearse aquí.
        
        # 1. Mapeo de campos de la UI por página
        page_fields = {
            'agregar': [
                'gasto_agregar_2',   # ID Gasto
                'material_agregar',
                'cantidad_agregar',
                'gasto_agregar'      # Importe Total
            ],
            'actualizar': [
                'idgasto_actualizar',
                'material_actualizar',
                'cantidad_actualizar',
                'gasto_actualizar'
            ],
            'eliminar': [
                'idgasto_eliminar',
                'material_eliminar',
                'cantidad_eliminar',
                'gasto_eliminar'
            ],
            'buscar': [
                'idgasto_buscar',    # Clave de búsqueda
                'material_buscar',   # Clave de búsqueda
                'cantidad_buscar',   # Resultado de búsqueda
                'gasto_buscar'       # Resultado de búsqueda
            ] 
        }
        
        # 2. Determinar la página clave
        try:
            # Si 'page' es None, intenta obtener el nombre de la página actual del stackedWidget
            page_key = page if page else self.stackedWidget.currentWidget().objectName().replace('page_', '')
        except Exception:
            # En caso de error (ej. al inicio), no limpia nada o lo maneja por defecto.
            page_key = 'desconocido'
        
        # 3. Obtener la lista de campos a limpiar
        fields_to_clear = page_fields.get(page_key, [])

        # 4. Iterar y limpiar los LineEdits
        for field_name in fields_to_clear:
            field = getattr(self, field_name, None)
            if field and hasattr(field, 'clear'): field.clear()
            
        # 5. Lógica adicional para la página 'consultar' o 'buscar' (Limpiar tabla si existe)
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