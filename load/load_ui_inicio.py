import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Importar los controladores de las ventanas CRUD
from load.load_ui_proyecto import Load_ui_proyecto
from load.load_ui_gasto import Load_ui_gastos
from load.load_ui_empleados import Load_ui_empleados
from load.load_ui_salarios import Load_ui_salarios
from load.load_ui_materiales import Load_ui_materiales
from load.load_ui_asignacion import Load_ui_asignacion

# Importar DAO para la información del Dashboard
from modelo.proyectodao import ProyectoDAO 

class Load_ui_inicio(QtWidgets.QMainWindow):
    # CORRECCIÓN 1: Agregar login_controller como argumento opcional
    def __init__(self, login_controller=None): 
        super().__init__()
        # Carga el diseño de la UI del menú principal
        uic.loadUi("ui/ui_inicio.ui", self) 
        self.setWindowTitle("Gestión de Clientes - Menú Principal")
        
        # CORRECCIÓN 2: Guardar la referencia al controlador de Login
        self.login_controller = login_controller
        
        # Diccionario para almacenar las referencias a las ventanas secundarias
        self.ventanas_crud = {}

        # Instancia del DAO para cargar el Dashboard
        self.proyectodao = ProyectoDAO()

        # --- Configuración Inicial y Conexiones ---
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        
        # Conexiones de la barra superior
        # CORRECCIÓN 3: Cambiar la conexión del boton_salir
        if hasattr(self, "boton_salir"): self.boton_salir.clicked.connect(self.cerrar_y_volver_a_login)
        if hasattr(self, "frame_superior"): self.frame_superior.mouseMoveEvent = self.mover_ventana
        if hasattr(self, "boton_menu"): self.boton_menu.clicked.connect(self.mover_menu)

        # Conexiones de los 6 botones de navegación lateral
        if hasattr(self, "boton_proyectos"): self.boton_proyectos.clicked.connect(lambda: self.abrir_ventana_crud('proyectos'))
        if hasattr(self, "boton_gastos"): self.boton_gastos.clicked.connect(lambda: self.abrir_ventana_crud('gastos'))
        if hasattr(self, "boton_empleados"): self.boton_empleados.clicked.connect(lambda: self.abrir_ventana_crud('empleados'))
        if hasattr(self, "boton_salarios"): self.boton_salarios.clicked.connect(lambda: self.abrir_ventana_crud('salarios'))
        if hasattr(self, "boton_materiales"): self.boton_materiales.clicked.connect(lambda: self.abrir_ventana_crud('materiales'))
        if hasattr(self, "boton_asignacion"): self.boton_asignacion.clicked.connect(lambda: self.abrir_ventana_crud('asignacion'))

        # Cargar datos iniciales del Dashboard y mostrar la ventana
        self.cargar_resumen_global()
        self.show()

    # CORRECCIÓN 4: Nuevo método para cerrar la ventana y mostrar el login
    def cerrar_y_volver_a_login(self):
        """Cierra la ventana actual (menú principal) y muestra la ventana de login."""
        self.close()
        # Verificar si existe la referencia y, si es así, mostrar la ventana de login
        if self.login_controller:
            self.login_controller.show()
            # Opcional: Limpiar campos sensibles o restaurar el foco
            if hasattr(self.login_controller, 'txt_contrasena'):
                self.login_controller.txt_contrasena.clear()
            if hasattr(self.login_controller, 'txt_usuario'):
                self.login_controller.txt_usuario.setFocus()
            
            
    # ----------------------------------------------------------------------
    # --- FUNCIONES DE NAVEGACIÓN Y DASHBOARD ---
    # ----------------------------------------------------------------------

    def abrir_ventana_crud(self, nombre_ventana):
        """
        Abre una ventana CRUD específica. Si ya está abierta, la trae al frente.
        """
        # Mapeo de nombres a clases controladoras (Debe coincidir con las importaciones)
        mapa_clases = {
            'proyectos': Load_ui_proyecto,
            'gastos': Load_ui_gastos,
            'empleados': Load_ui_empleados,
            'salarios': Load_ui_salarios,
            'materiales': Load_ui_materiales,
            'asignacion': Load_ui_asignacion,
        }
        
        ClaseVentana = mapa_clases.get(nombre_ventana)
        if not ClaseVentana:
            QMessageBox.critical(self, "Error", f"Controlador '{nombre_ventana}' no encontrado."); return

        # Si ya está abierta, la muestra y la trae al frente
        if nombre_ventana in self.ventanas_crud and self.ventanas_crud[nombre_ventana].isVisible():
            self.ventanas_crud[nombre_ventana].show(); self.ventanas_crud[nombre_ventana].activateWindow()
        else:
            # Crea una nueva instancia de la ventana CRUD
            try:
                # Nota: Las ventanas CRUD no necesitan la referencia del login
                nueva_ventana = ClaseVentana() 
                self.ventanas_crud[nombre_ventana] = nueva_ventana
                nueva_ventana.show()
            except Exception as e:
                QMessageBox.critical(self, "Error de Carga", f"No se pudo cargar la ventana de {nombre_ventana}.\nDetalle: {e}")
                
    def crear_grafico_dashboard(self, proyectos_activos, total_proyectos):
        """
        Crea un gráfico de barras simple para comparar Proyectos Activos vs Total.
        """
        # 1. Crear la figura de Matplotlib
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('None') 
        ax = fig.add_subplot(111)
        
        # 2. Datos para el gráfico
        labels = ['Activos', 'Completados']
        data = [proyectos_activos, total_proyectos - proyectos_activos]
        
        # 3. Dibujar el gráfico (Gráfico de barras)
        barras = ax.bar(labels, data, color=['#0078d7', '#444444']) 
        
        # 4. Estilizar para Dark Mode (coincidir con ui_inicio.ui)
        ax.set_title('Estado de Proyectos', color='#F0F0F0') 
        ax.set_xlabel('Tipo de Proyecto', color='#A0A0A0')
        ax.set_ylabel('Cantidad', color='#A0A0A0')
        
        ax.set_facecolor('#2D2D2D') 
        fig.set_facecolor('#2D2D2D') 

        # Color de los ticks (ejes)
        ax.tick_params(axis='x', colors='#F0F0F0') 
        ax.tick_params(axis='y', colors='#F0F0F0') 
        ax.spines['left'].set_color('#444444')
        ax.spines['bottom'].set_color('#444444')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        # Etiquetas de valor encima de las barras
        for bar in barras:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                    '%d' % int(height),
                    ha='center', va='bottom', color='#F0F0F0')

        # 5. Crear el lienzo de Matplotlib
        canvas = FigureCanvas(fig)
        
        # 6. Insertar el lienzo en el QFrame 'dashboard'
        dashboard_frame = self.dashboard 
        
        if dashboard_frame.layout() is None:
            layout = QtWidgets.QVBoxLayout(dashboard_frame)
            dashboard_frame.setLayout(layout)
        else:
            layout = dashboard_frame.layout()
        
        for i in reversed(range(layout.count())): 
            widgetToRemove = layout.itemAt(i).widget()
            layout.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)
        
        layout.addWidget(canvas)

    def cargar_resumen_global(self):
        """
        Llama al DAO para obtener los datos clave del proyecto y llena los QLineEdit,
        y luego llama a crear_grafico_dashboard.
        """
        try:
            # Llama al método que devuelve la tupla: 
            # (ProyectosActivos, TotalProyectos, CostosAcumulados, RentabilidadGlobal)
            resumen = self.proyectodao.obtenerResumenGlobal()
            
            if resumen and len(resumen) == 4:
                proyectos_activos, total_proyectos, costos, rentabilidad = resumen
                
                # Mapeo a los QLineEdit en ui_inicio.ui
                self.proyectosactivos.setText(str(proyectos_activos))
                self.totalproyectos.setText(str(total_proyectos))
                self.costosacumulados.setText(f"${costos:,.2f}")
                self.rentabilidad.setText(f"{rentabilidad:.2f}%")

                # Llamar a la función del gráfico
                self.crear_grafico_dashboard(proyectos_activos, total_proyectos)

        except Exception as e:
            QMessageBox.critical(self, "Error de Dashboard", f"Error al cargar el resumen: {e}. Verifique el SP 'sp_obtener_resumen_global'.")

    # ----------------------------------------------------------------------
    # --- FUNCIONES DE VENTANA (Mover/Menú) ---
    # ----------------------------------------------------------------------
    
    def mousePressEvent(self, event): self.clickPosition = event.globalPos()
    
    def mover_ventana(self, event):
        """Permite mover la ventana sin marco."""
        if not self.isMaximized() and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.clickPosition); 
            self.clickPosition = event.globalPos(); 
            event.accept()
            
    def mover_menu(self):
        """Maneja la animación de extensión y contracción del menú lateral."""
        width = self.frame_lateral.width(); 
        extender = 200 if width == 0 else 0
        self.boton_menu.setText("Menú" if width == 0 else "")
        
        # Animación para el frame lateral
        self.animacion = QPropertyAnimation(self.frame_lateral, b'minimumWidth'); 
        self.animacion.setDuration(300);
        self.animacion.setStartValue(width); 
        self.animacion.setEndValue(extender); 
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart); 
        self.animacion.start()
        
        # Animación para el botón (opcional, si el botón también se expande)
        self.animacionb = QPropertyAnimation(self.boton_menu, b'minimumWidth'); 
        self.animacionb.setStartValue(width); 
        self.animacionb.setEndValue(extender); 
        self.animacionb.setEasingCurve(QtCore.QEasingCurve.InOutQuart); 
        self.animacionb.start()