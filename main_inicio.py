# main_inicio.py (MODIFICADO)

from PyQt5 import QtWidgets
import sys
# Ahora importamos el controlador de Login
from load.load_ui_login import Load_ui_login 

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Inicia la ventana de Login
    window = Load_ui_login()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()