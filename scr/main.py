from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidget, QStatusBar, QAction, QTreeWidgetItem, QShortcut, QPushButton
from PyQt5.QtGui import QKeySequence
from PyQt5.Qt import QIcon, QSize, Qt

from scr.variables import *

import webbrowser
import qdarktheme
import subprocess
import traceback
import threading
import requests
import typing
import ctypes
import sys


def exceptionHandler(func) -> typing.Callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            with open("scr/files/logs/log.txt", "a+", encoding="utf-8", buffering=1) as file:
                file.write(traceback.format_exc())

            if not DIVELOP:
                if SYSTEM == "Windows":
                    subprocess.run(["notepad.exe", "scr/files/logs/log.txt"])

                elif SYSTEM == "Linux":
                    subprocess.run(["gedit", "scr/files/logs/log.txt"])

                else:
                    print("LOG: scr/files/logs/log.txt")

            sys.exit()

    return wrapper


class FocusTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)

        self.project = parent

    def mousePressEvent(self, event):
        self.setFocus()

        event.accept()


class Main(QMainWindow):
    def __init__(self, app) -> None:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)

        except AttributeError:
            pass

        for name in dir(self):
            try:
                attr = getattr(self, name)

                if callable(attr) and not name.startswith("__"):
                    setattr(self, name, exceptionHandler(attr))

            except RuntimeError:
                pass

        QMainWindow.__init__(self)

        self.app = app

        qdarktheme.setup_theme(theme=SETTINGS["theme"])

        self.application = {}
        self.engine = None

        self.dialog = None

        self.menubar = None

        self.selectProject = ""
        self.selectFile = ""

        self.compiling = False

        self.desktop = QApplication.desktop()

        size["width"] = self.desktop.width()
        size["height"] = self.desktop.height() - PLUS

        self.variables = {}
        self.cash = {}

        self.objects = {}
        self.menues = {}

        self.setGeometry(0, 0, int(size["width"] * 0.6), int(size["height"] * 0.6))
        self.move((size["width"] - self.width()) // 2, (size["height"] - self.height()) // 2)

        self.shortcut()

        self.initialization()

        self.init()

    def geometryInit(self) -> None:
        pass

    def initialization(self) -> None:
        self.setWindowTitle("GELauncher")

        self.objects["menu_rama"] = QTreeWidget(self)
        self.objects["menu_rama"].header().hide()
        self.objects["menu_rama"].setGeometry(-50, -50, 150 + 1, size["height"] + 100)
        self.objects["menu_rama"].show()

        self.objects["menu_versions"] = QPushButton(self)
        self.objects["menu_versions"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_versions"].setGeometry(0, 0, 100, 100)
        self.objects["menu_versions"].show()

        self.objects["menu_projects"] = QPushButton(self)
        self.objects["menu_projects"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_projects"].setGeometry(0, 100 - 1, 100, 100)
        self.objects["menu_projects"].show()

        self.objects["menu_about"] = QPushButton(self)
        self.objects["menu_about"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_about"].setGeometry(0, 200 - 2, 100, 100)
        self.objects["menu_about"].show()

        self.objects["menu_settings"] = QPushButton(self)
        self.objects["menu_settings"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_settings"].setGeometry(0, 300 - 3, 100, 100)
        self.objects["menu_settings"].setIcon(QIcon("scr/files/sprites/menu/settings.png"))
        self.objects["menu_settings"].setIconSize(QSize(80, 80))
        self.objects["menu_settings"].show()

        self.show()

    def init(self, type: str = "") -> None:
        self.menu()

        self.geometryInit()

    def menu(self) -> None:
        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.clear()

    def shortcut(self) -> None:
        pass

    def closeEvent(self, event) -> None:
        event.accept()

    def resizeEvent(self, event) -> None:
        size["width"] = self.width()
        size["height"] = self.height()

        self.desktop = QApplication.desktop()

        self.geometryInit()

        event.accept()
