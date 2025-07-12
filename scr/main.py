from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidget, QLabel, QStatusBar, QAction, QTreeWidgetItem, QShortcut, QPushButton, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout
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


class VersionItem(QWidget):
    def __init__(self, name, changelog="", parent=None):
        super().__init__(parent)

        self.project = parent

        self.name = name
        self.changelog = changelog

        # self.setFixedHeight(120)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)

        self.label = QLabel(name)
        self.label.setFont(BIG_HELP_FONT)
        # self.label.setStyleSheet("border: none; font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(self.label)

        self.changelog_label = QLabel(changelog if changelog else "Обновления и исправления ошибок")
        # self.changelog_label.setStyleSheet("border: none; font-size: 12px; color: #cccccc; margin: 5px 0px;")
        self.changelog_label.setWordWrap(True)
        # self.changelog_label.setMaximumHeight(40)
        layout.addWidget(self.changelog_label)

        self.download_button = QPushButton("Скачать")
        self.download_button.setFixedHeight(30)
        self.download_button.setStyleSheet(BUTTON_BLUE_STYLE)
        self.download_button.clicked.connect(lambda: self.onDownloadClick())
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def onDownloadClick(self):
        print(f"Скачивание версии: {self.name}")
        # Здесь можно добавить логику для скачивания конкретной версии


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
        self.objects["main"]["scroll_area"].setStyleSheet("QScrollArea { border: 1px solid #666; }")

        scrollWidget = QWidget()
        scrollLayout = QVBoxLayout(scrollWidget)
        scrollLayout.setSpacing(5)
        scrollLayout.setContentsMargins(10, 10, 10, 10)

        versions_data = [
            ("Godot Engine 4.2.2", "- update moving object by angle\n- message about a program update, if one exists\n- update help menu"),
            ("Godot Engine 4.2.1", "Исправления ошибок в системе анимации. Обновлена поддержка платформ."),
            ("Godot Engine 4.2.0", "Новые возможности 2D и 3D рендеринга. Улучшен редактор сцен."),
            ("Godot Engine 4.1.4", "Стабильные исправления. Оптимизация памяти и производительности."),
            ("Godot Engine 4.1.3", "Исправления ошибок импорта ресурсов. Улучшена совместимость."),
            ("Godot Engine 4.1.2", "Обновления системы физики. Исправления багов редактора."),
            ("Godot Engine 4.1.1", "Мелкие исправления и улучшения стабильности движка."),
            ("Godot Engine 4.1.0", "Крупное обновление с новыми функциями и улучшениями."),
            ("Godot Engine 4.0.4", "Критические исправления и улучшения производительности."),
            ("Godot Engine 4.0.3", "Исправления ошибок и стабилизация работы движка."),
            ("Godot Engine 4.0.2", "Важные исправления после выхода 4.0."),
            ("Godot Engine 4.0.1", "Первые исправления версии 4.0. Улучшения стабильности."),
            ("Godot Engine 4.0.0", "Полностью переработанная версия с поддержкой Vulkan и новым рендерером.")
        ]

        items = []
        for version_name, changelog in versions_data:
            version_item = VersionItem(version_name, changelog, self)

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