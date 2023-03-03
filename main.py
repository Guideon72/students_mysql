import sys
import sqlite3
import mysql.connector
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QToolBar,
    QStatusBar,
    QMessageBox,
)


class ExtDatabaseConnection:
    def __init__(
        self,
        host="localhost",
        user="PyUser",
        password="JHu5VdbfrPikXTucboxQ",
        database="school",
    ):
        # self.base = Path(__file__).parent / "data"
        # self.db_path = Path(self.base / database_file)
        self.host = host
        self.user = user
        self.password = password
        self.db = database

    def connect(self):
        db_connection = mysql.connector.connect(
            host=self.host, user=self.user, password=self.password, database=self.db
        )
        return db_connection


# Create a Main Window; required for any PyQt app
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Mangement System")
        self.setMinimumSize(640, 480)

        self.db = ExtDatabaseConnection()

        # Create file path objects for db and icons
        basepath = Path(Path(__file__).parent)
        add_icon_path = Path(basepath / "icons" / "add.png")
        search_icon_path = Path(basepath / "icons" / "search.png")

        # Add File/Add Student menu item to the menu bar
        file_menu_item = self.menuBar().addMenu("&File")
        add_student_action = QAction(QIcon(str(add_icon_path)), "Add Student", self)
        add_student_action.triggered.connect(self.insert_student)
        file_menu_item.addAction(add_student_action)

        # Add Edit/Search file menu items to the menu bar
        edit_menu_item = self.menuBar().addMenu("&Edit")
        find_student_action = QAction(QIcon(str(search_icon_path)), "Search", self)
        find_student_action.triggered.connect(self.find_student)
        edit_menu_item.addAction(find_student_action)

        # Add Help file menu item to the menu bar
        help_menu_item = self.menuBar().addMenu("&Help")
        get_help_action = QAction("About", self)
        get_help_action.triggered.connect(self.about)
        help_menu_item.addAction(get_help_action)

        # Build table for student data display
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "NAME", "COURSE", "PHONE"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.load_data()

        # Add and configure a Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(find_student_action)

        # Add and configure a Status Bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Add buttons to status bar when a table item is selected
        self.table.cellClicked.connect(self.cell_clicked)

    # Load/reload the table data from our database
    def load_data(self):
        try:
            connection = self.db.connect()
            curs = connection.cursor()
            curs.execute("SELECT * FROM students")
            results = curs.fetchall()

            self.table.setRowCount(0)  # prevents duplicating data
            for row_num, student in enumerate(results):
                self.table.insertRow(row_num)
                for col_num, data in enumerate(student):
                    self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            curs.close()
            connection.close()
        except sqlite3.OperationalError:
            print("Invalid database passed in")
            sys.exit()

    # Trigger the add student dialog box
    def insert_student(self):
        dialog = InsertDialog(self.load_data, self.db)
        dialog.exec()

    # Trigger the student search dialog box
    def find_student(self):
        dialog = FindDialog(self.table, self.db)
        dialog.exec()

    def cell_clicked(self):
        # Prevent buttons from duplicating each time
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
        # Set up Edit button to show when clicking a cell
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        # Set up Delete button to show when clicking a cell
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def edit(self):
        edit_dialog = EditDialog(self.load_data, self.table, self.db)
        edit_dialog.exec()

    def delete(self):
        delete_dialog = DeleteDialog(self.load_data, self.table, self.db)
        delete_dialog.exec()

    def about(self):
        about_dialog = AboutDialog()
        about_dialog.exec()


# Create a dialog window for adding students to our database
class InsertDialog(QDialog):
    def __init__(self, reload, db):
        super().__init__()
        self.setWindowTitle("Insert Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Implement the load_data function from the /
        # target MainWindow object in order to refresh data later
        self.load_data = reload

        self.db = db

        layout = QVBoxLayout()

        # Set up student name field
        stdnt_name = QLabel("Name")
        self.stdnt_edit_line = QLineEdit()
        self.stdnt_edit_line.setPlaceholderText("Name")
        layout.addWidget(stdnt_name)
        layout.addWidget(self.stdnt_edit_line)

        # Setup class name combo box
        class_name = QLabel("Class")
        self.class_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.class_name.addItems(courses)
        layout.addWidget(class_name)
        layout.addWidget(self.class_name)

        # Set up student mobile number field
        phone_num = QLabel("Phone")
        self.phone_edit_line = QLineEdit()
        self.phone_edit_line.setPlaceholderText("Mobile number")
        layout.addWidget(phone_num)
        layout.addWidget(self.phone_edit_line)

        # Set up the Submit button
        submit = QPushButton("Submit Student")
        submit.clicked.connect(self.add_student)
        layout.addWidget(submit)

        # Displays the layout
        self.setLayout(layout)

    def add_student(self):
        connection = self.db.connect()

        name = self.stdnt_edit_line.text()
        course = self.class_name.itemText(self.class_name.currentIndex())
        phone = self.phone_edit_line.text()
        curs = connection.cursor()
        curs.execute(
            "INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
            (
                name,
                course,
                phone,
            ),
        )
        connection.commit()
        curs.close()
        connection.close()
        self.load_data()
        self.close()


# Create a dialog window for searching our database for any students with a given name
class FindDialog(QDialog):
    def __init__(self, mwtable, db):
        super().__init__()
        self.search_table = mwtable
        self.db = db

        self.setWindowTitle("Find Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Set up student name field
        stdnt_name = QLabel("Name")
        self.stdnt_search_line = QLineEdit()
        self.stdnt_search_line.setPlaceholderText("Find Name")
        layout.addWidget(stdnt_name)
        layout.addWidget(self.stdnt_search_line)

        # Set up the Search button
        search = QPushButton("Find Student")
        search.clicked.connect(self.find_student)
        layout.addWidget(search)

        # Displays the layout
        self.setLayout(layout)

    def find_student(self):
        # Searches the displayed table; NOT the database. Does not need a connection
        name = self.stdnt_search_line.text()

        # Locate all records in table that match the query paramaters
        items = self.search_table.findItems(name, Qt.MatchFlag.MatchStartsWith)

        # clear current selection.
        self.search_table.setCurrentItem(None)

        # Identify each valid result and higlighting
        for item in items:
            # print(item.text())
            self.search_table.item(item.row(), 1).setSelected(True)

        self.close()


class EditDialog(QDialog):
    def __init__(self, reload, table, db):
        super().__init__()
        self.setWindowTitle("Update Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Implement the load_data function from the /
        # target MainWindow object in order to refresh data later
        self.load_data = reload

        self.mw_table = table
        self.db = db

        # Get the line index for the currently selected row
        idx = self.mw_table.currentRow()
        self.student_id = self.mw_table.item(idx, 0).text()
        student_name = self.mw_table.item(idx, 1).text()
        course_name = self.mw_table.item(idx, 2).text()
        mobile_num = self.mw_table.item(idx, 3).text()

        layout = QVBoxLayout()

        # Set up student name field
        stdnt_name = QLabel("Name")
        self.stdnt_edit_line = QLineEdit(student_name)
        layout.addWidget(stdnt_name)
        layout.addWidget(self.stdnt_edit_line)

        # Setup class name combo box

        class_name = QLabel("Class")
        self.class_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.class_name.addItems(courses)
        self.class_name.setCurrentText(course_name)
        layout.addWidget(class_name)
        layout.addWidget(self.class_name)

        # Set up student mobile number field
        phone_num = QLabel("Phone")
        self.phone_edit_line = QLineEdit(mobile_num)
        self.phone_edit_line.setPlaceholderText("Mobile number")
        layout.addWidget(phone_num)
        layout.addWidget(self.phone_edit_line)

        # Set up the Submit button
        submit = QPushButton("Update Student Record")
        submit.clicked.connect(self.update_student)
        layout.addWidget(submit)

        # Displays the layout
        self.setLayout(layout)

    def update_student(self):
        connection = self.db.connect()
        curs = connection.cursor()
        curs.execute(
            "UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
            (
                self.stdnt_edit_line.text(),
                self.class_name.itemText(self.class_name.currentIndex()),
                self.phone_edit_line.text(),
                self.student_id,
            ),
        )
        connection.commit()
        curs.close()
        connection.close()
        self.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self, reload, table, db):
        super().__init__()
        self.setWindowTitle("Delete Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        self.reload = reload
        self.db = db

        self.mw_table = table

        layout = QGridLayout()

        # Set up the Submit button
        msg = QLabel("Are you sure you want to delete this record?")

        confirmation = QPushButton("Yes")
        confirmation.clicked.connect(self.delete_record)

        cancel_action = QPushButton("No")
        cancel_action.clicked.connect(self.close)

        layout.addWidget(msg, 0, 0, 1, 2)
        layout.addWidget(confirmation, 1, 0)
        layout.addWidget(cancel_action, 1, 1)

        # Displays the layout
        self.setLayout(layout)

    def delete_record(self):
        # Get the line index and student ID for the currently selected row
        idx = self.mw_table.currentRow()
        student_id = self.mw_table.item(idx, 0).text()

        # connection = sqlite3.connect(self.db)
        connection = self.db.connect()
        curs = connection.cursor()
        curs.execute(
            "DELETE FROM students WHERE id = %s",
            (student_id,),
        )
        connection.commit()
        curs.close()
        connection.close()
        self.reload()
        self.close()

        # Add succes message box
        success_widget = QMessageBox()
        success_widget.setWindowTitle("Success")
        success_widget.setText("Record was deleted successfully.")
        success_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        Written as part of The Python MegaCourse from Ardit Sulce.
        Feel free to modify and reuse this app for your own learning.
        Written by Eric Snyder
        2023
        """
        self.setText(content)


def main():
    app = QApplication(sys.argv)
    sms = MainWindow()
    sms.show()
    sms.load_data()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
