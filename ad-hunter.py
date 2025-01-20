import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, QScrollArea, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal
import adbutils
from datetime import datetime


def check_connection():
    try:
        adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        devices = adb.device_list()

        if not devices:
            return False, "No devices connected. Please connect a device."
        
        device = devices[0]
        if device.get_state() == "device":
            return True, f"Device connected: {device.serial}"
        else:
            return False, f"Device is not in a valid state: {device.get_state()}"
    except Exception as e:
        return False, f"Error checking connection: {e}"


class MonitorThread(QThread):
    foreground_app_signal = pyqtSignal(str)

    def run(self):
        last_app = None
        while True:
            current_app = self.get_foreground_app()
            if current_app and current_app != last_app:
                self.foreground_app_signal.emit(current_app)
                last_app = current_app
            time.sleep(2)

    @staticmethod
    def get_foreground_app():
        """Get the package name of the app currently in the foreground using adbutils."""
        try:
            adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            device = adb.device()
            result = device.shell("dumpsys window | grep mCurrentFocus")
            if result:
                output = result.strip()
                if "u0" in output:
                    package_activity = output.split(" ")[-1]
                    package_name = package_activity.split("/")[0]
                    return package_name
            return None
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def get_installation_info(package_name):
        try:
            adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            device = adb.device()

            result = device.shell(f"dumpsys package {package_name}")
            
            install_date = None
            source = None
            
            first_install_time = None
            for line in result.splitlines():
                if "firstInstallTime" in line:
                    first_install_time = line.split('=')[-1].strip()
                    install_date = datetime.utcfromtimestamp(int(first_install_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    break
            
            for line in result.splitlines():
                if "installer" in line:
                    source = line.split('=')[-1].strip()
                    break

            return install_date, source

        except Exception as e:
            return None, None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Ad hunter")
        self.setGeometry(200, 200, 600, 400)

        self.active_apps = {}
        self.init_ui()
        self.monitor_thread = MonitorThread()
        self.monitor_thread.foreground_app_signal.connect(self.update_foreground_app)

    def init_ui(self):
        layout = QVBoxLayout()

        self.name_label = QLabel("Developed by: Hossam salem \n it's free software'")
        layout.addWidget(self.name_label)  

        self.label = QLabel("Press 'Start Monitoring' to detect the app displaying ads:")
        layout.addWidget(self.label)

        
        button_layout = QHBoxLayout()

        self.check_button = QPushButton("Check Connection")
        self.check_button.clicked.connect(self.check_device_connection)
        button_layout.addWidget(self.check_button)

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setEnabled(False)  
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def check_device_connection(self):
        is_connected, message = check_connection()
        if is_connected:
            QMessageBox.information(self, "Device Connection", message)
            self.start_button.setEnabled(True)  
        else:
            QMessageBox.warning(self, "Device Connection", message)
            self.start_button.setEnabled(False)  

    def start_monitoring(self):
        self.monitor_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_monitoring(self):
        self.monitor_thread.terminate()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_foreground_app(self, app_name):
        if app_name not in self.active_apps:
            app_layout = QHBoxLayout()

            app_label = QLabel(app_name)
            app_layout.addWidget(app_label)

            install_date, source = MonitorThread.get_installation_info(app_name)
            install_label = QLabel(f"Installed on: {install_date if install_date else 'N/A'}")
            source_label = QLabel(f"Source: {source if source else 'N/A'}")
            app_layout.addWidget(install_label)
            app_layout.addWidget(source_label)

            uninstall_button = QPushButton("Uninstall")
            if app_name.startswith("com.android") or app_name.startswith("system"):
                uninstall_button.setEnabled(False)
            uninstall_button.clicked.connect(lambda: self.uninstall_app(app_name))
            app_layout.addWidget(uninstall_button)

            self.scroll_area_layout.addLayout(app_layout)
            self.active_apps[app_name] = app_layout

    def uninstall_app(self, package_name):
        try:
            adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            device = adb.device()

            result = device.shell(f"pm uninstall {package_name}")
            if "Success" in result:
                QMessageBox.information(self, "Success", f"App '{package_name}' uninstalled successfully.")

                app_layout = self.active_apps.pop(package_name, None)
                if app_layout:
                    for i in reversed(range(app_layout.count())):
                        widget = app_layout.itemAt(i).widget()
                        if widget:
                            widget.deleteLater()
            else:
                QMessageBox.warning(self, "Error", f"Failed to uninstall app '{package_name}'. Error: {result.strip()}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
