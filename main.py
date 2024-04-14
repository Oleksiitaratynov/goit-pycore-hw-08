from collections import defaultdict, UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if  len(value[1:]) <= 15 and value[1:].isdigit():
            self.__value = value
        else:
            raise ValueError('Wrong telephone number')

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("wrong date use DD.MM.YYYY")
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def edit_phone(self, old_number, new_number):
        phone_to_edit = self.find_phone(old_number)
        if phone_to_edit:
            phone_to_edit.value = new_number

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            now = datetime.now().date()
            bday = self.birthday.date.replace(year=now.year)
            if bday < now:
                bday = bday.replace(year=now.year + 1)
            return (bday - now).days
        return None

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, Phones: {phones}{birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        today = datetime.date.today()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday and today <= record.birthday.value <= today + datetime.timedelta(days=7):
                upcoming_birthdays.append(record.name.value)
        return upcoming_birthdays

    def get_upcoming_birthday(self, days=7):
        upcoming_birthdays = []
        for record in self.data.values():
            days_to_bday = record.days_to_birthday()
            if days_to_bday is not None and days_to_bday <= days:
                upcoming_birthdays.append((record.name.value, days_to_bday))
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.data.get(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, new_phone)
        return "Phone number changed."
    else:
        return "Contact not found."

@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    else:
        return "Contact not found."

@input_error
def show_all(book: AddressBook):
    return '\n'.join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.data.get(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return str(record.birthday)

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = []
    for record in book.data.values():
        days_to_birthday = record.days_to_birthday()
        if days_to_birthday is not None and days_to_birthday <= 7:
            upcoming_birthdays.append(f"{record.name.value}: {days_to_birthday} days")
    if upcoming_birthdays:
        return "\n".join(upcoming_birthdays)
    else:
        return "No upcoming birthdays."

def parse_input(user_input):
    parts = user_input.split()
    command = parts[0]
    args = parts[1:]
    return command, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()