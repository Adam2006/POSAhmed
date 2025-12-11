from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QWidget,
    QLineEdit,
    QCheckBox,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QDateEdit,
    QHeaderView,
)
from datetime import datetime as dt
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QFont, QPixmap, QIcon, QCloseEvent, QIntValidator
from PyQt5.QtCore import Qt, QDate
from datetime import time

import sys, json, functools, win32print, datetime


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("app.ui", self)

        icon = QIcon("ico.png")
        self.setWindowIcon(icon)
        self.importData()
        current_date = datetime.date.today()
        current_datetime = datetime.datetime.now()
        date_string = current_date.strftime("%Y/%m/%d")
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        current_hour = current_datetime.hour
        try:
            with open("historique\data.json", "r") as f:
                self.Hdata = json.load(f)
        except:
            self.Hdata = {}
        #try:
        #    self.orderCounter = int(list(self.Hdata[date_string].keys())[-1]) + 1
        #except:
        #    self.orderCounter = 1
        if time(2, 30, 0)>time(int(datetime.datetime.now().strftime("%I")), int(datetime.datetime.now().strftime("%I")), 0)>time(12, 30, 0):
            self.orderCounter = 1
        else:
            try:
                self.orderCounter = int(list(self.Hdata[date_string].keys())[-1]) + 1
            except:
                self.orderCounter = 1
        self.btns = {}
        self.ProductBtns = {}
        self.purshaseDict = []
        self.page = 1
        self.pageNum = 0
        self.busy = False
        self.lb = QLabel()

        self.administrator = False
        self.password = "ab65"

        self.pageLabel = self.findChild(QLabel, "page")
        self.nextPage = self.findChild(QPushButton, "pushButton_3")
        self.previousPage = self.findChild(QPushButton, "pushButton_2")
        self.area = self.findChild(QScrollArea, "scrollArea")
        self.scrollArea_2 = self.findChild(QScrollArea, "scrollArea_2")
        self.Quantity = self.findChild(QPushButton, "pushButton_4")
        self.Price = self.findChild(QPushButton, "pushButton_5")
        self.Discount = self.findChild(QPushButton, "pushButton_6")
        self.editQuantityLabel = self.findChild(QLabel, "label_2")
        self.editPriceLabel = self.findChild(QLabel, "label_4")
        self.done = self.findChild(QPushButton, "pushButton_20")
        self.back = self.findChild(QPushButton, "pushButton_21")
        self.edit_type_label = self.findChild(QLabel, "label")
        self.edit_item_label = self.findChild(QLabel, "label_3")

        scroll_content = QWidget()

        self.area.setWidget(scroll_content)
        self.vbox = QVBoxLayout(scroll_content)
        self.vbox.setSpacing(10)
        self.vbox.setAlignment(Qt.AlignTop)

        scroll_content2 = QWidget()

        self.scrollArea_2.setWidget(scroll_content2)
        self.vbox2 = QVBoxLayout(scroll_content2)
        self.vbox2.setSpacing(10)
        self.vbox2.setAlignment(Qt.AlignTop)

        self._1 = self.findChild(QPushButton, "pushButton_15")
        self._2 = self.findChild(QPushButton, "pushButton_11")
        self._3 = self.findChild(QPushButton, "pushButton_9")
        self._4 = self.findChild(QPushButton, "pushButton_14")
        self._5 = self.findChild(QPushButton, "pushButton_12")
        self._6 = self.findChild(QPushButton, "pushButton_13")
        self._7 = self.findChild(QPushButton, "pushButton_8")
        self._8 = self.findChild(QPushButton, "pushButton_10")
        self._9 = self.findChild(QPushButton, "pushButton_16")
        self._0 = self.findChild(QPushButton, "pushButton_17")
        self._00 = self.findChild(QPushButton, "pushButton_18")
        self._clear = self.findChild(QPushButton, "pushButton_7")
        self._del = self.findChild(QPushButton, "pushButton_19")
        self.lst = [
            self._1,
            self._2,
            self._3,
            self._4,
            self._5,
            self._6,
            self._7,
            self._8,
            self._9,
            self._0,
            self._00,
        ]
        self.lst2 = [
            self.pushButton_23,
            self.pushButton_31,
            self.pushButton_33,
            self.pushButton_28,
            self.pushButton_29,
            self.pushButton_34,
            self.pushButton_30,
            self.pushButton_24,
            self.pushButton_32,
            self.pushButton_26,
            self.pushButton_25,
        ]
        self.suggestion = [self.pushButton_36, self.pushButton_37, self.pushButton_35]
        self._del_icon = QIcon(
            "C:/Users/romdh/Dropbox/PC/Desktop/adem/RestaurantProgram/icons/x-circle.svg"
        )
        self._clear_icon = QIcon(
            "C:/Users/romdh/Dropbox/PC/Desktop/adem/RestaurantProgram/x-square.svg"
        )
        self._del.setIcon(self._del_icon)
        self._clear.setIcon(self._clear_icon)
        self.del2.setIcon(self._del_icon)
        self.clear2.setIcon(self._clear_icon)

        self.focused = """
                                QPushButton {
                    color:aliceblue;
                    background-color: rgb(37, 37, 37);
                    border:0;
                    border-right: 2px solid rgb(93, 93, 93);
                    border-bottom: 0;
                    border-top: 2px solid  black;
                    border-left: 2px solid black;
                    border-radius:7px;
                }
                """

        self.Catgrid = QGridLayout(self.widget_4)
        self.widget_4.setLayout(self.Catgrid)
        cols = 5
        rows = len(self.data) // cols + 1
        col = 0
        self.caisse = 0
        row = 0
        lst = []
        for index, btn in enumerate(self.data):
            if self.data[btn][1] == "Active":
                if index == 0:
                    first = btn
                self.btns[btn] = QPushButton(self.widget_2)
                lst.append([self.btns[btn], btn])
                font = QFont()
                font.setPointSize(16)
                self.btns[btn].setFont(font)
                self.btns[btn].setStyleSheet(
                    f"background-color: rgb(58, 58, 58);margin:{7/rows}px;padding:{10/rows}px;color:aliceblue;"
                )
                self.btns[btn].setCursor(Qt.PointingHandCursor)
                self.btns[btn].setObjectName(btn)
                self.btns[btn].setText(btn)
                self.btns[btn].clicked.connect(functools.partial(self.clicker, btn))
                self.ProductBtns[btn] = {}
        lst.sort(key=lambda x: x[1][0], reverse=True)

        for w in lst:
            self.Catgrid.addWidget(w[0], row, col)
            col += 1
            if col == cols:
                row += 1
                col = 0

        for i in range(5):
            self.Catgrid.setColumnStretch(i, 1)
        for i in range(10):
            self.Catgrid.setRowStretch(i, 1)

        self.grid = QGridLayout(self.widget_3)

        self.widget_3.setLayout(self.grid)

        self.pushButton.hide()
        self.widget_5.hide()
        self.label_8.hide()
        self.back.hide()
        self.btn = first
        self.clicker(first)
        self.pushButton.clicked.connect(lambda: self.printReceipt())
        self.nextPage.clicked.connect(lambda: self.switchPage(1))
        self.previousPage.clicked.connect(lambda: self.switchPage(-1))
        font = QFont()
        add = QPushButton()
        add.setStyleSheet(
            "background-color: rgb(37, 37, 37);color:aliceblue;text-align: center; "
        )
        add.setMinimumHeight(60)
        add.setMaximumWidth(620)
        add.setText("Add table")
        font.setPointSize(17)
        add.setFont(font)
        self.vbox2.addWidget(add)
        add.clicked.connect(self.addTable)
        self.tables.clicked.connect(self.showTablesList)
        self.dataBtn.clicked.connect(self.showSells)
        font = QFont()
        add2 = QPushButton()
        add2.setStyleSheet(
            "background-color: rgb(37, 37, 37);color:aliceblue;text-align: center; "
        )
        add2.setMinimumHeight(60)
        add2.setMaximumWidth(620)
        add2.setText("Caisse")

        font.setPointSize(17)
        add2.setFont(font)
        self.vbox2.insertWidget(self.vbox2.count() - 1, add2)

        self.tablesDict = {}
        self.tablesDict[self.vbox2.count() - 1] = {}
        add2.clicked.connect(self.showTable)
        self.livraison = False
        self.label_10.setText(f"order N°:{self.orderCounter}")
        self.showTablesList()
        self.lb = QLabel(self.centralWidget())
        self.check = QCheckBox(self.lb)
        self.check.setText("  Livraison ?")
        font.setPointSize(18)
        self.check.setFont(font)
        self.lb.setGeometry(10, 550, 280, 60)
        self.check.setGeometry(0, 0, 200, 60)
        self.check.setStyleSheet("QCheckBox::indicator {width: 20px;height: 20px;}")
        self.lb.setStyleSheet(
            "background-color: rgb(37, 37, 37);color:aliceblue;text-align: center; border-radius:20px;"
        )
        self.totale = QLabel(self.centralWidget())
        self.totale.setText("Totale :")
        font.setPointSize(18)
        self.totale.setFont(font)
        self.totale.setGeometry(50, 480, 280, 60)
        self.totale.setStyleSheet("background-color: rgb(37, 37, 37);color:aliceblue;text-align: center; border-radius:20px;")
        self.check.stateChanged.connect(self.handle_checkbox_change)
        self.widget_3.hide()
        self.lb.hide()
        self.showMaximized()

    def showSells(self):
        def showCaisse():
            self.checkUser()
            if self.administrator:
                a = 0
                for i in range(table.rowCount()):
                    if not table.isRowHidden(i):
                        a += float(table.item(i, 2).text()[:-2])
                font.setPointSize(20)
                caisseLb.setFont(font)
                caisseLb.setText(f"Caisse: {a}dt")
                # caisseLb.raise_()
                caisseLb.setGeometry(300, 50, 400, 100)

        dialog = QDialog()
        D2 = QDialog(dialog)
        dialog.setWindowTitle("Sells")
        icon = QIcon("sell.png")
        dialog.setWindowIcon(icon)
        caisseLb = QLabel(dialog)
        label = QLabel(D2)
        Sdate = QLabel(label)
        font = QFont()
        Sorder = QLabel(label)
        t = QTableWidget(label)
        table = QTableWidget(dialog)
        liv = QLabel(label)
        caisse = QPushButton(dialog)
        caisse.setText("Caisse")
        font.setPointSize(17)
        caisse.setFont(font)
        caisse.setGeometry(750, 130, 150, 50)
        caisse.clicked.connect(showCaisse)
        LF = QLabel(dialog)
        LF.setText("from:")
        LF.setGeometry(150, 145, 100, 30)
        LF.setFont(font)
        periodF = QDateEdit(dialog)
        font.setPointSize(13)
        periodF.setFont(font)
        periodF.setGeometry(250, 145, 150, 30)

        def minimumMaximum(min):
            dates = []

            for date in self.Hdata:
                dates.append(date)
            try:
                m = dates[0]
            except:
                current_date = datetime.date.today()
                date_string = current_date.strftime("%Y/%m/%d")
                m = date_string
            if min:
                for date in dates:
                    if date < m:
                        m = date
            else:
                for date in dates:
                    if date > m:
                        m = date
            return m

        l = minimumMaximum(True)
        l1 = dt.strptime(l, "%Y/%m/%d").date()
        ls = [l1.year, l1.month, l1.day]

        h = minimumMaximum(False)
        h1 = dt.strptime(h, "%Y/%m/%d").date()
        hs = [h1.year, h1.month, h1.day]
        min_date = QDate(ls[0], ls[1], ls[2])
        max_date = QDate(hs[0], hs[1], hs[2])
        periodF.setMinimumDate(min_date)
        periodF.setMaximumDate(max_date)

        LT = QLabel(dialog)
        LT.setText("to:")
        LT.setGeometry(460, 145, 100, 30)
        LT.setFont(font)
        periodT = QDateEdit(dialog)
        font.setPointSize(13)
        periodT.setFont(font)
        periodT.setGeometry(550, 145, 150, 30)
        periodT.setDate(max_date)
        periodT.setMinimumDate(min_date)
        periodT.setMaximumDate(max_date)
        periodF.setDate(max_date)

        def handleDateChange():
            # Get the selected dates
            from_date = periodF.date()
            to_date = periodT.date()

            # Ensure that the first date is always smaller than the second date
            if from_date > to_date:
                periodF.setDate(to_date)
            if to_date < from_date:
                periodT.setDate(from_date)
            filter_table()
            label.hide()
            t.hide()

        def filter_table():
            # Get the selected date range
            date_from = periodF.date()
            date_to = periodT.date()

            for row in range(table.rowCount()):
                date_item = table.item(row, 0)
                date = QDate.fromString(date_item.text(), Qt.ISODate)

                # Check if the date falls within the specified range
                if date >= date_from and date <= date_to:
                    table.setRowHidden(row, False)
                else:
                    table.setRowHidden(row, True)
            table.sortItems(0)

        periodT.dateChanged.connect(handleDateChange)
        periodF.dateChanged.connect(handleDateChange)

        def showDesc(cell):
            self.updateHdata()

            row = cell.row()
            d = table.item(row, 0).text()
            o = table.item(row, 1).text()
            Sdate.setText("Date: " + d)
            Sdate.setGeometry(50, 0, 500, 40)
            font.setPointSize(17)
            Sdate.setFont(font)
            Sorder.setText("Order#: " + o)
            Sorder.setGeometry(550, 0, 300, 40)
            Sorder.setFont(font)
            label.show()
            label.setGeometry(0, 0, 1000, 600)
            liv.hide()
            if table.item(row, 4).text() == "oui":
                liv.show()
                liv.setText(
                    f"place:{self.Hdata[d][o][2]['place']}"
                    + " " * int(100 / (len(self.Hdata[d][o][2]["place"]) + 4))
                    + f"numero:{self.Hdata[d][o][2]['num']}"
                    + " " * int(100 / (len(self.Hdata[d][o][2]["place"]) + 4))
                    + f" price:{self.Hdata[d][o][2]['price']}dt"
                )
            font.setPointSize(14)
            liv.setFont(font)
            liv.setGeometry(50, 40, 900, 50)
            t.setColumnCount(5)
            t.setRowCount(len(self.Hdata[d][o][0]))
            t.setHorizontalHeaderLabels(
                ["product", "quantity", "price", "discount", "final price"]
            )
            t.setGeometry(0, 100, 1000, 500)
            t.setColumnWidth(0, 320)
            t.setColumnWidth(1, 100)
            t.setColumnWidth(2, 100)
            t.setColumnWidth(3, 100)
            t.setColumnWidth(4, 100)

            i = 0
            for desc in self.Hdata[d][o][0]:
                if desc["name"].split(" ")[0] == "pasta":
                    t.setColumnCount(6)
                    t.setColumnWidth(5, 250)
                    t.setItem(i, 5, QTableWidgetItem(str(desc["sauces"])))
                    t.setHorizontalHeaderLabels(
                        [
                            "product",
                            "quantity",
                            "price",
                            "discount",
                            "final price",
                            "sauces",
                        ]
                    )
                t.setItem(i, 0, QTableWidgetItem(str(desc["name"])))
                t.setItem(i, 1, QTableWidgetItem(str(desc["quantity"])))
                t.setItem(
                    i,
                    2,
                    QTableWidgetItem(
                        str(
                            float(desc["price"][:-2])
                            + float(desc["discount"].replace("dt", ""))
                        )
                        + "dt"
                    ),
                )
                t.setItem(i, 3, QTableWidgetItem(str(desc["discount"]) + "dt"))
                t.setItem(i, 4, QTableWidgetItem(str(desc["price"])))

                for j in range(t.columnCount()):
                    details_item = t.item(i, j)
                    try:
                        details_item.setTextAlignment(Qt.AlignCenter)
                    except:
                        pass
                i += 1
            # t.raise_()
            t.show()
            # Sdate.setStyleSheet("background-color:green")
            # Sorder.setStyleSheet("background-color:blue")
            # label.setStyleSheet("background-color:red")
            D2.exec_()

        dialog.setWindowModality(Qt.ApplicationModal)  # Set dialog modality

        # Create a table widget
        table.setColumnCount(5)  # Adjust the column count based on your data structure
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 200)
        table.setColumnWidth(3, 200)
        table.setColumnWidth(4, 200)
        table.itemClicked.connect(showDesc)

        table.setHorizontalHeaderLabels(
            [
                "Date",
                "Order",
                "Price",
                "Time",
                "livraison",
            ]
        )

        # Set the row count based on the total number of orders
        def count_names():
            count = 0
            data = self.Hdata

            for date in data.values():
                for num, order in date.items():
                    count += 1

            return count

        row_count = count_names()
        table.setRowCount(row_count)

        # Iterate over the data and populate the table
        row = 0

        def calculate_total_prices(row, date):
            total_prices = {}
            for number, orders in self.Hdata.items():
                total_prices[number] = {}
                for num, order_info in orders.items():
                    order_items = order_info[0]
                    total_price = 0
                    for item in order_items:
                        total_price += (
                            float(item["price"].replace("dt", "")) * item["quantity"]
                        )
                    total_prices[number][num] = total_price

            return total_prices[date][row]

        self.updateHdata()
        for date, orders in self.Hdata.items():
            for order_num, order_info in orders.items():
                time = order_info[1]
                livrason = order_info[2] != {"place": "", "num": "", "price": 0}

                # Set the date and order number in the first two columns
                table.setItem(row, 0, QTableWidgetItem(date))
                table.setItem(row, 1, QTableWidgetItem(str(order_num)))

                table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        str(
                            calculate_total_prices(order_num, date)
                            + self.Hdata[date][f"{order_num}"][2]["price"]
                        )
                        + "dt"
                    ),
                )

                table.setItem(row, 3, QTableWidgetItem(time))
                table.setItem(row, 4, QTableWidgetItem("oui" if livrason else "non"))

                for i in range(5):
                    details_item = table.item(row, i)
                    details_item.setTextAlignment(Qt.AlignCenter)
                row += 1

        table.setGeometry(0, 200, 960, self.centralWidget().height() - 200)
        filter_table()
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.show()
        dialog.showMaximized()
        dialog.exec_()

    def checkUser(self):
        dialog = QDialog()
        uic.loadUi("checkPassword.ui", dialog)
        icon = QIcon("lock.png")
        dialog.lineEdit.setEchoMode(QLineEdit.Password)
        dialog.setWindowTitle("administrator")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setWindowIcon(icon)

        def check():
            if dialog.lineEdit.text() == self.password:
                self.administrator = True
            else:
                self.administrator = False
            dialog.close()

        dialog.submit.clicked.connect(check)

        dialog.exec_()

    def upadtePurshaseDict(self):
        self.purshaseDict = []
        somme = 0 
        for i in range(self.vbox.count()):
            widget = self.vbox.itemAt(i).widget()
            quantity = widget.findChild(QLabel, "Q")
            inner_name = widget.findChild(QLabel, "N").text().lstrip()
            inner_cost = widget.findChild(QLabel, "P").text().lstrip()
            discount = widget.findChild(QLabel, "D").text().lstrip()
            realDescription = widget.children()[6].description.lstrip()
            
            somme += float(inner_cost[:-2])
            des = ""
            if inner_name.split(" ")[0] == "pasta":
                des = widget.findChild(QLabel, "S")
                des = des.text().lstrip()
            self.purshaseDict.append({})
            
            self.purshaseDict[i][inner_name, inner_cost, realDescription] = (
                int(quantity.text()[1:]),
                discount,
                des,
            )
        self.totale.setText(f"Totale: {somme}")

    def addTable(self):
        self.checkUser()
        if self.administrator:
            self.administrator = False
            font = QFont()
            add = QPushButton()
            add.setStyleSheet(
                "background-color: rgb(37, 37, 37);color:aliceblue;text-align: center; "
            )
            add.setMinimumHeight(60)
            add.setMaximumWidth(620)
            add.setText(str(self.vbox2.count() - 1))

            font.setPointSize(17)
            add.setFont(font)
            self.vbox2.insertWidget(self.vbox2.count() - 1, add)

            self.tablesDict[self.vbox2.count() - 1] = {}
            add.clicked.connect(self.showTable)

    def showTablesList(self):
        if not self.busy:
            self.lb.hide()
            self.widget_3.hide()
            self.pushButton.hide()
            self.label_10.hide()
            self.widget_8.show()
            self.label_8.hide()
            self.scrollArea_2.show()
            for index in range(self.vbox.count()):
                widget = self.vbox.itemAt(index).widget()
                self.tablesDict[self.table][index] = widget

            while self.vbox.count():
                item = self.vbox.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

    def handle_checkbox_change(self):
        state = self.check.isChecked()

        if state == True:

            def closeEvent(event):
                if event.spontaneous() and type(event) == QCloseEvent:
                    self.livraison = False
                    self.check.setCheckState(Qt.Unchecked)
                else:
                    self.livraison = True
                    self.livraisonData = {
                        "place": dialog.lineEdit.text(),
                        "num": dialog.lineEdit_2.text(),
                        "price": dialog.doubleSpinBox.value(),
                    }

            dialog = QDialog()
            uic.loadUi("livraison.ui", dialog)
            icon = QIcon("delivery.png")
            dialog.setWindowIcon(icon)
            validator = QIntValidator()
            validator.setRange(0, 99999999)
            dialog.lineEdit_2.setValidator(validator)
            dialog.setWindowFlags(
                dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint
            )
            dialog.setWindowTitle("delivery")
            dialog.closeEvent = closeEvent
            dialog.done_.clicked.connect(dialog.close)
            dialog.exec_()

    def showTable(self):
        font = QFont()
        self.label_10.show()
        self.table = self.vbox2.indexOf(self.sender()) + 1
        self.widget_8.hide()
        self.widget_3.show()
        self.label_8.show()

        self.pushButton.show()
        if self.table - 1 != 0:
            self.label_8.setText(f"Table N°:{self.table-1}")
        else:
            self.label_8.setText(f"Caisse")

            self.lb.show()

        for index, widget in self.tablesDict[self.table].items():
            self.vbox.addWidget(widget)
        self.upadtePurshaseDict()

        self.scrollArea_2.hide()

    def switchPage(self, num):
        if num == -1:
            if not (self.page <= 1):
                self.page += num
        if num == 1:
            if not (self.page >= self.pageNum):
                self.page += num

        self.clicker(self.btn)

    def importData(self):
        try:
            with open("menu.json", "r") as f:
                self.data = json.load(f)
        except:
            self.data = {}

    def updateHdata(self):
        try:
            with open("historique\data.json", "r") as f:
                self.Hdata = json.load(f)
        except:
            self.Hdata = {}

    def appendCommand(
        self,
        date,
        time,
        num,
        order,
        livraisonData={"place": "", "num": "", "price": 0},
    ):
        try:
            with open("historique\data.json", "r") as f:
                self.Hdata = json.load(f)
        except:
            self.Hdata = {}

        try:
            self.Hdata[date][num] = [order, time, livraisonData]
        except:
            self.Hdata[date] = {}
            self.Hdata[date][num] = [order, time, livraisonData]

        with open("historique\data.json", "w") as json_file:
            json.dump(self.Hdata, json_file)

    def clearProducts(self):
        global row, col
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item is not None:
                widget = item.widget()
                # remove the widget from the layout and set its parent to None
                self.grid.removeWidget(widget)
                widget.setParent(None)
        row = 0
        col = 0

    def clicker(self, btn):
        self.Tsender = ""
        self.sauces = ""
        self.meats = ""
        self.btn = btn
        self.grid.setSpacing(4)

        def label_clicked(name, cost, category, event):
            label = QPushButton()
            label.setObjectName("label")
            font = QFont()
            label.setStyleSheet("background-color: rgb(37, 37, 37);color:aliceblue;")
            label.setMinimumHeight(60)
            label.setMaximumWidth(620)

            nameLb = QLabel(label)
            nameLb.setObjectName("N")

            nameLb.setText(f"{category} {name}")

            font.setPointSize(11)
            nameLb.setFont(font)
            nameLb.setGeometry(10, 8, 150, 40)

            sauce_text = QLabel(label)
            sauce_text.setObjectName("S")
            sauce_text.setText("")
            if category == "pasta":
                self.annuler = False

                
                def closeEvent(event):
                    if event.spontaneous() and type(event) == QCloseEvent:
                        self.annuler = True
                    

                
                def ce(event):
                    if event.spontaneous() and type(event) == QCloseEvent:
                        self.annuler = True

                dialog = QDialog()

                dialog.setWindowFlags(
                    dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint
                )
                dialog.closeEvent = ce
                icon = QIcon("sauces.png")
                dialog.setWindowIcon(icon)
                uic.loadUi("pastaDialog.ui", dialog)


                def addSauce():
                    self.sauces = self.sender().text()
                    dialog.label_2.setText(self.sender().text())

                def end():
                    dialog.close()

                sauces = [
                    dialog.pushButton,
                    dialog.pushButton_2,
                    dialog.pushButton_3,
                ]
                for sauce in sauces:
                    sauce.clicked.connect(lambda: addSauce())
                dialog.done_.clicked.connect(lambda: end())
                dialog.closeEvent = closeEvent
                dialog.setWindowTitle("Sauces")
                dialog.exec_()
                if self.annuler:
                    return

                sauce_text.setText(self.sauces)
                self.sauces = ""
                font.setPointSize(7)
                sauce_text.setFont(font)
                sauce_text.setGeometry(40, 40, 250, 18)

            price = QLabel(label)
            price.setObjectName("FP")
            price.setText(cost)
            font.setPointSize(12)
            price.setFont(font)
            price.setGeometry(210, 15, 50, 20)
            price.setAlignment(Qt.AlignRight)

            recurrence = QLabel(label)
            recurrence.setText(f"×{1}")
            recurrence.setObjectName("Q")
            font.setPointSize(14)
            recurrence.setFont(font)
            recurrence.setGeometry(400, 15, 90, 20)

            finalPrice = QLabel(label)
            finalPrice.setText(cost)
            font.setPointSize(8)
            finalPrice.setObjectName("P")

            finalPrice.setFont(font)
            finalPrice.setGeometry(390, 55, 80, 20)

            def remove(label):
                
                label.close()
                self.vbox.removeWidget(label)
                self.upadtePurshaseDict()
                delete.clicked.disconnect()
            def SandwichDescription(name):
                dialog = QDialog()
                uic.loadUi("description.ui", dialog)
                def closs(): 
                    settings.description = dialog.plainTextEdit.toPlainText().replace('\n', ' ')
                    self.upadtePurshaseDict()
                    dialog.close()
                icon = QIcon("gearIcon")
                dialog.setWindowIcon(icon)
                dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                dialog.setWindowTitle("Description")

                dialog.done_.clicked.connect(closs)
                dialog.label_2.setText(name)


                dialog.exec_()
            delete = QPushButton(label)
            delete.setText("×")
            font.setPointSize(20)
            delete.setFont(font)
            delete.setGeometry(270, 10, 30, 40)
            delete.setStyleSheet("color: red;border:0;")
            delete.setCursor(Qt.PointingHandCursor)
            delete.clicked.connect(functools.partial(remove, label))

            settings = QPushButton(label)
            settings.setObjectName("L")
            settings.description = ""
            settings.setGeometry(190, 10, 30, 40)
            icon = QIcon('gear.png')
            settings.setIcon(icon)
            settings.setCursor(Qt.PointingHandCursor)
            settings.clicked.connect(functools.partial(SandwichDescription, nameLb.text()))

            discount = QLabel(label)
            discount.setText("")
            font.setPointSize(8)
            discount.setObjectName("D")
            discount.setFont(font)
            discount.setGeometry(500, 50, 80, 20)
            discount.setStyleSheet("color: red;")

            

            

            self.vbox.addWidget(label)
            self.upadtePurshaseDict()

        row = 0
        col = 0
        cols = 5
        rows = 3
        notActive = 0
        self.clearProducts()

        for index, product in enumerate(self.data[btn][0]):
            if self.data[btn][0][product][1] == "Active":
                label = QLabel()
                label.setMaximumSize(250, 80)
                pixmap = QPixmap(self.data[btn][0][product][4])
                label.setStyleSheet("background-color:rgb(37, 37, 37);")
                label.setAlignment(Qt.AlignCenter)

                label.setCursor(Qt.PointingHandCursor)

                scaled_pixmap = pixmap.scaled(
                    int(label.width()),
                    int(label.height() * 0.8),
                    aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                )
                label.setPixmap(scaled_pixmap)

                price = QLabel(label)
                price.setText("   " + str(self.data[btn][0][product][2]) + "dt")
                price.setStyleSheet(
                    "background-color:rgba(0, 0, 0, 0.9);color:aliceblue;"
                )
                price.setGeometry(-10, 0, 50, 20)

                name = QLabel(label)
                name.setText(str(product))
                name.setAlignment(Qt.AlignCenter)
                name.setStyleSheet(
                    "background-color:rgba(0, 0, 0, 0.9);color:aliceblue;"
                )
                name.setGeometry(
                    -10,
                    int(self.widget_3.height() / rows * 0.3),
                    int(self.widget_3.width() / cols) + 10,
                    name.height(),
                )

                label.mousePressEvent = functools.partial(
                    label_clicked, name.text(), price.text(), btn
                )

                for i in range(cols):
                    self.grid.setColumnMinimumWidth(
                        i, int(self.widget_3.width() / cols)
                    )
                for i in range(rows):
                    self.grid.setRowMinimumHeight(i, int(self.widget_3.height() / rows))

                minus = -1 + 15 * (self.page - 1)
                maxus = 14 + 15 * (self.page - 1)

                if minus < index <= maxus:
                    self.grid.addWidget(label, row, col)
                    col += 1
                if not (minus < index <= maxus):
                    continue

                if col == cols:
                    col = 0
                    row += 1
            else:
                notActive += 1
        self.pageNum = (((len(self.data[btn][0]) - 1) - notActive) // 14) + 1
        if self.pageNum > 1:
            self.pageLabel.show()
            self.nextPage.show()
            self.previousPage.show()
        if self.pageNum <= 1:
            self.pageLabel.hide()
            self.nextPage.hide()
            self.previousPage.hide()
        self.pageLabel.setText(f"Page: {self.page}")

    def printReceipt(self):
        # Set the text size command
        set_size_command = "\x1B\x4D\x00"  # ESC/POS command to set text size

        # Set the font command
        set_font_command = "\x1B\x21\x00"  # ESC/POS command to set font

        # Set the bold command
        bold_command = "\x1B\x45\x01"

        # Combine the commands and the ticket text
        current_date = datetime.date.today()
        date_string = current_date.strftime("%Y/%m/%d")
        current_time = datetime.datetime.now().time()
        time_string = current_time.strftime("%H:%M:%S")
        descriptions = []
        products = []
        prices = []
        repetetion = []
        items = []
        discounts = []
        for i in range(len(self.purshaseDict)):
            products.append(list(self.purshaseDict[i].keys())[0][0]+" "+list(self.purshaseDict[i].values())[0][2])
            if list(self.purshaseDict[i].values())[0][1][1:-3] == "":
                discounts.append("0")
            else:
                discounts.append(
                    list(self.purshaseDict[i].values())[0][1][1:-3].replace("dt", "")
                )
                
            

            prices.append(
                f"{float(list(self.purshaseDict[i].keys())[0][1][:-2]) - float(discounts[i])}dt"
            )
            repetetion.append(list(self.purshaseDict[i].values())[0][0])

            descriptions.append(list(self.purshaseDict[i].keys())[0][2])
        

        for i in range(len(products)):

            items.append(
                {
                    "name": products[i],
                    "quantity": repetetion[i],
                    "price": prices[i],
                    "discount": discounts[i],
                    "description": descriptions[i],
                }
            )
        if items == []:
            return
        total = 0

        if True:
            cuisine_lines = []
            cuisine_lines.append(
                f"order#:{self.orderCounter} date:{date_string} time:{time_string}\n"
            )

            for item in items:
                product_name = f'{item["quantity"]}  {item["name"]} \n {item["description"]} \n'
                cuisine_lines.append(product_name)

        if not self.livraison:
            self.appendCommand(date_string, time_string, self.orderCounter, items)
            lines = [
                "Phone: 99777197",
                f"Order#:                    {self.orderCounter}",
                f"Order Date:                {date_string}",
                f"Order Time:                {time_string}",
                "_____________________________________________",
                "Product                     Quantity     Price",
                "_____________________________________________",
                "",
            ]
        else:
            self.appendCommand(
                date_string,
                time_string,
                self.orderCounter,
                items,
                self.livraisonData,
            )
            lines = [
                "Phone: 99777197",
                f"Order#:                    {self.orderCounter}",
                f"Order Date:                {date_string}",
                f"Order Time:                {time_string}",
                f"Costumer house:",
                f"{self.livraisonData['place']}",
                f"Costumer phone:                {self.livraisonData['num']}",
                f"delivery price:                {self.livraisonData['price']}dt",
                "_____________________________________________",
                "Product                     Quantity     Price",
                "_____________________________________________",
                "",
            ]
            total += int(self.livraisonData["price"])
        for item in items:
            product_name = item["name"]
            quantity = item["quantity"]
            price = item["price"]

            product_text = ' '.join(product_name.split(' ')[0:])
            line = f"{product_text.ljust(35)}{('x'+str(quantity))}{str(price).rjust(8)}"
                
            lines.append(line)
            

        for i in range(len(products)):
            total += float(prices[i][:-2]) * int(repetetion[i])

        lines.extend(
            [
                "",
                "_______________________________________________",
                "",
                "\x1B\x21\x30" + "\x1B\x45\x01" + f"          Total: {round(total,2)}dt",
            ]
        )
        ticket_text = "\n".join(lines)
        cuisine_ticket_data = ""
        cuisine_ticket_text = "\n".join(cuisine_lines)
        cuisine_ticket_data = "\x1D\x21\x01" + "\x1D\x21\x10" + cuisine_ticket_text
        ticket_data = set_size_command + set_font_command + bold_command + ticket_text
        title_data = "\x1B\x21\x30" + "\x1B\x45\x01" + "\t  Woods \n\n"

        def print_cuisine_ticket():
            cuisine_printer = "XP-80C (copy 1)"
            hPrinter2 = win32print.OpenPrinter(cuisine_printer)
            try:
                hJob2 = win32print.StartDocPrinter(
                    hPrinter2, 1, ("Ticket", None, "RAW")
                )

                try:
                    win32print.StartPagePrinter(hPrinter2)

                    win32print.WritePrinter(
                        hPrinter2, cuisine_ticket_data.encode("utf-8"))

                    win32print.EndPagePrinter(hPrinter2)
                finally:
                    win32print.EndDocPrinter(hPrinter2)
            finally:
                win32print.ClosePrinter(hPrinter2)

            cut_ticket(cuisine_printer)

        def print_ticket():
            caisse_printer = "XP-80C (copy 1)"
            hPrinter = win32print.OpenPrinter(caisse_printer)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket", None, "RAW"))
 
                try:
                    win32print.StartPagePrinter(hPrinter)

                    # Send the ticket data to the printer
                    for i in range(self.vbox.count()):
                        a = self.vbox.itemAt(i)
                        if a:
                            b = a.widget().findChild(QLabel, "FP")
                            if b:
                                self.caisse += float(b.text()[:-2])
                    self.tablesDict[self.table] = {}
                    while self.vbox.count():
                        item = self.vbox.takeAt(0)
                        widget = item.widget()
                        if widget:
                            widget.setParent(None)
                    self.livraison = False
                    self.check.setCheckState(Qt.Unchecked)
                    win32print.WritePrinter(hPrinter, title_data.encode("utf-8"))
                    win32print.WritePrinter(hPrinter, ticket_data.encode("utf-8"))

                    
                    self.upadtePurshaseDict()

                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)

            print(ticket_data)
            cut_ticket(caisse_printer)
        
        def cut_ticket(p):
            # Send the paper cut command to the printer
            hPrinter = win32print.OpenPrinter(p)

            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cut", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)

                    # Send the paper cut command
                    cut_command = "\x1D\x56\x01"  # ESC/POS paper cut command
                    win32print.WritePrinter(hPrinter, "\n\n\n\n\n".encode("utf-8"))
                    win32print.WritePrinter(hPrinter, cut_command.encode("utf-8"))

                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)

        print_ticket()
        self.orderCounter += 1
        self.upadtePurshaseDict()
        self.updateHdata()
        print_cuisine_ticket()
        self.label_10.setText(f"order N°:{self.orderCounter}")


app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()