from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUiType

import os
import sys
import re
import multiprocessing
import wmi
import hashlib

from transformers import MarianMTModel, MarianTokenizer
from typing import List


bundle_dir = parent_dir = None

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    parent_dir = os.path.dirname(sys.executable)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = bundle_dir

artifact_id = "translator"

dictionaries_path = os.path.join(parent_dir, "Dictionaries")
model_en_path = os.path.join(dictionaries_path, "en-ar")
model_ru_path = os.path.join(dictionaries_path, "ru-ar")
model_he_path = os.path.join(dictionaries_path, "he-ar")

main_class, _ = loadUiType(os.path.join(bundle_dir, "ui\\main.ui"))
license_class, _ = loadUiType(os.path.join(bundle_dir, "ui\\licenser.ui"))


class MainClass(QMainWindow, main_class):
    def __init__(self, my_license):
        super(MainClass, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.my_license = my_license

        self.tokenizer_en = None
        self.model_en = None
        self.tokenizer_ru = None
        self.model_ru = None
        self.tokenizer_he = None
        self.model_he = None

        self.label = QLabel("")
        self.handle_ui()
        self.handle_buttons()

    def handle_ui(self):
        # self.label.setFixedWidth(550)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.statusbar.addPermanentWidget(self.label)
        if os.path.exists(model_en_path):
            self.inputComboBox.addItem("English")
        if os.path.exists(model_ru_path):
            self.inputComboBox.addItem("Russian")
        if os.path.exists(model_he_path):
            self.inputComboBox.addItem("Hebrew")
        if self.inputComboBox.count() == 1:
            self.label.setText('لا يوجد قواميس داخل المجلد {}'.format(dictionaries_path))
        else:
            self.label.setText('تمت إضافة القواميس الموجودة داخل المجلد {}'.format(dictionaries_path))
        self.outputTextEdit.setAlignment(Qt.AlignRight)
        self.repaint()

    def handle_buttons(self):
        self.inputComboBox.currentTextChanged.connect(self.combobox_changed)
        self.translateButton.clicked.connect(self.translate)

    def combobox_changed(self):
        if self.inputComboBox.currentText() == "English":
            self.inputTextEdit.setAlignment(Qt.AlignLeft)
            if self.model_en is None:
                self.label.setText('جاري تحميل القاموس، الرجاء الانتظار')
                self.repaint()
                self.tokenizer_en = MarianTokenizer.from_pretrained(model_en_path)
                self.model_en = MarianMTModel.from_pretrained(model_en_path)
                self.label.setText('تم تحميل القاموس')
        elif self.inputComboBox.currentText() == "Russian":
            self.inputTextEdit.setAlignment(Qt.AlignLeft)
            if self.model_ru is None:
                self.label.setText('جاري تحميل القاموس، الرجاء الانتظار')
                self.repaint()
                self.tokenizer_ru = MarianTokenizer.from_pretrained(model_ru_path)
                self.model_ru = MarianMTModel.from_pretrained(model_ru_path)
                self.label.setText('تم تحميل القاموس')
        elif self.inputComboBox.currentText() == "Hebrew":
            self.inputTextEdit.setAlignment(Qt.AlignRight)
            if self.model_he is None:
                self.label.setText('جاري تحميل القاموس، الرجاء الانتظار')
                self.repaint()
                self.tokenizer_he = MarianTokenizer.from_pretrained(model_he_path)
                self.model_he = MarianMTModel.from_pretrained(model_he_path)
                self.label.setText('تم تحميل القاموس')
        self.repaint()

    def translate(self):
        self.label.setText('')
        self.outputTextEdit.clear()
        self.repaint()
        if self.inputComboBox.currentText() == "":
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("الرجاء اختيار لغة الإدخال.")
            msgBox.setWindowTitle("لغة الإدخال")
            msgBox.exec()
            return
        match = re.match('^\s*$', self.inputTextEdit.toPlainText())
        if match:
            self.inputTextEdit.clear()
            self.repaint()
            return
        self.label.setText('جاري الترجمة، الرجاء الانتظار')
        self.repaint()
        src_text = list()
        words = List[str]
        src_text.append(self.inputTextEdit.toPlainText())
        if self.inputComboBox.currentText() == "English":
            translated = self.model_en.generate(**self.tokenizer_en.prepare_seq2seq_batch(src_text, return_tensors="pt"))
            words: List[str] = self.tokenizer_en.batch_decode(translated, skip_special_tokens=True)
        elif self.inputComboBox.currentText() == "Russian":
            translated = self.model_ru.generate(**self.tokenizer_ru.prepare_seq2seq_batch(src_text, return_tensors="pt"))
            words: List[str] = self.tokenizer_ru.batch_decode(translated, skip_special_tokens=True)
        else:
            translated = self.model_he.generate(**self.tokenizer_he.prepare_seq2seq_batch(src_text, return_tensors="pt"))
            words: List[str] = self.tokenizer_he.batch_decode(translated, skip_special_tokens=True)
        for item in words:
            self.outputTextEdit.append(item)
            self.label.setText('تمت الترجمة')
            self.repaint()


class LicenseClass(QMainWindow, license_class):
    def __init__(self, parent, serial):
        super(LicenseClass, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.serial = serial

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
        if not lcs == self.parent.my_license:
            self.license_edit.setText("")
        else:
            license_path = os.path.join(parent_dir, "license.lcs")
            f = open(license_path, 'w')
            f.write(lcs)
            self.close()
            self.parent.show()


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
        return serial
    except:
        return None


def get_license(ser, art_id):
    code = art_id + "_" + ser
    key = hashlib.md5(code.encode()).hexdigest()
    upper = key.upper()
    final = ""
    i = 0
    for ch in upper:
        i += 1
        final += ch
        if (i % 4) == 0 and i < len(upper):
            final += "-"
    return final


def check_lic(my_lic):
    license_path = os.path.join(parent_dir, "license.lcs")
    if os.path.exists(license_path):
        lcs_file = open(license_path, 'r')
        lcs = lcs_file.read()
        if lcs == my_lic:
            return True
    return False


def main():
    app = QApplication(sys.argv)
    serial = get_serial()
    if serial is None:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Error)
        msgBox.setText("هناك مشكلة في استخراج الرقم التسلسلي.\nالرجاء تجربة تفعيل البرنامج بصلاحية المدير.")
        msgBox.setWindowTitle("الرقم التسلسلي")
        msgBox.exec()
    else:
        my_license = get_license(serial, artifact_id)
        main_ui = MainClass(my_license)
        lic_ui = LicenseClass(main_ui, serial)
        res = check_lic(my_license)
        if res:
            main_ui.show()
        else:
            lic_ui.show()
    app.exec_()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
