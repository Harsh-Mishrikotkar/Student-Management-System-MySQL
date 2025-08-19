from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
     QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
     QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3

class DatabaseConnection:
    def __init__(self, databaseFile="database.db"):
        self.databaseFile = databaseFile
        
    def connect(self):
        connection = sqlite3.connect(self.databaseFile)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        fileMenuItem = self.menuBar().addMenu("&File")
        helpMenuItem = self.menuBar().addMenu("&Help")
        editMenuItem = self.menuBar().addMenu("&Edit")

        addStudentAction = QAction(QIcon("icons/add.png"), "Add Student", self)
        addStudentAction.triggered.connect(self.insert)
        fileMenuItem.addAction(addStudentAction)

        aboutAction = QAction("About", self)
        helpMenuItem.addAction(aboutAction)
        aboutAction.triggered.connect(self.about)

        searchAction = QAction(QIcon("icons/search.png"), "Search", self)
        editMenuItem.addAction(searchAction)
        searchAction.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Course", "Mobile"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(addStudentAction)
        toolbar.addAction(searchAction)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.table.cellClicked.connect(self.clickedCell)

    def clickedCell(self):
        editButton = QPushButton("Edit")
        editButton.clicked.connect(self.edit)
        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for i in children:
                self.statusBar.removeWidget(i)

        
        self.statusBar.addWidget(editButton)
        self.statusBar.addWidget(deleteButton)
    
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog(self)
        dialog.exec()
    
    def LoadTable(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for rowNumber, rowData in enumerate(result):
            self.table.insertRow(rowNumber)
            for columnNumber, data in enumerate(rowData):
                self.table.setItem(rowNumber, columnNumber, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = insertDialog(self)
        dialog.exec()

    def search(self):
        dialog = searchDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()
class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Student data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.studentId = mainWindow.table.item(mainWindow.table.currentRow(), 0).text()

        index = mainWindow.table.currentRow()
        studentName = mainWindow.table.item(index, 1).text()
        self.studentName = QLineEdit(studentName)
        self.studentName.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.studentName)
        
        courseName = mainWindow.table.item(index, 2).text()
        self.courseName = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.courseName.addItems(courses)
        self.courseName.setCurrentText(courseName)
        layout.addWidget(self.courseName)

        mobileNumber = mainWindow.table.item(index, 3).text()
        self.mobileNumber = QLineEdit(mobileNumber)
        self.mobileNumber.setPlaceholderText("Enter Mobile Number")
        layout.addWidget(self.mobileNumber)

        button = QPushButton("Update")
        button.clicked.connect(self.updateStudent)
        layout.addWidget(button)

        self.setLayout(layout)

    def updateStudent(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name=?, course=?, mobile=? WHERE id=?",
                       (self.studentName.text(),
                        self.courseName.itemText(self.courseName.currentIndex()),
                        self.mobileNumber.text(),
                        self.studentId))
        connection.commit()
        cursor.close()
        connection.close()
        mainWindow.LoadTable()
        self.close()
        confirmationBox = QMessageBox()
        confirmationBox.setWindowTitle("Success")
        confirmationBox.setText("Student data has been updated successfully.")

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student data")
        
        layout = QGridLayout()
        confirmationLabel = QLabel("Are you sure you want to delete this student?")
        yesButton = QPushButton("Yes")
        noButton = QPushButton("No")
        
        layout.addWidget(confirmationLabel, 0, 0, 1, 2)
        layout.addWidget(yesButton, 1, 0)
        layout.addWidget(noButton, 1, 1)
        self.setLayout(layout)
        
        yesButton.clicked.connect(self.deleteStudent)
        noButton.clicked.connect(self.reject)
        
    
    def deleteStudent(self):
        index = mainWindow.table.currentRow()
        studentId = mainWindow.table.item(index, 0).text()
        
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id=?", (studentId,))
        connection.commit()
        cursor.close()
        connection.close()
        mainWindow.LoadTable()
        
        self.close()
        confirmationBox = QMessageBox()
        confirmationBox.setWindowTitle("Success")
        confirmationBox.setText("Student has been deleted successfully.")

class insertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Student data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.studentName = QLineEdit()
        self.studentName.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.studentName)
        
        self.courseName = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.courseName.addItems(courses)
        layout.addWidget(self.courseName)

        self.mobileNumber = QLineEdit()
        self.mobileNumber.setPlaceholderText("Enter Mobile Number")
        layout.addWidget(self.mobileNumber)

        button = QPushButton("Submit")
        button.clicked.connect(self.addStudent)
        layout.addWidget(button)

        self.setLayout(layout)

    def addStudent(self):
        name = self.studentName.text()
        course = self.courseName.itemText(self.courseName.currentIndex())
        mobile = self.mobileNumber.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        mainWindow.LoadTable()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
            This is a simple Student Management System built using PyQt6 and SQLite.
            It allows you to add, edit, delete, and search for student records.
            Developed by Harsh Mishrikotkar, during the course of Python Programming.
            Feel free to contribute or modify the code as per your needs.
            """
        self.setText(content)
        

class searchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.studentName = QLineEdit()
        self.studentName.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.studentName)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)
    
    def search(self):
        name = self.studentName.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name LIKE ?", (name,))
        rows = list(result)
        print(rows)
        items = mainWindow.table.findItems(name, Qt.MatchFlag.MatchContains)
        for i in items:
            print(i)
            mainWindow.table.item(i.row(), 1).setSelected(True)
        
        cursor.close()
        connection.close()

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
mainWindow.LoadTable()
sys.exit(app.exec())