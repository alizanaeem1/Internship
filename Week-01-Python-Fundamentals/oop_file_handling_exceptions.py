"""
Week 1 - OOP, File Handling, and Exception Handling
This file demonstrates advanced beginner-level Python concepts.
"""

from pathlib import Path
import json


# ---------------------------------------------------------
# 1. CLASSES AND OBJECTS
# ---------------------------------------------------------

class Student:
    """Represents a university student."""

    university = "COMSATS University Islamabad"

    def __init__(self, name, roll_number, cgpa):
        self.name = name
        self.roll_number = roll_number
        self.cgpa = cgpa

    def display_profile(self):
        return (
            f"Name: {self.name}\n"
            f"Roll Number: {self.roll_number}\n"
            f"CGPA: {self.cgpa}\n"
            f"University: {self.university}"
        )

    def update_cgpa(self, new_cgpa):
        if 0.0 <= new_cgpa <= 4.0:
            self.cgpa = new_cgpa
        else:
            raise ValueError("CGPA must be between 0.0 and 4.0.")


student = Student("Aliza Naeem", "FA23-BSE-116", 3.60)

print("Student Object")
print(student.display_profile())


# ---------------------------------------------------------
# 2. ENCAPSULATION
# ---------------------------------------------------------

class BankAccount:
    """Demonstrates encapsulation using a private attribute."""

    def __init__(self, account_holder, opening_balance=0):
        self.account_holder = account_holder
        self.__balance = opening_balance

    @property
    def balance(self):
        return self.__balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self.__balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if amount > self.__balance:
            raise ValueError("Insufficient balance.")
        self.__balance -= amount


account = BankAccount("Aliza", 10000)
account.deposit(5000)
account.withdraw(3000)

print("\nEncapsulation")
print("Account Holder:", account.account_holder)
print("Current Balance:", account.balance)


# ---------------------------------------------------------
# 3. INHERITANCE
# ---------------------------------------------------------

class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

    def get_role(self):
        return "Employee"

    def display_information(self):
        return f"{self.employee_id} - {self.name} - {self.get_role()}"


class Intern(Employee):
    def __init__(self, name, employee_id, technology):
        super().__init__(name, employee_id)
        self.technology = technology

    def get_role(self):
        return "Intern"

    def display_information(self):
        base_info = super().display_information()
        return f"{base_info} - Technology: {self.technology}"


intern = Intern("Aliza Naeem", "INT-001", "Python")

print("\nInheritance")
print(intern.display_information())


# ---------------------------------------------------------
# 4. POLYMORPHISM
# ---------------------------------------------------------

class PDFDocument:
    def load(self):
        return "Loading data from PDF document"


class TextDocument:
    def load(self):
        return "Loading data from text document"


class WordDocument:
    def load(self):
        return "Loading data from Word document"


def process_document(document):
    print(document.load())


print("\nPolymorphism")
documents = [PDFDocument(), TextDocument(), WordDocument()]

for document in documents:
    process_document(document)


# ---------------------------------------------------------
# 5. CLASS METHODS AND STATIC METHODS
# ---------------------------------------------------------

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, fahrenheit):
        celsius = (fahrenheit - 32) * 5 / 9
        return cls(celsius)

    @staticmethod
    def is_freezing(celsius):
        return celsius <= 0


temperature = Temperature.from_fahrenheit(68)

print("\nClass and Static Methods")
print(f"Celsius: {temperature.celsius:.2f}")
print("Is Freezing:", Temperature.is_freezing(temperature.celsius))


# ---------------------------------------------------------
# 6. CUSTOM EXCEPTION
# ---------------------------------------------------------

class InvalidMarksError(Exception):
    """Raised when marks are outside the valid range."""


def validate_marks(marks):
    if not 0 <= marks <= 100:
        raise InvalidMarksError("Marks must be between 0 and 100.")
    return True


print("\nCustom Exception")

try:
    validate_marks(105)
except InvalidMarksError as error:
    print("Validation Error:", error)


# ---------------------------------------------------------
# 7. BASIC EXCEPTION HANDLING
# ---------------------------------------------------------

def safe_divide(numerator, denominator):
    try:
        result = numerator / denominator
    except ZeroDivisionError:
        return "Cannot divide by zero."
    except TypeError:
        return "Both values must be numeric."
    else:
        return result
    finally:
        print("Division operation attempted.")


print("\nException Handling")
print("10 / 2 =", safe_divide(10, 2))
print("10 / 0 =", safe_divide(10, 0))
print("'10' / 2 =", safe_divide("10", 2))


# ---------------------------------------------------------
# 8. FILE HANDLING
# ---------------------------------------------------------

data_folder = Path(__file__).parent / "sample_data"
data_folder.mkdir(exist_ok=True)

text_file = data_folder / "internship_notes.txt"

with text_file.open("w", encoding="utf-8") as file:
    file.write("Week 1 Internship Notes\n")
    file.write("Topic: Python Fundamentals\n")
    file.write("Status: Completed\n")

with text_file.open("a", encoding="utf-8") as file:
    file.write("Additional Topic: File Handling\n")

print("\nFile Handling")
with text_file.open("r", encoding="utf-8") as file:
    content = file.read()
    print(content)


# ---------------------------------------------------------
# 9. JSON HANDLING
# ---------------------------------------------------------

profile_data = {
    "name": "Aliza Naeem",
    "role": "Software Engineering Intern",
    "skills": ["Python", "Git", "GitHub"],
    "week": 1,
}

json_file = data_folder / "profile.json"

with json_file.open("w", encoding="utf-8") as file:
    json.dump(profile_data, file, indent=4)

with json_file.open("r", encoding="utf-8") as file:
    loaded_profile = json.load(file)

print("\nJSON Handling")
print("Loaded Profile:", loaded_profile)


# ---------------------------------------------------------
# 10. SAFE FILE READING
# ---------------------------------------------------------

def read_file_safely(file_path):
    try:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            return file.read()

    except FileNotFoundError as error:
        return str(error)
    except PermissionError:
        return "Permission denied while reading the file."
    except OSError as error:
        return f"Operating system error: {error}"


print("\nSafe File Reading")
print(read_file_safely(text_file))


# ---------------------------------------------------------
# 11. CONTEXT MANAGER CLASS
# ---------------------------------------------------------

class SimpleLogger:
    """Custom context manager for writing log messages."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.file = None

    def __enter__(self):
        self.file = self.file_path.open("a", encoding="utf-8")
        return self

    def log(self, message):
        self.file.write(message + "\n")

    def __exit__(self, exception_type, exception_value, traceback):
        if self.file:
            self.file.close()


log_file = data_folder / "activity.log"

with SimpleLogger(log_file) as logger:
    logger.log("Python OOP practice completed.")
    logger.log("File handling practice completed.")

print("\nContext Manager")
print(read_file_safely(log_file))


# ---------------------------------------------------------
# 12. MINI PROJECT: TASK MANAGEMENT
# ---------------------------------------------------------

class Task:
    def __init__(self, title, status="Pending"):
        self.title = title
        self.status = status

    def complete(self):
        self.status = "Completed"

    def to_dictionary(self):
        return {
            "title": self.title,
            "status": self.status,
        }


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, title):
        self.tasks.append(Task(title))

    def complete_task(self, index):
        if index < 0 or index >= len(self.tasks):
            raise IndexError("Task index is out of range.")
        self.tasks[index].complete()

    def save_tasks(self, file_path):
        task_data = [task.to_dictionary() for task in self.tasks]

        with Path(file_path).open("w", encoding="utf-8") as file:
            json.dump(task_data, file, indent=4)

    def display_tasks(self):
        if not self.tasks:
            print("No tasks available.")
            return

        for index, task in enumerate(self.tasks, start=1):
            print(f"{index}. {task.title} - {task.status}")


task_manager = TaskManager()
task_manager.add_task("Practice Python fundamentals")
task_manager.add_task("Learn file handling")
task_manager.add_task("Study object-oriented programming")
task_manager.complete_task(0)

print("\nTask Manager")
task_manager.display_tasks()

tasks_file = data_folder / "tasks.json"
task_manager.save_tasks(tasks_file)

print("\nSaved Tasks")
print(read_file_safely(tasks_file))
