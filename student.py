from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMessageBox, QComboBox, QApplication
from models import session, Book, User


class Student(QDialog):
    def __init__(self, user):
        super().__init__()

        self.setWindowTitle('Студенческая библиотека - Режим студента')
        self.setFixedSize(400, 200)
        self.user = user
        self.adjustSize()
        self.move_center()

        layout = QVBoxLayout()

        welcome_label = QLabel(f"Добро пожаловать, {user.username}!")
        borrow_books_btn = QPushButton("Взять книгу в аренду")
        view_borrowed_books_btn = QPushButton("Просмотреть взятые книги")
        return_books_btn = QPushButton("Вернуть книгу")

        borrow_books_btn.clicked.connect(self.borrow_book)
        view_borrowed_books_btn.clicked.connect(self.view_borrowed_books)
        return_books_btn.clicked.connect(self.return_book)

        layout.addWidget(welcome_label)
        layout.addWidget(borrow_books_btn)
        layout.addWidget(view_borrowed_books_btn)
        layout.addWidget(return_books_btn)

        self.setLayout(layout)



    def browse_books(self):
        books = session.query(Book).filter_by(is_available=1).all()

        if books:
            book_list = "\n".join([f"{book.title} Автор: {book.author}" for book in books])
            QMessageBox.information(self, "Доступные книги", f"Доступные книги:\n{book_list}",
                                    QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, "Доступные книги", "В данный момент нет доступных книг.",
                                    QMessageBox.StandardButton.Ok)

    def borrow_book(self):
        books = session.query(Book).filter_by(is_available=1).all()

        if not books:
            QMessageBox.information(self, "Взять книгу в аренду", "В данный момент нет доступных книг.")
            return

        book_combo = QComboBox()
        book_combo.addItems([f"{book.title} Автор: {book.author}" for book in books])


        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите книгу")
        dialog.setGeometry(400, 400, 300, 100)

        layout = QVBoxLayout()
        layout.addWidget(book_combo)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_book = book_combo.currentText()
            title, author = selected_book.split(" Автор: ")

            book = session.query(Book).filter_by(title=title, author=author, is_available=1).first()

            if book:
                book.is_available = 0
                book.borrower_id = self.user.id
                session.commit()
                QMessageBox.information(self, "Взять книгу в аренду", f"Книга '{title}' успешно взята в аренду.")
            else:
                QMessageBox.warning(self, "Взять книгу в аренду", "Книга уже взята или не существует.")

    def view_borrowed_books(self):
        borrowed_books = session.query(Book).filter_by(borrower_id=self.user.id).all()

        if borrowed_books:
            book_list = "\n".join([f"{book.title} Автор: {book.author}" for book in borrowed_books])
            QMessageBox.information(self, "Взятые книги", f"Ваши взятые книги:\n{book_list}")
        else:
            QMessageBox.information(self, "Взятые книги", "Вы не взяли ни одной книги в аренду.")

    def return_book(self):
        books = session.query(Book).filter_by(borrower_id=self.user.id).all()

        if not books:
            QMessageBox.information(self, "Вернуть книгу", "У вас нет взятых книг для возврата.")
            return

        book_combo = QComboBox()
        book_combo.addItems([f"{book.title} Автор: {book.author}" for book in books])

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
            selected_book = book_combo.currentText()
            title, author = selected_book.split(" Автор: ")

            returned_book = session.query(Book).filter_by(title=title, author=author, borrower_id=self.user.id).first()

            if returned_book:
                returned_book.borrower_id = None
                returned_book.is_available = 1
                session.commit()
                self.show_message("Вернуть книгу", f"Книга '{title}' успешно возвращена.")
            else:
                self.show_error_message("Ошибка", "Произошла ошибка при возврате книги.")
    def move_center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry()
        frame_gm.moveCenter(screen.center())
        self.move(frame_gm.topLeft())

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

