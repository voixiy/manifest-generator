import sys
import os
import requests
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

download_link = "https://github.com/voixiy/manifests-steam/raw/refs/heads/main/"

class DownloadThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self, ID):
        super().__init__()
        self.ID = ID

    def run(self):
        try:
            url = f"{download_link}{self.ID}.zip"
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(os.getcwd(), f"Manifest\{self.ID}.zip")
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                self.log_signal.emit(f"Downloaded {self.ID}.zip successfully on path 'Manifest'.")
            else:
                self.log_signal.emit(f"Error: {self.ID}.zip not found.")
        except Exception as e:
            self.log_signal.emit(f"Error in download thread: {e}")

class Ui(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join('UI', 'main.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading UI file: {e}")
            sys.exit(1)

        font_id = QtGui.QFontDatabase.addApplicationFont('Font/Montserrat-Bold.ttf')
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QtGui.QFont(font_family, 18)
        self.label.setFont(font)
        
        self.Generate.clicked.connect(self.start_download_thread)
        self.show()

    def log(self, message: str):
        if hasattr(self, "Logs"):
            self.Logs.appendPlainText(message)
        else:
            print(f"Log: {message}")

    def start_download_thread(self):
        id_field = self.findChild(QPlainTextEdit, 'ID')
        if id_field:
            ID = id_field.toPlainText().strip()
            if ID:
                self.log(f"Finding {ID}.zip in our github repository...")
                self.download_thread = DownloadThread(ID)
                self.download_thread.log_signal.connect(self.log)
                self.download_thread.start()
            else:
                self.log("Error: ID field is empty.")
        else:
            self.log("Error: ID field not found in UI.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
