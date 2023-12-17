from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QMessageBox, \
    QApplication
from models import session, User


class RegistrationWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Регистрация")
        self.setGeometry(200, 200, 300, 300)

        layout = QVBoxLayout()

        username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()

        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        role_label = QLabel("Выберите роль:")

        self.student_radio = QRadioButton("Студент")
        self.employee_radio = QRadioButton("Сотрудник")

        # Дополнительные поля для студента
        self.group_label = QLabel("Группа:")
        self.group_input = QLineEdit()
        self.group_label.setVisible(False)
        self.group_input.setVisible(False)

        self.fullname_label = QLabel("ФИО:")
        self.fullname_input = QLineEdit()
        self.fullname_label.setVisible(False)
        self.fullname_input.setVisible(False)

        self.phone_label = QLabel("Номер телефона:")
        self.phone_input = QLineEdit()
        self.phone_label.setVisible(False)
        self.phone_input.setVisible(False)

        self.employee_fullname_label = QLabel("ФИО:")
        self.employee_fullname_input = QLineEdit()
        self.employee_fullname_label.setVisible(False)
        self.employee_fullname_input.setVisible(False)

        self.employee_phone_label = QLabel("Номер телефона:")
        self.employee_phone_input = QLineEdit()
        self.employee_phone_label.setVisible(False)
        self.employee_phone_input.setVisible(False)

        register_button = QPushButton("Зарегистрироваться")
        register_button.clicked.connect(self.register_user)

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(role_label)
        layout.addWidget(self.student_radio)
        layout.addWidget(self.employee_radio)

        layout.addWidget(self.group_label)
        layout.addWidget(self.group_input)
        layout.addWidget(self.fullname_label)
        layout.addWidget(self.fullname_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)

        layout.addWidget(self.employee_fullname_label)
        layout.addWidget(self.employee_fullname_input)
        layout.addWidget(self.employee_phone_label)
        layout.addWidget(self.employee_phone_input)

        layout.addWidget(register_button)

        self.setLayout(layout)

        self.student_radio.toggled.connect(self.toggle_student_fields)
        self.employee_radio.toggled.connect(self.toggle_employee_fields)

    def toggle_student_fields(self):
        is_student = self.student_radio.isChecked()

        self.group_label.setVisible(is_student)
        self.group_input.setVisible(is_student)
        self.fullname_label.setVisible(is_student)
        self.fullname_input.setVisible(is_student)
        self.phone_label.setVisible(is_student)
        self.phone_input.setVisible(is_student)

    def toggle_employee_fields(self):
        is_employee = self.employee_radio.isChecked()

        self.employee_fullname_label.setVisible(is_employee)
        self.employee_fullname_input.setVisible(is_employee)
        self.employee_phone_label.setVisible(is_employee)
        self.employee_phone_input.setVisible(is_employee)

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not self.student_radio.isChecked() and not self.employee_radio.isChecked():
            self.show_error_message("Ошибка регистрации", "Выберите роль: студент или сотрудник.")
            return

        if not username or not password:
            self.show_error_message("Ошибка регистрации", "Заполните все поля.")
            return

        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            self.show_error_message("Ошибка регистрации", "Пользователь с таким именем уже существует.")
            return

        role = "Студент" if self.student_radio.isChecked() else "Сотрудник"
        additional_info = ""

        if role == "Студент":
            group = self.group_input.text()
            fullname = self.fullname_input.text()
            phone = self.phone_input.text()

            if phone and len(phone) != 11:
                self.show_error_message("Ошибка регистрации", "Некорректная длина номера телефона. Введите 11 цифр.")
                return

            additional_info = f"\nГруппа: {group}\nФИО: {fullname}\nТелефон: {phone}"

        elif role == "Сотрудник":
            employee_fullname = self.employee_fullname_input.text()
            employee_phone = self.employee_phone_input.text()

            if employee_phone and len(employee_phone) != 11:
                self.show_error_message("Ошибка регистрации", "Некорректная длина номера телефона. Введите 11 цифр.")
                return

            additional_info = f"\nФИО: {employee_fullname}\nТелефон: {employee_phone}"

        try:
            user = User(username=username, password=password, role=role)
            session.add(user)
            session.commit()

            self.show_message("Успешно", f"Новый пользователь зарегистрирован как {role}.{additional_info}")

        except Exception as err:
            session.rollback()
            print(f"Error: {err}")

        finally:
            session.close()

        self.close()

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()


if __name__ == '__main__':
    app = QApplication([])
    window = RegistrationWindow()
    window.show()
    app.exec()
