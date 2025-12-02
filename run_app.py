# main_inicio.py
from PyQt5 import QtWidgets
import sys
from load.load_ui_inicio import Load_ui_inicio 

def main():
    app = QtWidgets.QApplication(sys.argv)
    # Asegúrate de que Load_ui_inicio esté en la ruta 'load'
    window = Load_ui_inicio()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()