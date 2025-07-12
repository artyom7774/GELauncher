from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidget, QLabel, QStatusBar, QAction, QTreeWidgetItem, QShortcut, QPushButton, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QKeySequence
from PyQt5.Qt import QIcon, QSize, Qt

from scr.variables import *

from urllib.parse import urlparse

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


def versionDownload(url, folder, chunk_size=8192):
    if not os.path.exists(folder):
        os.mkdir(folder)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f"{folder}/engine.zip", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def versionIsCurrect(version, minVersion):
    if version[0] > minVersion[0]:
        return True

    if version[0] < minVersion[0]:
        return False

    if version[1] > minVersion[1]:
        return True

    if version[1] < minVersion[1]:
        return False

    if version[2] > minVersion[2]:
        return True

    if version[2] < minVersion[2]:
        return False

    return True


class FocusTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)

        self.project = parent

    def mousePressEvent(self, event):
        self.setFocus()

        event.accept()


class VersionItem(QTreeWidget):
    def __init__(self, name, log="", version=None, parent=None):
        super().__init__(parent)

        self.project = parent
        self.version = version

        self.name = name
        self.log = log

        self.header().hide()

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)

        self.name = QLabel(f"Game Engine {name}")
        self.name.setFont(BIG_HELP_FONT)
        layout.addWidget(self.name)

        self.changelog = QLabel(log)
        self.changelog.setWordWrap(True)

        layout.addWidget(self.changelog)

        verSplit = list(map(int, version.split(".")))
        verMinSplit = list(map(int, MIN_VERSION_FOR_DOWNLOAD.split(".")))

        if versionIsCurrect(verSplit, verMinSplit):
            self.download = QPushButton(translate("Download"))
            self.download.setFixedHeight(24)
            self.download.setStyleSheet(BUTTON_BLUE_STYLE)
            self.download.clicked.connect(lambda: self.onDownloadClick())

            layout.addWidget(self.download)

        self.view = QPushButton(translate("View"))
        self.view.setFixedHeight(24)
        self.view.setStyleSheet(BUTTON_BLUE_STYLE)
        self.view.clicked.connect(lambda: self.onViewClick())

        layout.addWidget(self.view)

        self.setLayout(layout)

    def onViewClick(self):
        webbrowser.open(f"https://github.com/artyom7774/Game-Engine-3/releases/tag/GE{self.version}")

    def onDownloadClick(self):
        thr = threading.Thread(target=lambda: versionDownload(
            f"https://github.com/artyom7774/Game-Engine-3/releases/tag/GE{self.version}/Game-Engine-3-windows.zip",
            f"versions/Game Engine {self.version}/"
        ))
        thr.daemon = True
        thr.start()


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

        self.dialog = None

        self.menubar = None

        self.desktop = QApplication.desktop()

        size["width"] = self.desktop.width()
        size["height"] = self.desktop.height() - PLUS

        self.selectMenu = "versions"

        self.variables = {}
        self.objects = {}

        self.setFixedSize(int(size["width"] * 0.6), int(size["height"] * 0.6))
        self.move((size["width"] - self.width()) // 2, (size["height"] - self.height()) // 2)

        self.shortcut()

        self.initialization()

        self.init()

    def initialization(self) -> None:
        self.setWindowTitle("GELauncher")
        self.setWindowIcon(QIcon("scr/files/sprites/logo.png"))

        self.objects["main"] = {}

        self.objects["menu_rama"] = QTreeWidget(self)
        self.objects["menu_rama"].header().hide()
        self.objects["menu_rama"].setGeometry(-50, -50, 150 + 1, size["height"] + 100)
        self.objects["menu_rama"].show()

        self.objects["menu_versions"] = QPushButton(self)
        self.objects["menu_versions"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_versions"].setGeometry(0, 0, 100, 100)
        self.objects["menu_versions"].setIcon(QIcon("scr/files/sprites/menu/versions.png"))
        self.objects["menu_versions"].setIconSize(QSize(80, 80))
        self.objects["menu_versions"].show()

        def menuVersionsSolve():
            self.selectMenu = "versions"

            self.init()

        self.objects["menu_versions"].clicked.connect(lambda: menuVersionsSolve())

        self.objects["menu_projects"] = QPushButton(self)
        self.objects["menu_projects"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_projects"].setGeometry(0, 100 - 1, 100, 100)
        self.objects["menu_projects"].setIcon(QIcon("scr/files/sprites/menu/projects.png"))
        self.objects["menu_projects"].setIconSize(QSize(80, 80))
        self.objects["menu_projects"].show()

        def menuProjectsSolve():
            self.selectMenu = "projects"

            self.init()

        self.objects["menu_projects"].clicked.connect(lambda: menuProjectsSolve())

        self.objects["menu_about"] = QPushButton(self)
        self.objects["menu_about"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_about"].setGeometry(0, 200 - 2, 100, 100)
        self.objects["menu_about"].setIcon(QIcon("scr/files/sprites/menu/about.png"))
        self.objects["menu_about"].setIconSize(QSize(80, 80))
        self.objects["menu_about"].show()

        def menuAboutSolve():
            self.selectMenu = "about"

            self.init()

        self.objects["menu_about"].clicked.connect(lambda: menuAboutSolve())

        self.objects["menu_settings"] = QPushButton(self)
        self.objects["menu_settings"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_settings"].setGeometry(0, 300 - 3, 100, 100)
        self.objects["menu_settings"].setIcon(QIcon("scr/files/sprites/menu/settings.png"))
        self.objects["menu_settings"].setIconSize(QSize(80, 80))
        self.objects["menu_settings"].show()

        def menuSettingsSolve():
            self.selectMenu = "settings"

            self.init()

        self.objects["menu_settings"].clicked.connect(lambda: menuSettingsSolve())

        self.show()

    def init(self) -> None:
        for name, value in self.objects["main"].items():
            try:
                value.hide()
                value.deleteLater()

            except RuntimeError:
                pass

        menues = {
            "versions": lambda: self.versionsMenu(),
            "projects": lambda: self.projectsMenu(),
            "about": lambda: self.aboutMenu(),
            "settings": lambda: self.settingsMenu()
        }

        menues[self.selectMenu]()

        self.menu()

    def versionsMenu(self):
        print(1)

        self.objects["main"]["scroll_area"] = QScrollArea(self)
        self.objects["main"]["scroll_area"].setGeometry(107, 10, self.width() - 130, self.height() - 42)
        self.objects["main"]["scroll_area"].setWidgetResizable(True)
        self.objects["main"]["scroll_area"].setStyleSheet("QScrollArea { border: 1px solid #3f4042; };")

        scrollWidget = QWidget()
        scrollLayout = QVBoxLayout(scrollWidget)
        scrollLayout.setSpacing(5)

        url = "https://raw.githubusercontent.com/artyom7774/Game-Engine-3/main/scr/files/updates.json"

        response = requests.get(url)
        data = response.json()

        versions = []

        for version in data["sorted"]:
            versions.append(version)

        items = []

        versions = versions[::-1]

        for version in versions:
            name = data["updates"][version]["name"]
            log = data["updates"][version]["text"]

            version_item = VersionItem(name, log, version, self)

            scrollLayout.addWidget(version_item)

            items.append(version_item)

        scrollLayout.addStretch()

        self.objects["main"]["scroll_area"].setWidget(scrollWidget)
        self.objects["main"]["scroll_area"].show()

    def projectsMenu(self):
        print(2)

    def aboutMenu(self):
        print(3)

    def settingsMenu(self):
        print(4)

    def menu(self) -> None:
        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.clear()

    def shortcut(self) -> None:
        pass

    def closeEvent(self, event) -> None:
        event.accept()