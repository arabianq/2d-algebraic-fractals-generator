# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'export_manager.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExportManager(object):
    def setupUi(self, ExportManager):
        ExportManager.setObjectName("ExportManager")
        ExportManager.resize(275, 286)
        self.centralwidget = QtWidgets.QWidget(ExportManager)
        self.centralwidget.setObjectName("centralwidget")
        self.fractals_list = QtWidgets.QListWidget(self.centralwidget)
        self.fractals_list.setGeometry(QtCore.QRect(10, 30, 256, 192))
        self.fractals_list.setObjectName("fractals_list")
        item = QtWidgets.QListWidgetItem()
        item.setCheckState(QtCore.Qt.Unchecked)
        self.fractals_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setCheckState(QtCore.Qt.Unchecked)
        self.fractals_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setCheckState(QtCore.Qt.Unchecked)
        self.fractals_list.addItem(item)
        self.chose_label = QtWidgets.QLabel(self.centralwidget)
        self.chose_label.setGeometry(QtCore.QRect(10, 10, 251, 20))
        self.chose_label.setAlignment(QtCore.Qt.AlignCenter)
        self.chose_label.setObjectName("chose_label")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 230, 241, 28))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancel_button = QtWidgets.QPushButton(self.widget)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout.addWidget(self.cancel_button)
        self.export_import_button = QtWidgets.QPushButton(self.widget)
        self.export_import_button.setObjectName("export_import_button")
        self.horizontalLayout.addWidget(self.export_import_button)
        ExportManager.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ExportManager)
        self.statusbar.setObjectName("statusbar")
        ExportManager.setStatusBar(self.statusbar)

        self.retranslateUi(ExportManager)
        QtCore.QMetaObject.connectSlotsByName(ExportManager)

    def retranslateUi(self, ExportManager):
        _translate = QtCore.QCoreApplication.translate
        ExportManager.setWindowTitle(_translate("ExportManager", "MainWindow"))
        __sortingEnabled = self.fractals_list.isSortingEnabled()
        self.fractals_list.setSortingEnabled(False)
        item = self.fractals_list.item(0)
        item.setText(_translate("ExportManager", "123"))
        item = self.fractals_list.item(1)
        item.setText(_translate("ExportManager", "432"))
        item = self.fractals_list.item(2)
        item.setText(_translate("ExportManager", "423234"))
        self.fractals_list.setSortingEnabled(__sortingEnabled)
        self.chose_label.setText(_translate("ExportManager", "Chose fractals you want to export/import"))
        self.cancel_button.setText(_translate("ExportManager", "Cancel"))
        self.export_import_button.setText(_translate("ExportManager", "Export/Import"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ExportManager = QtWidgets.QMainWindow()
    ui = Ui_ExportManager()
    ui.setupUi(ExportManager)
    ExportManager.show()
    sys.exit(app.exec_())