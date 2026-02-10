import json
from datetime import datetime, timedelta
import os

BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"

# -------------------- BOOK CLASS --------------------
class Book:
    def __init__(self, title, author, isbn, year=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.available = True
        self.borrowed_by = None
        self.due_date = None

    def check_out(self, member_id, days=14):
        if not self.available:
            return False
        self.available = False
        self.borrowed_by = member_id
        self.due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        return True

    def return_book(self):
        self.available = True
        self.borrowed_by = None
        self.due_date = None

    def is_overdue(self):
        if not self.available and self.due_date:
            return datetime.now() > datetime.strptime(self.due_date, "%Y-%m-%d")
        return False

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        book = Book(data["title"], data["author"], data["isbn"], data.get("year"))
        book.available = data["available"]
        book.borrowed_by = data["borrowed_by"]
        book.due_date = data["due_date"]
        return book

    def __str__(self):
        status = "Available" if self.available else f"Borrowed by {self.borrowed_by} (Due: {self.due_date})"
        return f"{self.title} by {self.author} | ISBN: {self.isbn} | {status}"


# -------------------- MEMBER CLASS --------------------
class Member:
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
        self.borrowed_books = []
        self.max_books = 5

    def can_borrow(self):
        return len(self.borrowed_books) < self.max_books

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        member = Member(data["name"], data["member_id"])
        member.borrowed_books = data["borrowed_books"]
        return member

    def __str__(self):
        return f"{self.name} (ID: {self.member_id}) | Borrowed: {len(self.borrowed_books)} books"


# -------------------- LIBRARY CLASS --------------------
class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.load_data()

    def add_book(self, book):
        self.books[book.isbn] = book

    def register_member(self, member):
        self.members[member.member_id] = member

    def borrow_book(self, isbn, member_id):
        if isbn not in self.books or member_id not in self.members:
            return "Book or Member not found"

        book = self.books[isbn]
        member = self.members[member_id]

        if not member.can_borrow():
            return "Borrow limit reached"

        if book.check_out(member_id):
            member.borrowed_books.append(isbn)
            return "Book borrowed successfully"
        return "Book not available"

    def return_book(self, isbn, member_id):
        if isbn in self.books and member_id in self.members:
            book = self.books[isbn]
            member = self.members[member_id]
            if isbn in member.borrowed_books:
                book.return_book()
                member.borrowed_books.remove(isbn)
                return "Book returned successfully"
        return "Return failed"

    def search_books(self, keyword):
        results = []
        for book in self.books.values():
            if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower() or keyword == book.isbn:
                results.append(book)
        return results

    def save_data(self):
        with open(BOOKS_FILE, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.books.items()}, f, indent=4)

        with open(MEMBERS_FILE, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.members.items()}, f, indent=4)

    def load_data(self):
        if os.path.exists(BOOKS_FILE):
            with open(BOOKS_FILE) as f:
                data = json.load(f)
                for k, v in data.items():
                    self.books[k] = Book.from_dict(v)

        if os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE) as f:
                data = json.load(f)
                for k, v in data.items():
                    self.members[k] = Member.from_dict(v)

    def show_overdue_books(self):
        return [book for book in self.books.values() if book.is_overdue()]


# -------------------- MENU SYSTEM --------------------
def menu():
    print("\n" + "="*35)
    print("  LIBRARY MANAGEMENT SYSTEM")
    print("="*35)
    print("1. Add Book")
    print("2. Register Member")
    print("3. Borrow Book")
    print("4. Return Book")
    print("5. Search Books")
    print("6. View All Books")
    print("7. View All Members")
    print("8. View Overdue Books")
    print("9. Save & Exit")
    print("0. Exit Without Saving")


def main():
    library = Library()

    while True:
        menu()
        choice = input("Enter choice: ")

        if choice == "1":
            title = input("Title: ")
            author = input("Author: ")
            isbn = input("ISBN: ")
            year = input("Year (optional): ")
            library.add_book(Book(title, author, isbn, year))

        elif choice == "2":
            name = input("Member Name: ")
            member_id = input("Member ID: ")
            library.register_member(Member(name, member_id))

        elif choice == "3":
            isbn = input("ISBN: ")
            member_id = input("Member ID: ")
            print(library.borrow_book(isbn, member_id))

        elif choice == "4":
            isbn = input("ISBN: ")
            member_id = input("Member ID: ")
            print(library.return_book(isbn, member_id))

        elif choice == "5":
            keyword = input("Search keyword: ")
            results = library.search_books(keyword)
            for book in results:
                print(book)

        elif choice == "6":
            for book in library.books.values():
                print(book)

        elif choice == "7":
            for member in library.members.values():
                print(member)

        elif choice == "8":
            overdue = library.show_overdue_books()
            for book in overdue:
                print(book)

        elif choice == "9":
            library.save_data()
            print("Data saved. Goodbye!")
            break

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
