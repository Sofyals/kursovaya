from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMessageBox, QInputDialog, QComboBox, QApplication
from models import session, User, Book


class Employee(QDialog):
    def __init__(self, user):
        super().__init__()

        self.setWindowTitle('Студенческая библиотека - Режим библиотекаря')
        self.setFixedSize(400, 200)
        self.adjustSize()
        self.move_center()

        layout = QVBoxLayout()

        welcome_label = QLabel(f"Добро пожаловать, {user.username}!")
        add_book_btn = QPushButton("Добавить новую книгу")
        manage_users_btn = QPushButton("Управление читателями")
        view_borrowed_books_btn = QPushButton("Просмотреть взятые книги")
        return_book_btn = QPushButton("Отметить книгу как возвращенную")

        add_book_btn.clicked.connect(self.add_book)
        manage_users_btn.clicked.connect(self.manage_users)
        view_borrowed_books_btn.clicked.connect(self.view_borrowed_books)
        return_book_btn.clicked.connect(self.return_book)

        layout.addWidget(welcome_label)
        layout.addWidget(add_book_btn)
        layout.addWidget(manage_users_btn)
        layout.addWidget(view_borrowed_books_btn)
        layout.addWidget(return_book_btn)

        self.setLayout(layout)

    def add_book(self):
        title, ok = QInputDialog.getText(self, "Добавить новую книгу", "Введите название книги:")

        if ok and title:
            author, ok = QInputDialog.getText(self, "Добавить новую книгу", "Введите автора книги:")

            if ok and author:
                quantity, ok = QInputDialog.getInt(self, "Добавить новую книгу", "Введите количество книг:", 1, 1)

                if ok and quantity > 0:
                    try:
                        existing_book = session.query(Book).filter_by(title=title, author=author,
                                                                      is_available=1).first()

                        if existing_book:
                            self.show_error_message("Ошибка", f"Книга '{title}' уже есть у другого пользователя.")
                        else:
                            for _ in range(quantity):
                                new_book = Book(title=title, author=author, is_available=1)
                                session.add(new_book)
                            session.commit()

                            self.show_message("Добавить новую книгу",
                                              f"Книга '{title}' (количество - {quantity}) успешно добавлена.")
                    except Exception as e:
                        session.rollback()
                        self.show_error_message("Ошибка", f"Произошла ошибка: {e}")
                    finally:
                        session.close()

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def move_center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry()
        frame_gm.moveCenter(screen.center())
        self.move(frame_gm.topLeft())

    def manage_users(self):
        options = ["Просмотреть пользователей", "Добавить нового пользователя", "Удалить пользователя"]
        choice, ok = QInputDialog.getItem(self, "Управление читателями", "Выберите действие:", options, 0, False)

        if ok and choice:
            if choice == "Просмотреть пользователей":
                self.show_users()
            elif choice == "Добавить нового пользователя":
                self.add_user()
            elif choice == "Удалить пользователя":
                self.delete_user()

    def show_users(self):
        users = session.query(User).all()

        if users:
            user_list = "\n".join([f"{user.username} ({user.role})" for user in users])
            self.show_message("Список пользователей", f"Список пользователей:\n{user_list}")
        else:
            self.show_message("Список пользователей", "Нет зарегистрированных пользователей.")

    def add_user(self):
        username, ok = QInputDialog.getText(self, "Добавить нового пользователя", "Введите имя пользователя:")

        if ok and username:
            password, ok = QInputDialog.getText(self, "Добавить нового пользователя", "Введите пароль:")

            if ok and password:
                role_options = ["Студент", "Сотрудник"]
                role, ok = QInputDialog.getItem(self, "Добавить нового пользователя", "Выберите роль:",
                                                role_options, 0, False)

                if ok and role:
                    try:
                        new_user = User(username=username, password=password, role=role)
                        session.add(new_user)
                        session.commit()

                        self.show_message("Добавить нового пользователя", f"Пользователь {username} успешно добавлен.")
                    except Exception as e:
                        session.rollback()
                        self.show_error_message("Ошибка", f"Произошла ошибка: {e}")
                    finally:
                        session.close()

    def delete_user(self):
        users = session.query(User).all()

        if users:
            user_names = [user.username for user in users]
            user_name, ok = QInputDialog.getItem(self, "Удалить пользователя", "Выберите пользователя:", user_names, 0,
                                                 False)

            if ok and user_name:
                try:
                    user_to_delete = session.query(User).filter_by(username=user_name).first()

                    if user_to_delete:
                        session.delete(user_to_delete)
                        session.commit()

                        self.show_message("Удалить пользователя", f"Пользователь {user_name} успешно удален.")
                    else:
                        self.show_error_message("Ошибка", f"Пользователь {user_name} не найден.")
                except Exception as e:
                    session.rollback()
                    self.show_error_message("Ошибка", f"Произошла ошибка: {e}")
                finally:
                    session.close()
        else:
            self.show_message("Удалить пользователя", "Нет зарегистрированных пользователей.")

    def view_borrowed_books(self):
        borrowed_books = session.query(Book).filter(Book.borrower_id.isnot(None)).all()

        if borrowed_books:
            book_list = "\n".join([self.format_borrowed_book_info(book) for book in borrowed_books])
            self.show_message("Взятые книги", f"Взятые книги:\n{book_list}")
        else:
            self.show_message("Взятые книги", "Нет взятых книг.")

    def format_borrowed_book_info(self, book):
        return f"{book.title} Автор: {book.author} (взята {book.borrower.username})"

    def return_book(self):
        borrowed_books = session.query(Book).filter(Book.borrower_id.isnot(None)).all()

        if not borrowed_books:
            QMessageBox.information(self, "Вернуть книгу", "Нет взятых книг для возврата.",
                                    QMessageBox.StandardButton.Ok)
            return

        book_combo = QComboBox()
        book_combo.addItems([self.format_borrowed_book_info(book) for book in borrowed_books])
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите книгу для возврата")
        dialog.setGeometry(400, 400, 300, 100)
        layout = QVBoxLayout()
        layout.addWidget(book_combo)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_book_info = book_combo.currentText()
            selected_book_title, _ = selected_book_info.split(" Автор: ")
            try:
                returned_book = session.query(Book).filter_by(title=selected_book_title).first()

                if returned_book and returned_book.borrower_id is not None:
                    returned_book.borrower_id = None
                    session.commit()
                    self.show_message("Вернуть книгу", f"Книга '{selected_book_title}' успешно возвращена.")
                else:
                    self.show_error_message("Ошибка", "Книга не была взята в аренду или уже возвращена.")
            except Exception as e:
                session.rollback()
                self.show_error_message("Ошибка", f"Произошла ошибка: {e}")
            finally:
                session.close()

if __name__ == "__main__":
    app = QApplication([])
    user = User(username="test", role="employee")
    window = Employee(user)
    window.show()
    app.exec()
