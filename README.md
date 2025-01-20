# Ad-Huner
AdHunter is a software tool designed to detect and remove unwanted ad patches and intrusive advertisements from applications. It scans programs for hidden adware or unwanted modifications and eliminates them, ensuring a smoother user experience without annoying pop-ups or disruptive ads.

Installation Guide
To run the program you’ve written using PyQt5 and adbutils, you need to install a few essential libraries on your machine. Here's how to set it up:

1. Install Python
Ensure that you have Python installed on your system. You can download it from here. During installation, make sure to check the option "Add Python to PATH."

2. Install Required Libraries
To install the necessary libraries to run the program, open Command Prompt (Windows) or Terminal (Mac/Linux) and use pip to install the following libraries:

`pip install PyQt5 adbutils`

PyQt5: A library for building graphical user interfaces (GUIs).
adbutils: A library for interacting with Android devices using the ADB protocol.
3. Ensure ADB is Installed
You must have the ADB (Android Debug Bridge) tool installed on your computer to interact with an Android device. You can download ADB from the Android Developer website.

After installation, check if ADB is working correctly by opening Command Prompt or Terminal and running:

`adb devices`

Program Overview
This program monitors applications on a connected Android device and detects the app running in the foreground. It also provides information about the app, such as installation date and source, and allows users to uninstall unwanted apps.

Key Components of the Program:
Graphical User Interface (GUI):

Built using PyQt5 for creating the user interface.
The interface has a "Start Monitoring" button to begin tracking running apps and a "Stop Monitoring" button to stop the process.
When a new foreground app is detected, the program displays information such as installation date and source (e.g., Google Play Store or external source).
You can uninstall apps using the "Uninstall" button next to each app.
Interaction with the Android Device:

adbutils is used to interact with the Android device via ADB.
ADB commands are used to fetch details about the current foreground app, such as its name and installation data.
If the app displaying ads is detected, the user can uninstall it directly from the program.
Main Classes in the Program:
MainWindow: The main window containing the graphical user interface.
MonitorThread: A background thread that detects the app currently in the foreground.
check_connection: A function that checks the connection to the Android device via ADB.
get_foreground_app: A function that retrieves the package name of the currently running app.
4. How to Use:
Connect your Android device via USB.
Open the program and click on the "Check Connection" button to verify the connection.
Once the connection is verified, click the "Start Monitoring" button to start tracking the apps.
The program will show the currently running apps along with details like installation date and source.
You can uninstall unwanted apps by clicking the "Uninstall" button next to the app name.
Notes:
Ensure that the "Developer Options" and "USB Debugging" are enabled on your Android device (Settings > Developer options > USB debugging).

