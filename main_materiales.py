from PyQt5 import QtWidgets
import sys
from load.load_ui_materiales import Load_ui_materiales 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Load_ui_materiales()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()