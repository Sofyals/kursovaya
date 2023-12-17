import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from models import session, User
from registration import RegistrationWindow
from student import Student
from employee import Employee
from models import Base, engine

Base.metadata.create_all(bind=engine)

class PasswordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Студенческая библиотека")
        self.setFixedSize(300, 200)

        self.current_user = None

        layout = QVBoxLayout()

        username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()

        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.check_password)

        register_button = QPushButton("Регистрация")
        register_button.clicked.connect(self.open_registration_window)

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(register_button)

        self.setLayout(layout)


        self.adjustSize()
        self.move_center()

    def open_registration_window(self):
        registration_window = RegistrationWindow()
        registration_window.exec()

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def check_password(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            user = session.query(User).filter_by(username=username, password=password).first()

            if user:
                self.current_user = user
                self.open_window(user.role)
            else:
                self.show_error_message("Ошибка авторизации", "Неверное имя пользователя или пароль.")

        except Exception as e:
            print(f"Error: {e}")
            self.show_error_message("Ошибка авторизации", "Произошла ошибка при авторизации.")

        finally:
            session.close()

    def open_window(self, role):
        self.close()

        if role == "Студент":
            window = Student(self.current_user)
        elif role == "Сотрудник":
            window = Employee(self.current_user)
        else:
            self.show_error_message("Ошибка", "Неизвестная роль пользователя")
            return

        window.exec()

    def move_center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry()
        frame_gm.moveCenter(screen.center())
        self.move(frame_gm.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PasswordWindow()
    main_window.show()
    sys.exit(app.exec())
