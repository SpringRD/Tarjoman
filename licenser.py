from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUiType

import os
import sys
import wmi
import hashlib


bundle_dir = parent_dir = None

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    parent_dir = os.path.dirname(sys.executable)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = bundle_dir

license_path = os.path.join(parent_dir, "license.lcs")


def get_serial():
    c = wmi.WMI()
    try:
        for item in c.Win32_PhysicalMedia():
            if item.wmi_property('Tag').value == "\\\\.\\PHYSICALDRIVE0":
                ser = item.wmi_property('SerialNumber').value
                break
        serial = ""
        for ch in ser:
            if not ch == ' ':
                serial += ch
        # serial = c.Win32_PhysicalMedia()[0].SerialNumber
        print("Serial: " + serial)
        return serial
    except:
        print("Serial is None")
        return None


def get_license(ser, art_id):
    code = art_id + "_" + ser
    key = hashlib.md5(code.encode()).hexdigest()
    upper = key.upper()
    my_license = ""
    i = 0
    for ch in upper:
        i += 1
        my_license += ch
        if (i % 4) == 0 and i < len(upper):
            my_license += "-"
    print("License: " + my_license)
    return my_license


def check_lic(my_lic):
    if os.path.exists(license_path):
        lcs_file = open(license_path, 'r')
        lcs = lcs_file.read()
        if lcs == my_lic:
            return True
    return False


class MainClass(QMainWindow):

    def __init__(self):
        super(MainClass, self).__init__()

        self.setWindowTitle("My App")

        label = QLabel("This is a the main window!")

        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)


app = QApplication(sys.argv)
main_ui = MainClass()
license_class, _ = loadUiType(os.path.join(bundle_dir, "ui\\licenser.ui"))


class LicenseClass(QMainWindow, license_class):
    def __init__(self, serial, my_license):
        super(LicenseClass, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.serial = serial
        self.my_license = my_license

        self.handle_ui()
        self.handle_buttons()

    def handle_ui(self):
        self.serial_edit.setText(self.serial)

    def handle_buttons(self):
        self.ok_button.clicked.connect(self.ok)

    def ok(self):
        if self.serial_edit.text() == "" or self.license_edit.text() == "":
            return
        lcs = self.license_edit.text()
        if not lcs == self.my_license:
            self.license_edit.setText("")
        else:
            f = open(license_path, 'w')
            f.write(lcs)
            self.close()
            main_ui.show()


def main():
    artifact = "nameOfApp"
    serial = get_serial()
    if serial is None:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Error)
        msg_box.setText("هناك مشكلة في استخراج الرقم التسلسلي.\nالرجاء تجربة تفعيل البرنامج بصلاحية المدير.")
        msg_box.setWindowTitle("الرقم التسلسلي")
        msg_box.exec()
    else:
        my_license = get_license(serial, artifact)
        lic_ui = LicenseClass(serial, my_license)
        res = check_lic(my_license)
        if res:
            main_ui.show()
        else:
            lic_ui.show()
    app.exec_()


if __name__ == '__main__':
    main()
