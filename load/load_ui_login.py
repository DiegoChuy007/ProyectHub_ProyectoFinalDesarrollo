# load/load_ui_login.py

import sys
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

# Importar el controlador del menú principal para lanzar la aplicación
from load.load_ui_inicio import Load_ui_inicio 
from modelo.usuariodao import UsuarioDAO

class Load_ui_login(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Carga el diseño de la UI del login
        uic.loadUi("ui/ui_login.ui", self) 
        self.setWindowTitle("Acceso al Sistema - Gestión de Clientes")
        self.show()
        
        # Instanciar el DAO
        self.usuario_dao = UsuarioDAO()
        
        # Referencia para la ventana principal
        self.main_window = None

        # --- Conexiones de la UI (Basado en ui_login.ui) ---
        
        # Conectar el botón de ingresar
        if hasattr(self, "btn_ingresar"):
            self.btn_ingresar.clicked.connect(self.autenticar_usuario)
        
        # Habilitar la entrada con la tecla Enter
        if hasattr(self, "txt_contrasena"):
            self.txt_contrasena.returnPressed.connect(self.autenticar_usuario)


    def autenticar_usuario(self):
        """
        Verifica las credenciales del usuario y lanza el menú principal si son correctas.
        """
        # Asegúrate de que los widgets existen antes de usarlos
        if not hasattr(self, 'txt_usuario') or not hasattr(self, 'txt_contrasena'):
            QMessageBox.critical(self, "Error de UI", "Faltan campos de usuario/contraseña en la interfaz.")
            return

        usuario = self.txt_usuario.text().strip()
        contrasena = self.txt_contrasena.text().strip()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error de Acceso", "Debe ingresar el usuario y la contraseña.")
            return

        try:
            # Llama al método del DAO para verificar las credenciales
            if self.usuario_dao.verificarCredenciales(usuario, contrasena):
                QMessageBox.information(self, "Acceso Exitoso", f"Bienvenido, {usuario}.", QMessageBox.Ok)
                
                # Cargar y mostrar la ventana principal (Load_ui_inicio)
                self.lanzar_menu_principal()
                
            else:
                QMessageBox.critical(self, "Error de Acceso", "Usuario o contraseña incorrectos.")
                self.txt_contrasena.clear() # Limpia solo la contraseña tras fallo
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error durante la autenticación.\nDetalle: {e}")

    def lanzar_menu_principal(self):
        """
        Cierra (oculta) la ventana de login y abre el menú principal, 
        pasando la referencia de login.
        """
        try:
            # CORRECCIÓN 1: Pasar la referencia 'self' al constructor de Load_ui_inicio
            # Esto permite a la ventana principal llamar a self.show() cuando se cierre.
            self.main_window = Load_ui_inicio(login_controller=self) 
            self.main_window.show()
            
            # CORRECCIÓN 2: Oculta la ventana de login en lugar de cerrarla
            self.hide() 
        except Exception as e:
            QMessageBox.critical(self, "Error de Aplicación", f"No se pudo cargar el menú principal.\nDetalle: {e}")