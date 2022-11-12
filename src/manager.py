from _manager import *
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
import sqlite3


class Manager(Ui_ExportManager, QMainWindow):
    def __init__(self, main_window, new_fractals=None):
        super().__init__()

        if new_fractals is not None:
            self.new_fractals = new_fractals

        self.main_window = main_window

    def closeEvent(self, event):
        self.main_window.manager = None

    def import_fractals(self):
        new_fractals = []
        for i in range(self.fractals_list.count()):
            if self.fractals_list.item(i).checkState() == Qt.Checked:
                name = self.fractals_list.item(i).text()
                for fractal in self.new_fractals:
                    if name == fractal["name"]:
                        new_fractals.append(fractal)
        if not new_fractals:
            return

        con = sqlite3.connect(self.main_window.database)
        cur = con.cursor()

        i = 0
        fracs = [x["name"] for x in self.main_window.CUSTOM_FRACTALS]
        ids = [x["id"] for x in self.main_window.CUSTOM_FRACTALS]
        for fractal in new_fractals:
            if self.main_window.CUSTOM_FRACTALS:
                if fractal["name"] in fracs:
                    cur.execute(f"""UPDATE CUSTOM_FRACTALS SET 
                                            'name' = '{fractal['name']}', 
                                            'axiom' = '{fractal['axiom']}', 
                                            'rules' = '{fractal['rules']}', 
                                            'angle' = '{fractal['angle']}', 
                                            'default_iterations_count' = '{fractal['iterations']}' WHERE id = 
                                                            '{ids[fracs.index(fractal['name'])]}'""")
                else:
                    cur.execute(f"""INSERT INTO CUSTOM_FRACTALS 
                        VALUES('{fractal['name']}', '{fractal['axiom']}', '{fractal['rules']}', '{fractal['angle']}', '{fractal['iterations']}', 
                        '{len(self.main_window.CUSTOM_FRACTALS) + 1 + i}')""")
            else:
                print(2)
                cur.execute(f"""INSERT INTO CUSTOM_FRACTALS 
                                            VALUES('{fractal['name']}', '{fractal['axiom']}', '{fractal['rules']}', '{fractal['angle']}', '{fractal['iterations']}', 
                                            '{len(self.main_window.CUSTOM_FRACTALS) + 1 + i}')""")
            i += 1
        con.commit()
        con.close()
        self.main_window.load_fractals()
        self.close()

    def export_fractals(self):
        export_file_text = ""
        for i in range(self.fractals_list.count()):
            if self.fractals_list.item(i).checkState() == Qt.Checked:
                name = self.fractals_list.item(i).text()
                for fractal in self.main_window.CUSTOM_FRACTALS:
                    if name == fractal["name"]:
                        rules = ""
                        for rule in fractal["rules"]:
                            rules += f"{rule}:{fractal['rules'][rule]};"

                        text = f"name::{fractal['name']}/\n" \
                               f"axiom::{fractal['axiom']}/\n" \
                               f"rules::{rules}/\n" \
                               f"angle::{fractal['angle']}/\n" \
                               f"default_iterations_count::{fractal['iterations']}/\n" \
                               f"---\n"
                        export_file_text += text

        export_file_text = export_file_text.strip()[:-3]
        if not export_file_text:
            return

        path = QFileDialog.getSaveFileName(self, "Export to", "", ".txt File (*txt);;All Files (*)")[0]
        if not path:
            return

        if not path.endswith(".txt"):
            path += ".txt"

        with open(path, "w") as f:
            f.write(export_file_text)
        self.close()