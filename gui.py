# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
# read boolean value from checkbox
# test for data saved in correct location
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDate, QSettings
from PyQt5.QtWidgets import QMessageBox
from download import Download
from dateutil.parser import parse
from datetime import date, datetime, timedelta
from os import path

class Ui_Dialog(object):
    my_settings = QSettings("settings.ini", QSettings.IniFormat)
    dir = ""
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(649, 463)
        self.from_date = QtWidgets.QCalendarWidget(Dialog)
        self.from_date.setGeometry(QtCore.QRect(30, 40, 310, 183))
        self.from_date.setMinimumSize(QtCore.QSize(310, 183))
        self.from_date.setObjectName("from_date")
        self.from_date.clicked[QDate].connect(self.from_show_date)

        self.to_date = QtWidgets.QCalendarWidget(Dialog)
        self.to_date.setGeometry(QtCore.QRect(350, 40, 310, 183))
        self.to_date.setObjectName("to_date")
        self.to_date.clicked[QDate].connect(self.to_show_date)

        self.nse_zipped = QtWidgets.QCheckBox(Dialog)
        self.nse_zipped.setGeometry(QtCore.QRect(80, 240, 81, 17))
        self.nse_zipped.setObjectName("nse_zipped")

        self.headless = QtWidgets.QCheckBox(Dialog)
        self.headless.setGeometry(QtCore.QRect(80, 260, 70, 17))
        self.headless.setObjectName("headless")

        self.only_today = QtWidgets.QCheckBox(Dialog)
        self.only_today.setGeometry(QtCore.QRect(470, 260, 81, 17))
        self.headless.setObjectName("only_today")

        self.dont_download_bhavcopy = QtWidgets.QCheckBox(Dialog)
        self.dont_download_bhavcopy.setGeometry(QtCore.QRect(260, 260, 180, 17))
        self.dont_download_bhavcopy.setObjectName("dont_download_bhavcopy")

        self.bse_zipped = QtWidgets.QCheckBox(Dialog)
        self.bse_zipped.setGeometry(QtCore.QRect(470, 240, 81, 16))
        self.bse_zipped.setObjectName("bse_zipped")

        self.include_weekend = QtWidgets.QCheckBox(Dialog)
        self.include_weekend.setGeometry(QtCore.QRect(260, 240, 131, 17))
        self.include_weekend.setObjectName("include_weekend")

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 12, 51, 21))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(350, 12, 47, 21))
        self.label_2.setObjectName("label_2")

        self.Submit = QtWidgets.QPushButton(Dialog)
        self.Submit.setGeometry(QtCore.QRect(290, 310, 75, 23))
        self.Submit.setObjectName("Submit")
        self.Submit.clicked.connect(self.on_submit)

        self.from_date_label = QtWidgets.QLabel(Dialog)
        self.from_date_label.setGeometry(QtCore.QRect(80, 13, 81, 20))
        self.from_date_label.setText("")
        self.from_date_label.setObjectName("from_date_label")

        self.to_date_label = QtWidgets.QLabel(Dialog)
        self.to_date_label.setGeometry(QtCore.QRect(380, 12, 151, 21))
        self.to_date_label.setText("")
        self.to_date_label.setObjectName("to_date_label")

        self.select_folder = QtWidgets.QPushButton(Dialog)
        self.select_folder.setGeometry(QtCore.QRect(50, 310, 41, 23))
        self.select_folder.setObjectName("select_folder")
        self.select_folder.clicked.connect(self.sel_folder)

        self.select_folder.setObjectName("select_folder")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 310, 31, 21))
        self.label_3.setObjectName("label_3")

        self.selected_folder_path = QtWidgets.QTextEdit(Dialog)
        self.selected_folder_path.setGeometry(QtCore.QRect(92, 310, 191, 31))
        self.selected_folder_path.setObjectName("selected_folder_path")

        self.IndicesSource = QtWidgets.QComboBox(Dialog)
        self.IndicesSource.setGeometry(QtCore.QRect(260, 280, 90, 20))
        self.IndicesSource.setObjectName("IndicesSource")
        self.IndicesSource.addItem("")
        self.IndicesSource.addItem("")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def sel_folder(self):
        self.fileDialog = QtWidgets.QFileDialog()
        self.fileDialog.setGeometry(QtCore.QRect(50, 310, 41, 23))
        self.fileDialog.setObjectName("select 2 folder")
        # directory only
        self.fileDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        # just list mode is quite sufficient for choosing a diectory
        self.fileDialog.setViewMode(QtWidgets.QFileDialog.List)
        # only want to to show directories
        self.fileDialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)

        if not self.fileDialog.exec_():
            return
        Ui_Dialog.dir = self.fileDialog.selectedFiles()[0]
        self.selected_folder_path.clear()
        self.selected_folder_path.insertPlainText(Ui_Dialog.dir)
        Ui_Dialog.my_settings.setValue("save_folder_path", Ui_Dialog.dir)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.nse_zipped.setText(_translate("Dialog", " Nse zipped?"))
        self.headless.setText(_translate("Dialog", " Headless?"))
        self.only_today.setText(_translate("Dialog", " Only Today?"))
        self.dont_download_bhavcopy.setText(_translate("Dialog", " Don't download bhavcopy"))
        self.bse_zipped.setText(_translate("Dialog", "Bse Zipped?"))
        self.include_weekend.setText(_translate("Dialog", "Include Weekend"))
        self.label.setText(_translate("Dialog", "From"))
        self.label_2.setText(_translate("Dialog", "To"))
        self.Submit.setText(_translate("Dialog", "Submit"))
        self.select_folder.setText(_translate("Dialog", "Folder"))
        self.label_3.setText(_translate("Dialog", "Select Folder"))
        self.IndicesSource.setItemText(0, _translate("Dialog", "Nse"))
        self.IndicesSource.setItemText(1, _translate("Dialog", "Moneycontrol"))

    def from_show_date(self, date1):
        self.from_date_label.setText(date1.toString())

    def to_show_date(self, date1):
        self.to_date_label.setText(date1.toString())
        to_date = datetime.strptime(date1.toString("dd-MMM-yyyy"), '%d-%b-%Y').date()
        if to_date.isoweekday() in {5, 6, 7}:
            next_from_date = to_date + timedelta(days=8-to_date.isoweekday())
        else:
            next_from_date = to_date + timedelta(days=1)
        Ui_Dialog.my_settings.setValue("from_date", next_from_date.strftime("%d-%b-%Y"))
        if next_from_date.isoweekday() in {5, 6, 7}:
            next_to_date = next_from_date + timedelta(days=8-to_date.isoweekday())
        else:
            next_to_date = next_from_date + timedelta(days=1)
        Ui_Dialog.my_settings.setValue("to_date", next_to_date.strftime("%d-%b-%Y"))

    def disable_widgets_during_process(self, value):
        self.Submit.setEnabled(value)
        self.select_folder.setEnabled(value)
        self.selected_folder_path.setEnabled(value)
        self.from_date.setEnabled(value)
        self.to_date.setEnabled(value)
        self.nse_zipped.setEnabled(value)
        self.bse_zipped.setEnabled(value)
        self.include_weekend.setEnabled(value)
        self.IndicesSource.setEnabled(value)
        self.headless.setEnabled(value)
        self.only_today.setEnabled(value)
        self.dont_download_bhavcopy.setEnabled(value)

        self.Submit.repaint()
        self.select_folder.repaint()
        self.selected_folder_path.repaint()
        self.from_date.repaint()
        self.to_date.repaint()
        self.nse_zipped.repaint()
        self.bse_zipped.repaint()
        self.include_weekend.repaint()
        self.IndicesSource.repaint()
        self.headless.repaint()
        self.only_today.repaint()
        self.dont_download_bhavcopy.repaint()

    def check_for_invalid_data(self):
        complete = True
        if self.from_date_label.text().strip() == "" \
                or self.selected_folder_path.toPlainText().strip() == "" \
                or self.to_date_label.text().strip() == "":
            msg = QMessageBox()
            msg.setText("Some fields are empty")
            msg.exec_()
            complete = False

        return complete

    def on_submit(self):
        self.disable_widgets_during_process(False)
        if not self.check_for_invalid_data():
            self.disable_widgets_during_process(True)
            return
        Ui_Dialog.my_settings.setValue("nse_zipped", int(self.nse_zipped.isChecked()))
        Ui_Dialog.my_settings.setValue("bse_zipped", int(self.bse_zipped.isChecked()))
        Ui_Dialog.my_settings.setValue("include_weekend", int(self.include_weekend.isChecked()))
        Ui_Dialog.my_settings.setValue("headless", int(self.headless.isChecked()))
        Ui_Dialog.my_settings.setValue("dont_download_bhavcopy", int(self.dont_download_bhavcopy.isChecked()))
        Ui_Dialog.my_settings.setValue("only_today", int(self.only_today.isChecked()))
        Ui_Dialog.my_settings.setValue("indices_source", int(self.IndicesSource.currentIndex()))
        Ui_Dialog.my_settings.sync()

        d = Download(self.nse_zipped.isChecked(), self.nse_zipped.isChecked(),
                     self.include_weekend.isChecked(), self.selected_folder_path.toPlainText(),
                     self.headless.isChecked(), self.only_today.isChecked(),
                     self.dont_download_bhavcopy.isChecked(),
                     str(self.IndicesSource.currentText()))

        d.download_data(parse(self.from_date_label.text()).date(), parse(self.to_date_label.text()).date())

        self.disable_widgets_during_process(True)

    def load_settings(self):
        if path.exists("settings.ini"):
            self.from_date_label.setText(parse(Ui_Dialog.my_settings.value("from_date")).strftime("%d-%b-%Y"))
            self.to_date_label.setText(parse(Ui_Dialog.my_settings.value("to_date")).strftime("%d-%b-%Y"))

            Ui_Dialog.dir = Ui_Dialog.my_settings.value("save_folder_path")
            self.selected_folder_path.insertPlainText(Ui_Dialog.dir)

            self.nse_zipped.setChecked(int(Ui_Dialog.my_settings.value("nse_zipped")))

            self.bse_zipped.setChecked(int(Ui_Dialog.my_settings.value("bse_zipped")))
            self.include_weekend.setChecked(int(Ui_Dialog.my_settings.value("include_weekend")))

            self.headless.setChecked(int(Ui_Dialog.my_settings.value("headless")))
            self.dont_download_bhavcopy.setChecked(int(Ui_Dialog.my_settings.value("dont_download_bhavcopy")))
            self.only_today.setChecked(int(Ui_Dialog.my_settings.value("only_today")))
            self.IndicesSource.setCurrentIndex(int(Ui_Dialog.my_settings.value("indices_source")))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    ui.load_settings()
    Dialog.show()
    sys.exit(app.exec_())