from _gui import *
from PyQt5.QtWidgets import QMainWindow, QColorDialog, QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, \
    QLineEdit, QListWidgetItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt
import fractal_generator
import sqlite3
import manager
import sys


class Program(Ui_MainWindow, QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("2D Algebraic Fractals Generator (L-System)")
        self.setFixedSize(1030, 695)
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.image = None
        self.pixmap = None
        self.last_mouse_position = None
        self.manager = None
        self.DEFAULT_FRACTALS = []
        self.CUSTOM_FRACTALS = []
        self.offset = [0, 0]
        self.rules = {}
        self.correction_angle = 0
        self.iterations = 0
        self.angle = 0
        self.zoom = 1.0
        self.image_width = 600
        self.image_height = 600
        self.axiom = ""
        self.database = "fractals_db.sqlite"
        self.fractal_color = Qt.white
        self.background_color = Qt.black
        self.grabbed = False
        self.is_default_fractal_chosen = False

        self.zoom_label.setText("x" + str(self.zoom))

        self.load_fractals()

        self.x_offset_slider.valueChanged.connect(self.x_offset_slider_moved)
        self.y_offset_slider.valueChanged.connect(self.y_offset_slider_moved)
        self.x_offset_spinbox.valueChanged.connect(self.x_offset_spinbox_changed)
        self.y_offset_spinbox.valueChanged.connect(self.y_offset_spinbox_changed)

        self.change_fractal_color_button.clicked.connect(self.change_fractal_color)
        self.change_background_color_button.clicked.connect(self.change_background_color)

        self.iterations_spinbox.valueChanged.connect(self.iterations_changed)
        self.axiom_lineedit.textChanged.connect(self.axiom_changed)
        self.correction_angle_spinbox.valueChanged.connect(self.correction_angle_changed)
        self.angle_spinbox.valueChanged.connect(self.angle_changed)
        self.rules_plaintextedit.textChanged.connect(self.rules_changed)

        self.fractal_type_chooser.currentTextChanged.connect(self.set_fractal_type)

        self.save_as_image_button.clicked.connect(self.save_as_image)
        self.save_custom_fractal_button.clicked.connect(self.save_custom_fractal)
        self.remove_custom_fractal_button.clicked.connect(self.remove_custom_fractal)
        self.export_custom_fractals_button.clicked.connect(self.export_custom_fractals)
        self.import_custom_fractals_button.clicked.connect(self.import_custom_fractals)

    def import_custom_fractals(self):
        if self.manager is None:
            self.manager = manager.Manager(self, [])
            self.manager.setupUi(self.manager)
            self.manager.setFixedSize(275, 286)
            self.manager.setWindowIcon(QtGui.QIcon('icon.png'))
            
            self.manager.chose_label.setText("Chose fractals you want to import")
            self.manager.export_import_button.setText("Import")
            self.manager.fractals_list.clear()

            path = QFileDialog.getOpenFileName(self, "Import", "", ".txt File (*txt);;All Files (*)")[0]
            if not path:
                return

            with open(path, "r") as f:
                text = f.read()
                text = text.replace("\n", "")
                text = text.split("---")
                text = list(map(lambda x: x.split("/")[:-1], text))

            if not text:
                return

            for fractal in text:
                if len(fractal) != 5:
                    continue
                name = fractal[0].split("::")[-1]
                axiom = fractal[1].split("::")[-1]
                rules = fractal[2].split("::")[-1]
                angle = fractal[3].split("::")[-1]

                try:
                    angle = float(angle)
                except ValueError:
                    continue

                iterations = fractal[4].split(":")[-1]

                try:
                    iterations = int(iterations)
                except ValueError:
                    continue

                if name and axiom and rules and angle and iterations:
                    item = QListWidgetItem(name)
                    item.setCheckState(Qt.Checked)
                    self.manager.fractals_list.addItem(item)
                    self.manager.new_fractals.append(
                        {
                            "name": name,
                            "axiom": axiom,
                            "rules": rules,
                            "angle": angle,
                            "iterations": iterations
                        }
                    )

        self.manager.export_import_button.clicked.connect(self.manager.import_fractals)
        self.manager.cancel_button.clicked.connect(lambda: self.manager.close())
        self.manager.show()

    def export_custom_fractals(self):
        if self.manager is None:
            self.manager = manager.Manager(self)
            self.manager.setupUi(self.manager)
            self.manager.setFixedSize(275, 286)
            self.manager.setWindowIcon(QtGui.QIcon('icon.png'))

            self.manager.chose_label.setText("Chose fractals you want to export")
            self.manager.export_import_button.setText("Export")

            self.manager.fractals_list.clear()
            for fractal in self.CUSTOM_FRACTALS:
                item = QListWidgetItem(fractal["name"])
                item.setCheckState(Qt.Checked)
                self.manager.fractals_list.addItem(item)

            self.manager.export_import_button.clicked.connect(self.manager.export_fractals)
            self.manager.cancel_button.clicked.connect(lambda: self.manager.close())
            self.manager.show()

    def save_custom_fractal(self):
        name_ = ""
        if not self.is_default_fractal_chosen:
            name_ = self.fractal_type_chooser.currentText()

        dialog = SaveFractalDialog(name_)

        if not dialog.exec():
            return
        name = dialog.name
        if not name:
            return

        con = sqlite3.connect(self.database)
        cur = con.cursor()

        rules = ""
        for rule in self.rules:
            rules += f"{rule}:{self.rules[rule]};"

        if name != name_:
            cur.execute(f"""INSERT INTO CUSTOM_FRACTALS 
                        VALUES('{name}', '{self.axiom}', '{rules}', '{self.angle}', '{self.iterations}', 
                        '{len(self.CUSTOM_FRACTALS) + 1}')""")
        else:
            cur.execute(f"""UPDATE CUSTOM_FRACTALS SET 
                        'name' = '{name}', 
                        'axiom' = '{self.axiom}', 
                        'rules' = '{rules}', 
                        'angle' = '{self.angle}', 
                        'default_iterations_count' = '{self.iterations}' WHERE id = 
                                        '{self.fractal_type_chooser.currentIndex() + 1 - len(self.DEFAULT_FRACTALS)}'
                    """)

        con.commit()
        con.close()

        self.load_fractals()
        self.fractal_type_chooser.setCurrentIndex(len(self.DEFAULT_FRACTALS) + len(self.CUSTOM_FRACTALS) - 1)

    def remove_custom_fractal(self):
        fractal_name, fractal_id = self.fractal_type_chooser.currentText(), self.fractal_type_chooser.currentIndex() + 1
        fractal_id -= len(self.DEFAULT_FRACTALS)

        fractal = None
        for frac in self.CUSTOM_FRACTALS:
            if frac["name"] == fractal_name and frac["id"] == fractal_id:
                fractal = frac
                self.remove_custom_fractal_button.setEnabled(True)
                break

        if fractal is None:
            return

        con = sqlite3.connect(self.database)
        cur = con.cursor()

        cur.execute(f"""DELETE FROM CUSTOM_FRACTALS WHERE id={fractal_id}""")
        con.commit()

        self.load_fractals()

        for fractal in self.CUSTOM_FRACTALS:
            id_ = fractal["id"]
            cur.execute(f"""UPDATE CUSTOM_FRACTALS SET id={id_ - fractal_id} WHERE id > {fractal_id}""")

        con.commit()
        con.close()
        self.load_fractals()

    def save_as_image(self):
        path = QFileDialog.getSaveFileName(self, "Save File", "", "PNG Image (*png);;All Files (*)")[0]
        if not path:
            return
        if not path.endswith(".png"):
            path += ".png"
        self.image.save(path)

    def load_fractals(self):
        self.fractal_type_chooser.clear()
        self.DEFAULT_FRACTALS = []
        self.CUSTOM_FRACTALS = []

        con = sqlite3.connect(self.database)
        cur = con.cursor()
        default_fractals = cur.execute("""SELECT * FROM DEFAULT_FRACTALS""").fetchall()
        custom_fractals = cur.execute("""SELECT * FROM CUSTOM_FRACTALS""").fetchall()
        con.close()

        for frac in default_fractals:
            name = frac[0]
            axiom = frac[1]
            rules = {}
            for string in frac[2].split(";")[:-1]:
                rule = string.split(":")
                rules[rule[0]] = rule[1]
            angle = frac[3]
            iterations = frac[4]
            id_ = frac[5]
            fractal = {
                "name": str(name),
                "axiom": axiom,
                "rules": rules,
                "angle": angle,
                "iterations": iterations,
                "id": id_
            }
            self.DEFAULT_FRACTALS.append(fractal)
            self.fractal_type_chooser.addItem(fractal["name"])

        for frac in custom_fractals:
            name = frac[0]
            axiom = frac[1]
            rules = {}
            for string in frac[2].split(";")[:-1]:
                rule = string.split(":")
                rules[rule[0]] = rule[1]
            angle = frac[3]
            iterations = frac[4]
            id_ = frac[5]
            fractal = {
                "name": str(name),
                "axiom": axiom,
                "rules": rules,
                "angle": angle,
                "iterations": iterations,
                "id": id_
            }
            self.CUSTOM_FRACTALS.append(fractal)
            self.fractal_type_chooser.addItem(fractal["name"])
        self.set_fractal_type()

    def set_fractal_type(self):
        fractal_name, fractal_id = self.fractal_type_chooser.currentText(), self.fractal_type_chooser.currentIndex() + 1

        if not fractal_name or not fractal_id:
            return

        fractal = None
        for frac in self.DEFAULT_FRACTALS:
            if frac["name"] == fractal_name and frac["id"] == fractal_id:
                fractal = frac
                self.remove_custom_fractal_button.setEnabled(False)
                self.is_default_fractal_chosen = True
                break

        if fractal is None:
            fractal_id -= len(self.DEFAULT_FRACTALS)
            for frac in self.CUSTOM_FRACTALS:
                if frac["name"] == fractal_name and frac["id"] == fractal_id:
                    fractal = frac
                    self.remove_custom_fractal_button.setEnabled(True)
                    self.is_default_fractal_chosen = False
                    break

        self.iterations = fractal["iterations"]
        self.iterations_spinbox.setValue(self.iterations)

        self.axiom = fractal["axiom"]
        self.axiom_lineedit.setText(self.axiom)

        self.rules = fractal["rules"]
        text = ""
        for rule in self.rules:
            text += f"{rule} -> {self.rules[rule]}\n"
        self.rules_plaintextedit.setPlainText(text)

        self.angle = fractal["angle"]
        self.angle_spinbox.setValue(self.angle)
        self.generate()

    def x_offset_slider_moved(self):
        x_offset = self.x_offset_slider.value()
        self.x_offset_spinbox.setValue(x_offset)
        self.offset = [x_offset, self.offset[1]]
        self.generate()

    def y_offset_slider_moved(self):
        y_offset = self.y_offset_slider.value()
        self.y_offset_spinbox.setValue(y_offset)
        self.offset = [self.offset[0], y_offset]
        self.generate()

    def x_offset_spinbox_changed(self):
        x_offset = self.x_offset_spinbox.value()
        self.x_offset_slider.setValue(x_offset)
        self.offset = [x_offset, self.offset[1]]
        self.generate()

    def y_offset_spinbox_changed(self):
        y_offset = self.y_offset_spinbox.value()
        self.y_offset_slider.setValue(y_offset)
        self.offset = [self.offset[0], y_offset]
        self.generate()

    def change_fractal_color(self):
        color = QColorDialog.getColor()
        color_rgb = color.getRgb()
        self.fractal_color_label.setStyleSheet(f"background-color: rgb{color_rgb};")
        self.fractal_color = color
        self.generate()

    def change_background_color(self):
        color = QColorDialog.getColor()
        color_rgb = color.getRgb()
        self.background_color_label.setStyleSheet(f"background-color: rgb{color_rgb};")
        self.background_color = color
        self.generate()

    def iterations_changed(self):
        if self.iterations_spinbox.value() != self.iterations:
            self.iterations = self.iterations_spinbox.value()
            self.generate()

    def axiom_changed(self):
        if self.axiom != self.axiom_lineedit.text():
            self.axiom = self.axiom_lineedit.text()
            if self.axiom:
                self.generate()

    def correction_angle_changed(self):
        self.correction_angle = self.correction_angle_spinbox.value()
        self.generate()

    def angle_changed(self):
        if self.angle != self.angle_spinbox.value():
            self.angle = self.angle_spinbox.value()
            self.generate()

    def rules_changed(self):
        rules_raw = self.rules_plaintextedit.toPlainText()
        rules_raw = rules_raw.replace("\n", ";")
        rules_raw = rules_raw.replace("->", ":")
        rules_raw = rules_raw.replace(" ", "")
        rules_ = rules_raw.split(";")
        rules_ = [rule.split(":") for rule in rules_ if len(rule.split(":")) == 2 and "" not in rule.split(":")]
        rules = {}
        for rule in rules_:
            rules[rule[0]] = rule[1]
        if self.rules != rules:
            self.rules = rules
            self.generate()

    def generate(self):
        if not self.axiom or not self.rules:
            return

        fractal = fractal_generator.Fractal(
            iterations=self.iterations,
            axiom=self.axiom,
            rules=self.rules,
            angle=self.angle,
            offset=self.offset,
            correction_angle=self.correction_angle,
            zoom=self.zoom
        )

        points = fractal.points
        if not points:
            return
        width = fractal.width
        height = fractal.height
        offset = fractal.offset

        if width < self.image_width:
            offset[0] += (self.image_width - width) / 2
            width = self.image_width
        if height < self.image_height:
            offset[1] += (self.image_height - height) / 2
            height = self.image_height

        self.image = QImage(width, height, QImage.Format_RGB32)
        self.image.fill(self.background_color)
        painter = QPainter(self.image)
        painter.setPen(QPen(self.fractal_color))
        prev_point = ()
        for point in points:
            if prev_point and point[2]:
                x0 = round(prev_point[0] + offset[0])
                y0 = round(prev_point[1] + offset[1])
                x1 = round(point[0] + offset[0])
                y1 = round(point[1] + offset[1])
                painter.drawLine(x0, y0, x1, y1)
            prev_point = point
        painter.end()
        self.pixmap = QPixmap(self.image)
        self.fractal_image_label.setPixmap(self.pixmap)

    def wheelEvent(self, event):
        if self.fractal_image_label.underMouse():
            y_normalized = event.angleDelta().y()
            y_normalized /= abs(y_normalized)
            if not (y_normalized < 0 and self.zoom <= 0.5):
                self.zoom += 0.25 * y_normalized
                self.zoom_label.setText("x" + str(self.zoom))
                self.generate()

    def mousePressEvent(self, event):
        if self.fractal_image_label.underMouse() and not self.grabbed:
            self.grabbed = True

    def mouseReleaseEvent(self, event):
        if self.grabbed:
            self.grabbed = False
            self.last_mouse_position = None

    def mouseMoveEvent(self, event):
        if self.grabbed:
            mouse_position = (event.x(), event.y())
            if not self.last_mouse_position:
                self.last_mouse_position = mouse_position
                return
            relative = (
                mouse_position[0] - self.last_mouse_position[0],
                mouse_position[1] - self.last_mouse_position[1]
            )
            if relative:
                self.offset[0] += relative[0] / self.zoom
                self.offset[1] += relative[1] / self.zoom

                if self.offset[0] < -self.image_width:
                    self.offset[0] = self.image_width
                elif self.offset[0] > self.image_width:
                    self.offset[0] = -self.image_width

                if self.offset[1] < -self.image_height:
                    self.offset[1] = self.image_height
                elif self.offset[1] > self.image_height:
                    self.offset[1] = -self.image_height

                self.x_offset_slider.setValue(round(self.offset[0]))
                self.x_offset_spinbox.setValue(round(self.offset[0]))
                self.y_offset_slider.setValue(round(self.offset[1]))
                self.y_offset_spinbox.setValue(round(self.offset[1]))

                self.last_mouse_position = mouse_position

                self.generate()

    def closeEvent(self, event):
        if self.manager is not None:
            self.manager.close()


class SaveFractalDialog(QDialog):
    def __init__(self, name):
        super().__init__()
        self.setWindowTitle("Save Custom Fractal")

        button = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        message = QLabel("Write the name of the new fractal")
        self.layout.addWidget(message)

        self.name = name
        self.name_textedit = QLineEdit()
        self.name_textedit.setText(name)
        self.layout.addWidget(self.name_textedit)
        self.name_textedit.textChanged.connect(self.name_changed)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def name_changed(self):
        self.name = self.name_textedit.text()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Program()
    ui.show()
    sys.exit(app.exec_())
