from PyQt5 import QtWidgets
import sys
# Asume que load_ui_salarios.py está en la ruta correcta
from load.load_ui_salarios import Load_ui_salarios 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Load_ui_salarios()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()