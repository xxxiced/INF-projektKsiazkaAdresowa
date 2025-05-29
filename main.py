from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from ui import Ui_MainWindow
from new_adress import Ui_new_adress_window
from edit_adress import Ui_edit_adress_window 
from stats import Ui_stats_window
import json, os

base_direction = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_direction, "adress.json")

class MainWindow(QMainWindow,Ui_MainWindow):
     
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.action_new.triggered.connect(self.new_adress)
        self.ui.action_delete.triggered.connect(self.delete_adress)
        self.ui.action_edit.triggered.connect(self.edit_adress)
        self.ui.action_name.triggered.connect(self.name_statistics)
        self.ui.action_surname.triggered.connect(self.surname_statistics)
        self.ui.action_city.triggered.connect(self.city_statistics)
        self.ui.searchInput.textChanged.connect(lambda: self.sort_buttons(self.ui.searchInput.text()))
        self.no_adress_selected()
        try:
            with open(json_path,"r") as f:
                adress_list = json.load(f)
        
        except (json.JSONDecodeError):
            adress_list = []
        
        for adress in adress_list:
            self.add_adress_button(adress)
    
    def no_adress_selected(self):
        self.current_adress = ""
        self.ui.name_value.setText("Nie wybrano żadnego adresu")
        self.ui.phone.hide()
        self.ui.email.hide()
        self.ui.city.hide()
        self.ui.street.hide()
        self.ui.building.hide()
        self.ui.apartment.hide()
        self.ui.phone_value.hide()
        self.ui.email_value.hide()
        self.ui.city_value.hide()
        self.ui.street_value.hide()
        self.ui.building_value.hide()
        self.ui.apartment_value.hide()

    def adress_selected(self):
        self.ui.phone.show()
        self.ui.email.show()
        self.ui.city.show()
        self.ui.street.show()
        self.ui.building.show()
        self.ui.apartment.show()
        self.ui.phone_value.show()
        self.ui.email_value.show()
        self.ui.city_value.show()
        self.ui.street_value.show()
        self.ui.building_value.show()
        self.ui.apartment_value.show()
    
    def new_adress(self):
        self.new_window = new_adress_window(self)
        self.new_window.exec_()

    def add_adress_button(self,adress):
        name_surname = f"{adress['name']}_{adress['surname']}"
        self.button = QtWidgets.QPushButton(name_surname.replace("_"," "),self.ui.scrollAreaWidgetContents)
        self.button.setMinimumSize(QtCore.QSize(0, 30))
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button.setObjectName(name_surname)
        self.button.setMaximumWidth(275)
        self.ui.verticalLayout.addWidget(self.button)
        
        def button_pressed():
            self.ui.name_value.setText(f"{name_surname}".replace("_"," "))
            self.ui.phone_value.setText(adress["phone"])
            self.ui.email_value.setText(adress["email"])
            self.ui.city_value.setText(adress["city"])
            self.ui.street_value.setText(adress["street"])
            self.ui.building_value.setText(adress["building"])
            self.ui.apartment_value.setText(adress["apartment"])
            self.adress_selected()
            self.current_adress = name_surname

        self.button.pressed.connect(button_pressed)
        

        layout = self.ui.verticalLayout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item == self.ui.spacerItem:
                layout.takeAt(i)
                break
        
        self.ui.verticalLayout.addItem(self.ui.spacerItem)

    def delete_adress(self):
        if self.current_adress == "":
            QMessageBox.information(self, "Błąd", "Nie wybrano adresu do usunięcia!")
            return
        
        try:
            with open(json_path,"r") as f:
                adress_list = json.load(f)
        except (json.JSONDecodeError):
            adress_list = []
        
        adress_list_pre_delete = adress_list

        for adress in adress_list_pre_delete:
            name_surname = f"{adress['name']}_{adress['surname']}"
            if name_surname == self.current_adress:   
                adress_list.remove(adress)   
                with open(json_path,"w") as f:
                    json.dump(adress_list,f,indent=1)
                break
        
        button = self.findChild(QtWidgets.QPushButton, self.current_adress)
        if button:
            self.ui.verticalLayout.removeWidget(button)
            button.setParent(None)
            button.deleteLater()   
        
        self.no_adress_selected()

    def edit_adress(self):
        if self.current_adress == "":
            QMessageBox.information(self, "Błąd", "Nie wybrano adresu do edycji!")
            return
        self.new_window = edit_adress_window(self, self.current_adress)
        self.new_window.exec_()
        
    def calculate_score(self, adress, search_input):
        score = 0
        adress_values = []
        for value in adress.values():
            adress_values.append(value.lower())
        search_parts = search_input.lower().split()
        for part in search_parts:
            for item in adress_values:
                if part == item:
                    score = score + 4
                elif item.startswith(part):
                    score = score + 2
                elif part in item:
                    score = score + 1
        return score
    
    def sort_buttons(self, search_input):
        try:
            with open(json_path, "r") as f:
                adress_list = json.load(f)
        except json.JSONDecodeError:
            adress_list = []
        scored_adresses = []
        for adress in adress_list:
            score = self.calculate_score(adress, search_input)
            scored_adresses.append((score,adress))
        
        scored_adresses.sort(key=lambda x: x[0], reverse=True)
        
        layout = self.ui.verticalLayout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item == self.ui.spacerItem:
               layout.takeAt(i)
               break

        while self.ui.verticalLayout.count():
            item = self.ui.verticalLayout.takeAt(0)
            widget = item.widget()
            if widget is not None and widget is not self.ui.searchInput and widget is not self.ui.spacerItem:
                widget.setParent(None)
                widget.deleteLater()
        
        self.ui.verticalLayout.removeWidget(self.ui.searchInput)
        self.ui.verticalLayout.insertWidget(0, self.ui.searchInput)
        self.ui.verticalLayout.addItem(self.ui.spacerItem)
        for score, adress in scored_adresses:
            self.add_adress_button(adress)

    def name_statistics(self):
        self.stats = stats_window("name")
        self.stats.exec_()

    def surname_statistics(self):
        self.stats = stats_window("surname")
        self.stats.exec_()

    def city_statistics(self):
        self.stats = stats_window("city")
        self.stats.exec_()



class new_adress_window(QtWidgets.QDialog,Ui_new_adress_window):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.cancel.clicked.connect(self.close)
        self.add.clicked.connect(self.add_adress)
        self.name_input.returnPressed.connect(self.surname_input.setFocus)
        self.surname_input.returnPressed.connect(self.phone_input.setFocus)
        self.phone_input.returnPressed.connect(self.email_input.setFocus)
        self.email_input.returnPressed.connect(self.city_input.setFocus)
        self.city_input.returnPressed.connect(self.street_input.setFocus)
        self.street_input.returnPressed.connect(self.building_input.setFocus)
        self.building_input.returnPressed.connect(self.apartment_input.setFocus)
        self.apartment_input.returnPressed.connect(self.add.click)
        self.cancel.setAutoDefault(False)
        self.add.setAutoDefault(False)

    def add_adress(self):
        adress = {
            "name": self.name_input.text().replace(" ", ""),
            "surname": self.surname_input.text().replace(" ", ""),
            "phone": self.phone_input.text(),
            "email": self.email_input.text().replace(" ", ""),
            "city": self.city_input.text(),
            "street": self.street_input.text(),
            "building": self.building_input.text().replace(" ", ""),
            "apartment": self.apartment_input.text().replace(" ", "")
            }
        try:
            with open(json_path,"r") as f:
                adress_list = json.load(f)
        
        except (json.JSONDecodeError):
            adress_list = []
        
        for item in adress_list:
            if item.get("name").lower() == adress["name"].lower() and item.get("surname").lower() == adress["surname"].lower():
                QMessageBox.information(self, "Błąd", "Adres już istnieje!")
                self.close()
                return
        
        adress_list.append(adress)
        with open(json_path,"w") as f:
                json.dump(adress_list,f,indent=1)

        self.main_window.add_adress_button(adress)

        self.close()

class edit_adress_window(QtWidgets.QDialog,Ui_edit_adress_window):
    def __init__(self, main_window, current_adress):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.current_adress = current_adress
        self.cancel.clicked.connect(self.close)
        self.confirm.clicked.connect(self.confirm_clicked)
        
        try:
            with open(json_path,"r") as f:
                adress_list = json.load(f)
        except (json.JSONDecodeError):
            adress_list = []

        for adress in adress_list:
            name_surname = f"{adress['name']}_{adress['surname']}"
            if name_surname == self.current_adress:   
                self.name_input.setText(adress["name"])
                self.surname_input.setText(adress["surname"])
                self.phone_input.setText(adress["phone"])
                self.email_input.setText(adress["email"])
                self.city_input.setText(adress["city"])
                self.street_input.setText(adress["street"])
                self.building_input.setText(adress["building"])
                self.apartment_input.setText(adress["apartment"])
                break
        
        self.name_input.returnPressed.connect(self.surname_input.setFocus)
        self.surname_input.returnPressed.connect(self.phone_input.setFocus)
        self.phone_input.returnPressed.connect(self.email_input.setFocus)
        self.email_input.returnPressed.connect(self.city_input.setFocus)
        self.city_input.returnPressed.connect(self.street_input.setFocus)
        self.street_input.returnPressed.connect(self.building_input.setFocus)
        self.building_input.returnPressed.connect(self.apartment_input.setFocus)
        self.apartment_input.returnPressed.connect(self.confirm.click)
        self.cancel.setAutoDefault(False)
        self.confirm.setAutoDefault(False)

    def confirm_clicked(self):
        new_adress = {
            "name": self.name_input.text().replace(" ", ""),
            "surname": self.surname_input.text().replace(" ", ""),
            "phone": self.phone_input.text(),
            "email": self.email_input.text().replace(" ", ""),
            "city": self.city_input.text(),
            "street": self.street_input.text(),
            "building": self.building_input.text().replace(" ", ""),
            "apartment": self.apartment_input.text().replace(" ", "")
            }
        old_adress = self.current_adress
        
        try:
            with open(json_path,"r") as f:
                adress_list = json.load(f)
        except (json.JSONDecodeError):
            adress_list = []
        
        adress_list_pre_delete = adress_list

        for adress in adress_list_pre_delete:
            name_surname = f"{adress['name']}_{adress['surname']}"
            if name_surname == old_adress:   
                old_adress_value = adress
                adress_list.remove(adress)
                break   
        
        for item in adress_list:
            if item.get("name").lower() == new_adress["name"].lower() and item.get("surname").lower() == new_adress["surname"].lower():
                QMessageBox.information(self, "Błąd", "Adres już istnieje!")
                self.close()
                return
        
        adress_list.append(new_adress)
        
        self.main_window.add_adress_button(new_adress)
        
        button = self.main_window.findChild(QtWidgets.QPushButton, old_adress)
        
        if button:
            self.main_window.ui.verticalLayout.removeWidget(button)
            button.setParent(None)
            button.deleteLater()   
        
        self.main_window.no_adress_selected()
        
        with open(json_path,"w") as f:
                json.dump(adress_list,f,indent=1)

        self.close()

class stats_window(QtWidgets.QDialog,Ui_stats_window):
    def __init__(self, stat):
        super().__init__()
        self.setupUi(self)
        self.stat = stat
        self.load_sort_statistics()
        self.display_stats(self.final_stat_list)
        self.leave.clicked.connect(self.close)
        name = self.name
        if stat == "name":
            self.name.setText("Imię")
        if stat == "surname":
            self.name.setText("Nazwisko")
        if stat == "city":
            self.name.setText("Miasto")

    def load_sort_statistics(self):
        try:
            with open(json_path, "r") as f:
                adress_list = json.load(f)
        except (json.JSONDecodeError):
            adress_list = []
    
        stat_list = []
        stat = self.stat

        for adress in adress_list:
            stat_list.append(adress[stat])
        
        self.final_stat_list = []

        for item in stat_list:
            found = False
            for entry in self.final_stat_list:
                if entry[0] == item:
                    entry[1] = entry[1] + 1
                    found = True
                    break
            if not found:
                self.final_stat_list.append([item, 1])
        
        i = 0

        for item in self.final_stat_list:
            if item[0] == "":
                self.final_stat_list[i][0] = "-"
                break
            i = i+1

        self.final_stat_list.sort(key=lambda x: x[1], reverse=True)

    def display_stats(self, final_stat_list):
        for item in final_stat_list:
            name = item[0]
            count = item[1]

            layout = QtWidgets.QHBoxLayout()

            name_label = QtWidgets.QLabel()
            name_label.setText(str(name))
            name_label.setMinimumSize(QtCore.QSize(81, 31))
            name_label.setMaximumSize(QtCore.QSize(81, 31))

            count_label = QtWidgets.QLabel()
            count_label.setText(str(count))
            count_label.setMinimumSize(QtCore.QSize(81, 31))
            count_label.setMaximumSize(QtCore.QSize(81, 31))

            layout.addWidget(name_label)
            layout.addWidget(count_label)

            self.verticalLayout.addLayout(layout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)




app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec()