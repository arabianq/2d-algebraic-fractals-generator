if __name__ == "__main__":
    import sys
    from gui import *

    app = QtWidgets.QApplication(sys.argv)
    ui = Program()
    ui.show()
    sys.exit(app.exec_())
