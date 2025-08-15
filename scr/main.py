from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidget, QLabel, QComboBox, QStatusBar, QAction, QTreeWidgetItem, QShortcut, QPushButton, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QKeySequence
from PyQt5.Qt import QIcon, QSize, Qt, QThread

from scr.variables import *

import webbrowser
import qdarktheme
import subprocess
import traceback
import threading
import requests
import shutil
import typing
import ctypes
import time
import sys

VERSIONS_WAS_LOADED = False
MIN_VERSION_FOR_DOWNLOAD = "3.11.0"


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


class ProjectItem(QTreeWidget):
    def __init__(self, path, parent=None):
        super().__init__(parent)

        self.project = parent
        self.path = path

        with open(f"{path}/version.json", "r", encoding="utf-8") as file:
            version = json.load(file)["version"]

        self.display = path.replace("projects/", "")

        self.version = version

        self.setFixedWidth(parent.width() - 160)

        self.header().hide()

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)

        self.name = QLabel(f"{self.display}")
        self.name.setFont(BIG_HELP_FONT)
        layout.addWidget(self.name)

        self.changelog = QLabel(translate("Version") + f": {self.version}")
        self.changelog.setWordWrap(True)

        layout.addWidget(self.changelog)

        verSplit = list(map(int, version.split(".")))
        verMinSplit = list(map(int, MIN_VERSION_FOR_DOWNLOAD.split(".")))

        self.delete = QPushButton(translate("Delete"))
        self.delete.setFixedHeight(24)
        self.delete.setStyleSheet(BUTTON_RED_STYLE)
        self.delete.clicked.connect(lambda: self.onDeleteClick())

        layout.addWidget(self.delete)

        self.setLayout(layout)

    def onDeleteClick(self):
        shutil.rmtree(self.path)

        self.project.init()


class VersionDownloadThread(QThread):
    def __init__(self, url, folder, version, parent=None):
        super().__init__(parent)

        self.url = url
        self.folder = folder

        self.version = version

    def run(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        with requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            with open(f"{self.folder}/installer.exe", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        os.system(f"cd \"versions/Game Engine {self.version}\" && installer.exe /s")
        os.remove(f"versions/Game Engine {self.version}/installer.exe")


class VersionItem(QTreeWidget):
    def __init__(self, name, log="", version=None, wasInstalled=False, parent=None):
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

        self.wasInstalled = wasInstalled

        self.changelog = QLabel(log)
        self.changelog.setWordWrap(True)

        layout.addWidget(self.changelog)

        verSplit = list(map(int, version.split(".")))
        verMinSplit = list(map(int, MIN_VERSION_FOR_DOWNLOAD.split(".")))

        if versionIsCurrect(verSplit, verMinSplit):
            self.download = QPushButton(translate("Download") if not wasInstalled else translate("Run"))
            self.download.setFixedHeight(24)
            self.download.setStyleSheet(BUTTON_BLUE_STYLE)
            self.download.clicked.connect(lambda: self.onDownloadClick())

            layout.addWidget(self.download)

        self.view = QPushButton(translate("View"))
        self.view.setFixedHeight(24)
        self.view.setStyleSheet(BUTTON_BLUE_STYLE)
        self.view.clicked.connect(lambda: self.onViewClick())

        layout.addWidget(self.view)

        if wasInstalled:
            self.save = QPushButton(translate("Save projects"))
            self.save.setFixedHeight(24)
            self.save.setStyleSheet(BUTTON_BLUE_STYLE)
            self.save.clicked.connect(lambda: self.onSaveProjectsClick())

            layout.addWidget(self.save)

            self.load = QPushButton(translate("Load projects"))
            self.load.setFixedHeight(24)
            self.load.setStyleSheet(BUTTON_BLUE_STYLE)
            self.load.clicked.connect(lambda: self.onLoadProjectsClick())

            layout.addWidget(self.load)

        self.setLayout(layout)

    def onViewClick(self):
        webbrowser.open(f"https://github.com/artyom7774/Game-Engine-3/releases/tag/GE{self.version}")

    def onDownloadClick(self):
        if not self.wasInstalled:
            self.download.setText(translate("Please wait..."))
            self.download.setDisabled(True)

            try:
                url = f"https://github.com/artyom7774/Game-Engine-3/releases/download/GE{self.version}/Game-Engine-3-windows.sfx.exe"
                folder = f"versions/Game Engine {self.version}/"

                self.project.downloading = True

                thr = VersionDownloadThread(url, folder, self.version)
                thr.finished.connect(self.onDownloadComplete)
                thr.start()

            except Exception as e:
                if str(e).startswith("404"):
                    self.project.init()

                    print("ERROR: version is not found")

                    MessageBox.error("Version is not found")

                    return

                else:
                    self.project.init()

                    print("ERROR: can't download engine, bad internet")

                    MessageBox.error("Check your internet connection")

                    return

        else:
            thr = threading.Thread(target=lambda: os.system(f"cd \"versions/Game Engine {self.version}\" && \"Game Engine 3.exe\""))
            thr.daemon = False
            thr.start()

    def onDownloadComplete(self):
        self.project.downloading = False

        self.project.init()

    def onSaveProjectsClick(self):
        pathLoad = f"versions/Game Engine {self.version}/projects"
        pathSave = f"projects"

        for project in os.listdir(pathLoad):
            if os.path.exists(f"{pathSave}/{project}"):
                shutil.rmtree(f"{pathSave}/{project}")

            shutil.copytree(f"{pathLoad}/{project}", f"{pathSave}/{project}")

    def onLoadProjectsClick(self):
        pathLoad = f"projects"
        pathSave = f"versions/Game Engine {self.version}/projects"

        for project in os.listdir(pathLoad):
            if os.path.isfile(f"{pathLoad}/{project}"):
                continue

            if os.path.exists(f"{pathSave}/{project}"):
                shutil.rmtree(f"{pathSave}/{project}")

            shutil.copytree(f"{pathLoad}/{project}", f"{pathSave}/{project}")


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

        self.menubar = None
        self.dialog = None

        self.downloading = False

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
        self.objects["menu_versions"].setIcon(QIcon(f"scr/files/sprites/menu/{SETTINGS['theme']}/versions.png"))
        self.objects["menu_versions"].setIconSize(QSize(80, 80))
        self.objects["menu_versions"].show()

        def menuVersionsSolve():
            self.selectMenu = "versions"

            self.init()

        self.objects["menu_versions"].clicked.connect(lambda: menuVersionsSolve())

        self.objects["menu_projects"] = QPushButton(self)
        self.objects["menu_projects"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_projects"].setGeometry(0, 100 - 1, 100, 100)
        self.objects["menu_projects"].setIcon(QIcon(f"scr/files/sprites/menu/{SETTINGS['theme']}/projects.png"))
        self.objects["menu_projects"].setIconSize(QSize(80, 80))
        self.objects["menu_projects"].show()

        def menuProjectsSolve():
            self.selectMenu = "projects"

            self.init()

        self.objects["menu_projects"].clicked.connect(lambda: menuProjectsSolve())

        self.objects["menu_about"] = QPushButton(self)
        self.objects["menu_about"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_about"].setGeometry(0, 200 - 2, 100, 100)
        self.objects["menu_about"].setIcon(QIcon(f"scr/files/sprites/menu/{SETTINGS['theme']}/about.png"))
        self.objects["menu_about"].setIconSize(QSize(80, 80))
        self.objects["menu_about"].show()

        def menuAboutSolve():
            self.selectMenu = "about"

            self.init()

        self.objects["menu_about"].clicked.connect(lambda: menuAboutSolve())

        self.objects["menu_settings"] = QPushButton(self)
        self.objects["menu_settings"].setStyleSheet("border-radius: 0px;")
        self.objects["menu_settings"].setGeometry(0, 300 - 3, 100, 100)
        self.objects["menu_settings"].setIcon(QIcon(f"scr/files/sprites/menu/{SETTINGS['theme']}/settings.png"))
        self.objects["menu_settings"].setIconSize(QSize(80, 80))
        self.objects["menu_settings"].show()

        def menuSettingsSolve():
            self.selectMenu = "settings"

            self.init()

        self.objects["menu_settings"].clicked.connect(lambda: menuSettingsSolve())

        self.show()

    def init(self) -> None:
        if self.downloading:
            return

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
        if self.downloading:
            return

        global VERSIONS_WAS_LOADED

        self.objects["main"]["scroll_area"] = QScrollArea(self)
        self.objects["main"]["scroll_area"].setGeometry(107, 10, self.width() - 130, self.height() - 42)
        self.objects["main"]["scroll_area"].setWidgetResizable(True)

        if SETTINGS["theme"] == "dark":
            self.objects["main"]["scroll_area"].setStyleSheet("QScrollArea { border: 1px solid #3f4042; };")

        else:
            self.objects["main"]["scroll_area"].setStyleSheet("QScrollArea { border: 1px solid #dadce0; };")

        scrollWidget = QWidget()
        scrollLayout = QVBoxLayout(scrollWidget)
        scrollLayout.setSpacing(5)

        url = "https://raw.githubusercontent.com/artyom7774/Game-Engine-3/main/scr/files/updates.json"

        if not VERSIONS_WAS_LOADED:
            try:
                print("LOG: download list of versions...")

                response = requests.get(url)
                data = response.json()

            except Exception:
                print("ERROR: can't download versions list, using last list of versions")

                data = json.load(open("scr/files/versions.json", "r", encoding="utf-8"))

            else:
                print("LOG: successful")

                with open("scr/files/versions.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)

                VERSIONS_WAS_LOADED = True

        else:
            data = json.load(open("scr/files/versions.json", "r", encoding="utf-8"))

        versions = []

        for version in data["sorted"]:
            versions.append(version)

        items = []

        versions = versions[::-1]

        for version in versions:
            name = data["updates"][version]["name"]
            log = data["updates"][version]["text"]

            wasInstalled = os.path.exists(f"versions/Game Engine {version}/")

            version_item = VersionItem(name, log, version, wasInstalled, self)

            scrollLayout.addWidget(version_item)

            items.append(version_item)

        scrollLayout.addStretch()

        self.objects["main"]["scroll_area"].setWidget(scrollWidget)
        self.objects["main"]["scroll_area"].show()

    def projectsMenu(self):
        if self.downloading:
            return

        self.objects["main"]["scroll_area"] = QScrollArea(self)
        self.objects["main"]["scroll_area"].setGeometry(107, 10, self.width() - 130, self.height() - 42)

        if SETTINGS["theme"] == "dark":
            self.objects["main"]["scroll_area"].setStyleSheet("QScrollArea { border: 1px solid #3f4042; };")

        else:
            self.objects["main"]["scroll_area"].setStyleSheet("QScrollArea { border: 1px solid #dadce0; };")

        scrollWidget = QWidget()
        scrollLayout = QVBoxLayout(scrollWidget)

        items = []

        cnt = 0

        for project in os.listdir("projects"):
            if os.path.isfile(f"projects/{project}"):
                continue

            if not os.path.exists(f"projects/{project}/version.json"):
                with open(f"projects/{project}/version.json", "w", encoding="utf-8") as file:
                    json.dump({"version": "3.11.0"}, file, indent=4)

            project_item = ProjectItem(f"projects/{project}", self)

            scrollLayout.addWidget(project_item)

            items.append(project_item)

            cnt += 1

        scrollLayout.addStretch()

        self.objects["main"]["scroll_area"].setWidget(scrollWidget)

        if cnt == 0:
            self.objects["main"]["title"] = QLabel(self)
            self.objects["main"]["title"].setFont(BIG_HELP_FONT)
            self.objects["main"]["title"].setText(translate("No projects"))
            self.objects["main"]["title"].setGeometry(100, 5, 400, 30)
            self.objects["main"]["title"].show()

        else:
            self.objects["main"]["scroll_area"].show()

    def aboutMenu(self):
        if self.downloading:
            return

        self.objects["main"]["title"] = QLabel(self)
        self.objects["main"]["title"].setFont(BIG_HELP_FONT)
        self.objects["main"]["title"].setText(translate("About"))
        self.objects["main"]["title"].setGeometry(100, 5, 400, 30)
        self.objects["main"]["title"].show()

        self.objects["main"]["github"] = QLabel(self)
        self.objects["main"]["github"].setFont(HELP_FONT)
        self.objects["main"]["github"].setText(f"{translate('GitHub')}: <a href='https://github.com/artyom7774/GELauncher'>https://github.com/artyom7774/GELauncher</a>")
        self.objects["main"]["github"].setOpenExternalLinks(True)
        self.objects["main"]["github"].setGeometry(100, 35, 1000, 30)
        self.objects["main"]["github"].show()

        self.objects["main"]["site"] = QLabel(self)
        self.objects["main"]["site"].setFont(HELP_FONT)
        self.objects["main"]["site"].setText(f"{translate('Project site')}: <a href='https://artyom7777.pythonanywhere.com'>https://artyom7777.pythonanywhere.com</a>")
        self.objects["main"]["site"].setOpenExternalLinks(True)
        self.objects["main"]["site"].setGeometry(100, 55, 1000, 30)
        self.objects["main"]["site"].show()

        self.objects["main"]["discord"] = QLabel(self)
        self.objects["main"]["discord"].setFont(HELP_FONT)
        self.objects["main"]["discord"].setText(f"{translate('Discord community')}: <a href='https://discord.gg/FxY6Kfgx57'>https://discord.gg/FxY6Kfgx57</a>")
        self.objects["main"]["discord"].setOpenExternalLinks(True)
        self.objects["main"]["discord"].setGeometry(100, 95, 1000, 30)
        self.objects["main"]["discord"].show()

    def settingsMenu(self):
        if self.downloading:
            return

        self.objects["main"]["title"] = QLabel(self)
        self.objects["main"]["title"].setFont(BIG_HELP_FONT)
        self.objects["main"]["title"].setText(translate("Settings"))
        self.objects["main"]["title"].setGeometry(100, 5, 400, 30)
        self.objects["main"]["title"].show()

        self.objects["main"]["language_label"] = QLabel(self)
        self.objects["main"]["language_label"].setFont(HELP_FONT)
        self.objects["main"]["language_label"].setText(f"{translate('Language')}:")
        self.objects["main"]["language_label"].setGeometry(100, 35, 1000, 30)
        self.objects["main"]["language_label"].show()

        self.objects["main"]["language_combobox"] = QComboBox(parent=self)

        self.objects["main"]["language_combobox"].addItems([obj for obj in LANGUAGES.values()])
        for i, name in enumerate(LANGUAGES):
            self.objects["main"]["language_combobox"].setItemIcon(i, QIcon(LANGUAGES_ICONS[name]))

        self.objects["main"]["language_combobox"].setCurrentIndex([translate(obj).lower() == translate(LANGUAGES[SETTINGS["language"]]).lower() for obj in LANGUAGES.values()].index(True))
        self.objects["main"]["language_combobox"].setGeometry(210, 35 + 2, 300, 20)
        self.objects["main"]["language_combobox"].setFont(FONT)
        self.objects["main"]["language_combobox"].show()

        self.objects["main"]["language_combobox"].currentIndexChanged.connect(lambda: self.onLanguageClick())

        self.objects["main"]["theme_label"] = QLabel(self)
        self.objects["main"]["theme_label"].setFont(HELP_FONT)
        self.objects["main"]["theme_label"].setText(f"{translate('Theme')}:")
        self.objects["main"]["theme_label"].setGeometry(100, 65, 1000, 30)
        self.objects["main"]["theme_label"].show()

        self.objects["main"]["theme_combobox"] = QComboBox(parent=self)
        self.objects["main"]["theme_combobox"].addItems([translate(obj) for obj in THEMES.values()])
        self.objects["main"]["theme_combobox"].setCurrentIndex([translate(obj).lower() == translate(THEMES[SETTINGS["theme"]]).lower() for obj in THEMES.values()].index(True))
        self.objects["main"]["theme_combobox"].setGeometry(210, 65 + 2, 300, 25)
        self.objects["main"]["theme_combobox"].setFont(FONT)
        self.objects["main"]["theme_combobox"].show()

        self.objects["main"]["theme_combobox"].currentIndexChanged.connect(lambda: self.onThemeClick())

    def onLanguageClick(self):
        SETTINGS["language"] = list(LANGUAGES.keys())[self.objects["main"]["language_combobox"].currentIndex()]

        with open("scr/files/settings/settings.json", "w", encoding="utf-8") as file:
            json.dump(SETTINGS, file, indent=4)

        thr = threading.Thread(target=lambda: self.newRunProgram())
        thr.start()

        self.close()

    def onThemeClick(self):
        SETTINGS["theme"] = list(THEMES.keys())[self.objects["main"]["theme_combobox"].currentIndex()]

        with open("scr/files/settings/settings.json", "w", encoding="utf-8") as file:
            json.dump(SETTINGS, file, indent=4)

        thr = threading.Thread(target=lambda: self.newRunProgram())
        thr.start()

        self.close()

    def newRunProgram(self):
        if SYSTEM == "Windows":
            if DIVELOP:
                subprocess.run(["venv/Scripts/python.exe", "GELauncher.py"])

            else:
                subprocess.run(["GELauncher.exe"])

        elif SYSTEM == "Linux":
            pass

        else:
            print("ERROR: system (Unknown) not supported this opperation")

    def menu(self) -> None:
        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.clear()

    def shortcut(self) -> None:
        pass

    def closeEvent(self, event) -> None:
        event.accept()
