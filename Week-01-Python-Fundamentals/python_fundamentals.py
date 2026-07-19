"""
Week 1 - Python Fundamentals
This file covers core Python syntax and programming concepts.
"""

# ---------------------------------------------------------
# 1. VARIABLES AND DATA TYPES
# ---------------------------------------------------------

student_name = "Aliza Naeem"
age = 21
cgpa = 3.60
is_intern = True
skills = ["Python", "Git", "GitHub"]

print("Student:", student_name)
print("Age:", age)
print("CGPA:", cgpa)
print("Intern:", is_intern)
print("Skills:", skills)

print("\nData Types")
print(type(student_name))
print(type(age))
print(type(cgpa))
print(type(is_intern))
print(type(skills))


# ---------------------------------------------------------
# 2. TYPE CASTING
# ---------------------------------------------------------

marks_text = "85"
marks = int(marks_text)
percentage = float(marks)

print("\nType Casting")
print("Marks as integer:", marks)
print("Percentage as float:", percentage)
print("Age as string:", str(age))


# ---------------------------------------------------------
# 3. OPERATORS
# ---------------------------------------------------------

a = 20
b = 6

print("\nArithmetic Operators")
print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
print("Floor Division:", a // b)
print("Modulus:", a % b)
print("Power:", a ** 2)

print("\nComparison Operators")
print("a == b:", a == b)
print("a != b:", a != b)
print("a > b:", a > b)
print("a < b:", a < b)
print("a >= b:", a >= b)
print("a <= b:", a <= b)

has_laptop = True
has_internet = True

print("\nLogical Operators")
print("AND:", has_laptop and has_internet)
print("OR:", has_laptop or has_internet)
print("NOT:", not has_laptop)

technologies = ["Python", "Flutter", "MongoDB"]

print("\nMembership Operators")
print("'Python' in technologies:", "Python" in technologies)
print("'Java' not in technologies:", "Java" not in technologies)

x = [1, 2, 3]
y = x
z = [1, 2, 3]

print("\nIdentity Operators")
print("x is y:", x is y)
print("x is z:", x is z)
print("x == z:", x == z)


# ---------------------------------------------------------
# 4. STRINGS
# ---------------------------------------------------------

project_title = "Real-Time RAG System"

print("\nString Operations")
print("Original:", project_title)
print("Uppercase:", project_title.upper())
print("Lowercase:", project_title.lower())
print("Title Case:", project_title.title())
print("Length:", len(project_title))
print("Starts with Real:", project_title.startswith("Real"))
print("Replace:", project_title.replace("RAG", "Retrieval-Augmented Generation"))
print("Split:", project_title.split("-"))

first_name = "Aliza"
last_name = "Naeem"
full_name = f"{first_name} {last_name}"

print("Formatted Name:", full_name)


# ---------------------------------------------------------
# 5. CONDITIONAL STATEMENTS
# ---------------------------------------------------------

marks = 86

if marks >= 90:
    grade = "A+"
elif marks >= 85:
    grade = "A"
elif marks >= 75:
    grade = "B+"
elif marks >= 65:
    grade = "B"
else:
    grade = "C"

print("\nConditional Statement")
print(f"Marks: {marks}, Grade: {grade}")

attendance = 82
result = "Eligible" if attendance >= 75 else "Not Eligible"
print("Attendance Status:", result)

username = "admin"
password = "python123"

if username == "admin":
    if password == "python123":
        print("Login successful")
    else:
        print("Incorrect password")
else:
    print("Unknown user")


# ---------------------------------------------------------
# 6. FOR LOOPS
# ---------------------------------------------------------

print("\nFor Loop")
for number in range(1, 6):
    print("Number:", number)

print("\nLoop Through Skills")
for index, skill in enumerate(skills, start=1):
    print(f"{index}. {skill}")

print("\nNested Loop")
for row in range(1, 4):
    for column in range(1, 4):
        print(f"Row {row}, Column {column}")


# ---------------------------------------------------------
# 7. WHILE LOOP
# ---------------------------------------------------------

print("\nWhile Loop")
counter = 1

while counter <= 5:
    print("Counter:", counter)
    counter += 1


# ---------------------------------------------------------
# 8. BREAK, CONTINUE, AND PASS
# ---------------------------------------------------------

print("\nBreak Example")
for number in range(1, 10):
    if number == 6:
        break
    print(number)

print("\nContinue Example")
for number in range(1, 8):
    if number == 4:
        continue
    print(number)

print("\nPass Example")
for number in range(1, 4):
    if number == 2:
        pass
    print(number)


# ---------------------------------------------------------
# 9. RANGE, ENUMERATE, AND ZIP
# ---------------------------------------------------------

students = ["Aliza", "Sara", "Hina"]
scores = [88, 91, 79]

print("\nUsing zip()")
for student, score in zip(students, scores):
    print(f"{student}: {score}")

print("\nUsing enumerate()")
for position, student in enumerate(students, start=1):
    print(position, student)


# ---------------------------------------------------------
# 10. COMPREHENSIONS
# ---------------------------------------------------------

numbers = list(range(1, 11))

squares = [number ** 2 for number in numbers]
even_numbers = [number for number in numbers if number % 2 == 0]
square_dictionary = {number: number ** 2 for number in range(1, 6)}
unique_remainders = {number % 3 for number in numbers}

print("\nComprehensions")
print("Squares:", squares)
print("Even Numbers:", even_numbers)
print("Square Dictionary:", square_dictionary)
print("Unique Remainders:", unique_remainders)


# ---------------------------------------------------------
# 11. USER INPUT EXAMPLE
# ---------------------------------------------------------

def user_input_demo():
    """Demonstrates user input without running automatically."""
    name = input("Enter your name: ").strip()
    user_age = int(input("Enter your age: "))
    print(f"Welcome {name}. Next year you will be {user_age + 1} years old.")


# Uncomment the following line to test user input:
# user_input_demo()


# ---------------------------------------------------------
# 12. SMALL PRACTICE PROGRAM
# ---------------------------------------------------------

def calculate_grade(subject_marks):
    """Calculate average and grade from a list of marks."""
    average = sum(subject_marks) / len(subject_marks)

    if average >= 90:
        final_grade = "A+"
    elif average >= 80:
        final_grade = "A"
    elif average >= 70:
        final_grade = "B"
    elif average >= 60:
        final_grade = "C"
    else:
        final_grade = "F"

    return average, final_grade


sample_marks = [86, 92, 78, 88, 90]
average_marks, final_grade = calculate_grade(sample_marks)

print("\nStudent Result")
print("Marks:", sample_marks)
print(f"Average: {average_marks:.2f}")
print("Final Grade:", final_grade)
