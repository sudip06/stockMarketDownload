from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDate, QSettings
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QTextEdit, QComboBox, QCalendarWidget
from os import path
from dateutil.parser import parse
from datetime import date, datetime, timedelta
from download import Download

class Ui_Dialog(object):
    my_settings = QSettings("settings.ini", QSettings.IniFormat)
    dir = ""
    
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 600)

        # Main vertical layout
        main_layout = QVBoxLayout(Dialog)

        # Date selection layout
        date_layout = QHBoxLayout()
        self.from_date = QCalendarWidget()
        self.from_date.setObjectName("from_date")
        self.from_date.clicked[QDate].connect(self.from_show_date)
        date_layout.addWidget(self.from_date)

        self.to_date = QCalendarWidget()
        self.to_date.setObjectName("to_date")
        self.to_date.clicked[QDate].connect(self.to_show_date)
        date_layout.addWidget(self.to_date)

        main_layout.addLayout(date_layout)

        # Labels for selected dates
        from_date_label_layout = QHBoxLayout()
        self.label = QLabel("From")
        from_date_label_layout.addWidget(self.label)
        self.from_date_label = QLabel("")
        from_date_label_layout.addWidget(self.from_date_label)

        to_date_label_layout = QHBoxLayout()
        self.label_2 = QLabel("To")
        to_date_label_layout.addWidget(self.label_2)
        self.to_date_label = QLabel("")
        to_date_label_layout.addWidget(self.to_date_label)

        main_layout.addLayout(from_date_label_layout)
        main_layout.addLayout(to_date_label_layout)

        # Checkboxes layout
        checkbox_layout = QVBoxLayout()
        
        self.nse_zipped = QCheckBox("Nse zipped?")
        checkbox_layout.addWidget(self.nse_zipped)

        self.bse_zipped = QCheckBox("Bse Zipped?")
        checkbox_layout.addWidget(self.bse_zipped)

        self.include_weekend = QCheckBox("Include Weekend")
        checkbox_layout.addWidget(self.include_weekend)

        self.headless = QCheckBox("Headless?")
        checkbox_layout.addWidget(self.headless)

        self.dont_download_indices = QCheckBox("Don't download indices")
        checkbox_layout.addWidget(self.dont_download_indices)

        self.only_today = QCheckBox("Only Today?")
        checkbox_layout.addWidget(self.only_today)

        self.dont_download_bhavcopy = QCheckBox("Don't download bhavcopy")
        checkbox_layout.addWidget(self.dont_download_bhavcopy)

        main_layout.addLayout(checkbox_layout)

        # Folder selection layout
        folder_layout = QHBoxLayout()
        self.select_folder = QPushButton("Select Folder")
        self.select_folder.setObjectName("select_folder")
        self.select_folder.clicked.connect(self.sel_folder)
        folder_layout.addWidget(self.select_folder)

        self.selected_folder_path = QTextEdit()
        self.selected_folder_path.setMaximumHeight(40)
        folder_layout.addWidget(self.selected_folder_path)

        main_layout.addLayout(folder_layout)

        # Indices source combo box
        indices_layout = QHBoxLayout()
        self.IndicesSource = QComboBox()
        indices_layout.addWidget(self.IndicesSource)
        self.IndicesSource.addItem("Nse")
        self.IndicesSource.addItem("Moneycontrol")
        self.IndicesSource.addItem("Nsepython")
        self.IndicesSource.addItem("YahooFinance")

        main_layout.addLayout(indices_layout)

        # Submit button
        self.Submit = QPushButton("Submit")
        self.Submit.setObjectName("Submit")
        self.Submit.clicked.connect(self.on_submit)
        main_layout.addWidget(self.Submit)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Stock Market Downloader"))

    def sel_folder(self):
        self.fileDialog = QtWidgets.QFileDialog()
        self.fileDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        self.fileDialog.setViewMode(QtWidgets.QFileDialog.List)
        self.fileDialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)

        if not self.fileDialog.exec_():
            return
        Ui_Dialog.dir = self.fileDialog.selectedFiles()[0]
        self.selected_folder_path.clear()
        self.selected_folder_path.insertPlainText(Ui_Dialog.dir)
        # Save the selected folder path to settings
        Ui_Dialog.my_settings.setValue("save_folder_path", Ui_Dialog.dir)
        Ui_Dialog.my_settings.sync()  # Ensure the setting is saved immediately

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.nse_zipped.setText(_translate("Dialog", " Nse zipped?"))
        self.headless.setText(_translate("Dialog", " Headless?"))
        self.dont_download_indices.setText(_translate("Dialog", "Don't download indices"))
        self.only_today.setText(_translate("Dialog", " Only Today?"))
        self.dont_download_bhavcopy.setText(_translate("Dialog", " Don't download bhavcopy"))
        self.bse_zipped.setText(_translate("Dialog", "Bse Zipped?"))
        self.include_weekend.setText(_translate("Dialog", "Include Weekend"))
        self.label.setText(_translate("Dialog", "From"))
        self.label_2.setText(_translate("Dialog", "To"))
        self.Submit.setText(_translate("Dialog", "Submit"))
        self.select_folder.setText(_translate("Dialog", "Select Folder"))  # Updated button text
        self.IndicesSource.setItemText(0, _translate("Dialog", "Nse"))
        self.IndicesSource.setItemText(1, _translate("Dialog", "Moneycontrol"))
        self.IndicesSource.setItemText(2, _translate("Dialog", "Nsepython"))
        self.IndicesSource.setItemText(3, _translate("Dialog", "YahooFinance"))


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
        self.dont_download_indices.setEnabled(value)
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
        self.dont_download_indices.repaint()
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
        Ui_Dialog.my_settings.setValue("dont_download_indices", int(self.dont_download_indices.isChecked()))
        Ui_Dialog.my_settings.setValue("dont_download_bhavcopy", int(self.dont_download_bhavcopy.isChecked()))
        Ui_Dialog.my_settings.setValue("only_today", int(self.only_today.isChecked()))
        Ui_Dialog.my_settings.setValue("indices_source", int(self.IndicesSource.currentIndex()))
        Ui_Dialog.my_settings.sync()

        d = Download(self.nse_zipped.isChecked(), self.nse_zipped.isChecked(),
                        self.include_weekend.isChecked(), self.selected_folder_path.toPlainText(),
                        self.headless.isChecked(), self.dont_download_indices.isChecked(),
                        self.only_today.isChecked(), self.dont_download_bhavcopy.isChecked(),
                        str(self.IndicesSource.currentText()))

        d.download_data(parse(self.from_date_label.text()).date(), parse(self.to_date_label.text()).date())

        self.disable_widgets_during_process(True)

    def load_settings(self):
        if path.exists("settings.ini"):
            self.from_date_label.setText(parse(Ui_Dialog.my_settings.value("from_date")).strftime("%d-%b-%Y"))
            self.to_date_label.setText(parse(Ui_Dialog.my_settings.value("to_date")).strftime("%d-%b-%Y"))

            Ui_Dialog.dir = Ui_Dialog.my_settings.value("save_folder_path", "")
            self.selected_folder_path.setPlainText(Ui_Dialog.dir)

            self.nse_zipped.setChecked(int(Ui_Dialog.my_settings.value("nse_zipped", 0)))

            self.bse_zipped.setChecked(int(Ui_Dialog.my_settings.value("bse_zipped", 0)))
            self.include_weekend.setChecked(int(Ui_Dialog.my_settings.value("include_weekend", 0)))

            self.headless.setChecked(int(Ui_Dialog.my_settings.value("headless", 0)))
            self.dont_download_indices.setChecked(int(Ui_Dialog.my_settings.value("dont_download_indices", 0)))
            self.dont_download_bhavcopy.setChecked(int(Ui_Dialog.my_settings.value("dont_download_bhavcopy", 0)))
            self.only_today.setChecked(int(Ui_Dialog.my_settings.value("only_today", 0)))
            self.IndicesSource.setCurrentIndex(int(Ui_Dialog.my_settings.value("indices_source", 0)))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    ui.load_settings()
    Dialog.show()
    sys.exit(app.exec_())