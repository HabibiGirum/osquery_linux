import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QMessageBox,QSystemTrayIcon,QMenu,QAction
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, QDateTime,Qt
import subprocess
import requests
import json

class VistarSyncApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.query_data = [
            'SELECT uuid FROM system_info;',
            'SELECT name FROM os_version;',
            # 'SELECT computer_name FROM system_info;',
            # "SELECT CASE WHEN enabled = 1 THEN 'Yes' ELSE 'No' END AS screenlock_enabled FROM screenlock;",
            # "SELECT CASE WHEN enabled = 1 THEN 'Yes' ELSE 'No' END AS screenlock_enabled FROM screenlock;",
            # "SELECT CASE WHEN encrypted = 1 THEN 'Yes' ELSE 'No' END AS disk_encryption FROM disk_encryption;",
            # "SELECT CASE WHEN EXISTS (SELECT 1 FROM apps WHERE name LIKE '%1Password.app%') THEN 'Yes' ELSE 'No' END AS password_manager;",
            # "SELECT CASE WHEN EXISTS (SELECT 1 FROM apps WHERE name LIKE '% Antivirus.app') THEN 'Yes' ELSE 'No' END AS Antivirius;"
        ]

        # self.setWindowFlags(PyQt5.QtCore.Qt.Window | PyQt5.QtCore.Qt.CustomizeWindowHint | PyQt5.QtCore.Qt.WindowTitleHint)  # Corrected the usage of QtCore
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)

        self.endpoint_Api= "https://api.vistar.cloud/api/v1/computers/osquery_log_data/"
        self.interval_seconds = 60
        self.last_sync_time = None
        self.sync_active = False
        if self.sync_active == False:
            self.display_mac_addresses()
        else:
            pass

        # self.create_UI()
    def warning_UI(self):
        self.setGeometry(1200, 50, 250, 0)

        pass

 

    def create_UI(self):
        self.setWindowTitle("Vistar MDM . . .")
        self.setStyleSheet("QMainWindow::title { background-color: black; color: white; border: 20px solid gray; font-size: 20px; }")

        # Set the application icon
        self.setWindowIcon(QIcon("/home/habg/Documents/Vistar/Resources/images/vistar.ico"))
        # Create a QLabel for the image
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Load toggle images
        self.start_image = QPixmap("/home/habg/Documents/Vistar/Resources/images/toggle_off.ico")
        self.stop_image = QPixmap("/home/habg/Documents/Vistar/Resources/images/toggle_on.ico")

        # Create a QLabel for the image
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap("/home/habg/Documents/Vistar/Resources/images/vistar.ico"))  
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Create a QLabel for the text
        text_label = QLabel("Sync Your Data!", self)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        # Create the toggle button with the start image
        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(QIcon(self.start_image))
        self.toggle_button.clicked.connect(self.on_toggle)
        layout.addWidget(self.toggle_button)

        central_widget.setLayout(layout)

        # Adding style to the button for better visualization
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                width: auto;  
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        self.toggle_button.setStyleSheet(button_style)

        self.update_toggle_button_label()

        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.sync_data)
        self.sync_timer.start(self.interval_seconds * 1000)

        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry(desktop.primaryScreen())
        self.move(screen_rect.right() - self.width() - 20, 20)
        
    
    def on_toggle(self):
        self.sync_active = not self.sync_active

        if self.sync_active:
            # self.last_sync_time = QDateTime.currentDateTime()
            self.sync_data()
        self.update_toggle_button_label()

    def sync_data(self):
        current_time = QDateTime.currentDateTime()
        # print(self.last_sync_time)
        # print(self.sync_active)
        
        # Check if self.last_sync_time is None and self.sync_active
        if self.last_sync_time is None and self.sync_active:
            # print("this None")
            self.last_sync_time = current_time
            osquery_data = self.run_osquery_and_send_data()
            # print(osquery_data)
            self.send_data_to_api(osquery_data)

        # Check if self.last_sync_time is not None before accessing its attributes
        if self.last_sync_time is not None:
            elapsed_time = (current_time.toSecsSinceEpoch() - self.last_sync_time.toSecsSinceEpoch())

            if elapsed_time >= self.interval_seconds and self.sync_active:
                # print("this is after start")
                osquery_data = self.run_osquery_and_send_data()
                self.send_data_to_api(osquery_data)
                self.last_sync_time = current_time

        if self.sync_active:
            self.sync_timer.start(self.interval_seconds * 1000)


    def send_data_to_api(self, data):
        data = {"data": data}
        requests.post(self.endpoint_Api, json=data)
        # try:
            

            # if response.status_code == 201:
            #     print(f"Data sent successfully. status code :{response.status_code}")
            # else:
            #     print(f"faild to send data. status code : {response.status_code}")
        # except requests.exceptions.RequestException as e:
        #     print(f'Error sending data : {e}')

    def run_osquery_and_send_data(self):
        all_osquery_data = []
        for query in self.query_data:
            # try:
            osquery_output = subprocess.check_output(["/bin/osqueryi", "--json", query], universal_newlines=True)
            osquery_data = json.loads(osquery_output)
            all_osquery_data.append(osquery_data)
            # except subprocess.CalledProcessError as e:
            #     print(f"Error running osquery for query '{query}': {e}")
            # except Exception as e:
            #     print(f"Error processing query '{query}': {e}")

        return all_osquery_data

    def update_toggle_button_label(self):
        label = "Stop Sync." if self.sync_active else "Start Sync"
        self.toggle_button.setText(label)

        if self.sync_active:
            self.toggle_button.setIcon(QIcon(self.stop_image))
        else:
            self.toggle_button.setIcon(QIcon(self.start_image))
    def on_exit(self):
        sys.exit()
    def show_window(self):
        if self.isVisible():
            toggle_app_action.setText("close")
            self.hide()
        else:
            toggle_app_action.setText("open")
            self.showNormal()



    def display_mac_addresses(self):
        try:
            local_mac_address = self.get_mac_address()
            print(local_mac_address)

            if local_mac_address:
                # Send local MAC address to the server
                data = {"mac_address": local_mac_address}
                response = requests.post("https://api.vistar.cloud/api/v1/computers/check_mac_address/", json=data)
                # print(response.status_code)

                if response.status_code == 200:
                    result = response.json()
                    mac_address_matched = result.get("status")
                    print(mac_address_matched)

                    if mac_address_matched:
                        message_box = QMessageBox()
                        message_box.setWindowTitle("Vistar MDM . . .")
                        message_box.setText("Hello We are Vistar Agent\nThank you for Registration!")
                        message_box.setIcon(QMessageBox.Information)
                        # message_box.setIcon("/home/habg/Documents/Vistar/Resources/images/vistar.ico")
                        message_box.setIconPixmap(QPixmap("/home/habg/Documents/Vistar/Resources/images/vistar.ico"))
                        message_box.addButton(QMessageBox.Ok)
                        message_box.setDefaultButton(QMessageBox.Ok)

                        # Adjust the position of the message box to the right corner
                        desktop = QApplication.desktop()
                        screen_rect = desktop.screenGeometry(desktop.primaryScreen())
                        message_box.move(screen_rect.right() - message_box.width() - 20, 20)
                        # message_box.move(20, 20)

                        message_box.exec_()
                        self.create_UI()
                    else:
                        message_box = QMessageBox()
                        message_box.setWindowTitle("Vistar MDM . . .")
                        message_box.setText("Please Register before start sync.\n Go to our website and register \n https://vistar.cloude")
                        message_box.setIcon(QMessageBox.Warning)
                        message_box.setIconPixmap(QPixmap("/home/habg/Documents/Vistar/Resources/images/vistar.ico"))
                        message_box.addButton(QMessageBox.Ok)
                        message_box.setDefaultButton(QMessageBox.Ok)

                        # Adjust the position of the message box to the right corner
                        desktop = QApplication.desktop()
                        screen_rect = desktop.screenGeometry(desktop.primaryScreen())
                        message_box.move(screen_rect.right() - message_box.width() - 20, 20)

                        message_box.exec_()
                        self.warning_UI()
                else:
                    # print(f"Failed to check MAC address. Status code: {response.status_code}")
                    message_box = QMessageBox()
                    message_box.setWindowTitle("Vistar MDM . . .")
                    message_box.setText("Please Register before start sync.\n Go to our website and register \n https://vistar.cloude")
                    message_box.setIcon(QMessageBox.Warning)
                    message_box.addButton(QMessageBox.Ok)
                    message_box.setDefaultButton(QMessageBox.Ok)

                        # Adjust the position of the message box to the right corner
                    desktop = QApplication.desktop()
                    screen_rect = desktop.screenGeometry(desktop.primaryScreen())
                    message_box.move(screen_rect.right() - message_box.width() - 20, 20)

                    message_box.exec_()
                    self.warning_UI()
            else:
                QMessageBox.warning(self, "Failed to Get MAC Address", "Please check your internet")
        except requests.exceptions.RequestException as e:
            # print(f"Failed to check MAC address. Status code: {response.status_code}")
            message_box = QMessageBox()
            message_box.setWindowTitle("Vistar MDM . . .")
            message_box.setText("Hello we are vistar angent before start to \nsync your data please check your internate ...")
            message_box.setIcon(QMessageBox.Warning)
            message_box.addButton(QMessageBox.Ok)
            message_box.setDefaultButton(QMessageBox.Ok)

                        # Adjust the position of the message box to the right corner
            desktop = QApplication.desktop()
            screen_rect = desktop.screenGeometry(desktop.primaryScreen())
            message_box.move(screen_rect.right() - message_box.width() - 20, 20)

            message_box.exec_()
            self.warning_UI()
            # print(f'Error check your internate: {e}')
            pass






            
    def get_mac_address(self):
        try:
            command = [
                '/bin/osqueryi',
                '--header=false',
                '--csv',
                "SELECT GROUP_CONCAT(mac, '_')AS mac FROM interface_details;",
            ]

            result = subprocess.run(command, capture_output=True, text=True)
            mac_address = result.stdout.strip()

            return mac_address
        except subprocess.CalledProcessError as e:
            # print(f"Failed to get MAC address: {e}")
            return None
     
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    osquery_app = VistarSyncApp()

    icon = QIcon("/home/habg/Documents/Vistar/Resources/images/vistar.ico")

    # Adding item on the menu bar
    tray = QSystemTrayIcon(icon)
    tray.setVisible(True)

    # Creating the options
    menu = QMenu()
    

    # Creating an instance of OsquerySyncApp

    # To open or close OsquerySyncApp when the system tray icon is clicked
    toggle_app_action = QAction("Open Vistar MDM")
    toggle_app_action.triggered.connect(osquery_app.show_window)
    menu.addAction(toggle_app_action)

    # To quit the app
    quit = QAction("Restart")
    quit.triggered.connect(osquery_app.on_exit)
    menu.addAction(quit)
    # display_mac_addresses()
    # Adding options to the system tray
    tray.setContextMenu(menu)

    osquery_app.show()

    sys.exit(app.exec_())