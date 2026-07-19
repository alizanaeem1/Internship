"""
Week 1 - Data Structures and Functions
This file covers Python collections, functions, and functional tools.
"""

from math import sqrt
from statistics import mean


# ---------------------------------------------------------
# 1. LISTS
# ---------------------------------------------------------

courses = ["Python", "Database", "Software Engineering"]
courses.append("Artificial Intelligence")
courses.insert(1, "Data Structures")
courses.remove("Database")

print("Courses:", courses)
print("First Course:", courses[0])
print("Last Course:", courses[-1])
print("Slice:", courses[1:3])

numbers = [12, 4, 18, 7, 10]
numbers.sort()
print("Sorted Numbers:", numbers)

numbers.reverse()
print("Reverse Sorted:", numbers)

copied_numbers = numbers.copy()
print("Copied List:", copied_numbers)


# ---------------------------------------------------------
# 2. TUPLES
# ---------------------------------------------------------

student_record = ("Aliza", "BS Software Engineering", 3.60)

name, program, cgpa = student_record

print("\nTuple Data")
print("Name:", name)
print("Program:", program)
print("CGPA:", cgpa)

single_item_tuple = ("Python",)
print("Single Item Tuple:", single_item_tuple)


# ---------------------------------------------------------
# 3. SETS
# ---------------------------------------------------------

frontend_skills = {"HTML", "CSS", "JavaScript", "Flutter"}
backend_skills = {"Python", "Node.js", "JavaScript"}

print("\nSet Operations")
print("Union:", frontend_skills | backend_skills)
print("Intersection:", frontend_skills & backend_skills)
print("Difference:", frontend_skills - backend_skills)
print("Symmetric Difference:", frontend_skills ^ backend_skills)

frontend_skills.add("React")
frontend_skills.discard("CSS")

print("Updated Frontend Skills:", frontend_skills)


# ---------------------------------------------------------
# 4. DICTIONARIES
# ---------------------------------------------------------

student = {
    "name": "Aliza Naeem",
    "program": "BS Software Engineering",
    "semester": 6,
    "cgpa": 3.60,
    "skills": ["Python", "Flutter", "Git"],
}

print("\nDictionary")
print("Name:", student["name"])
print("Program:", student.get("program"))

student["semester"] = 7
student["university"] = "COMSATS University Islamabad"

for key, value in student.items():
    print(f"{key}: {value}")

removed_value = student.pop("semester")
print("Removed Semester:", removed_value)


# ---------------------------------------------------------
# 5. BASIC FUNCTIONS
# ---------------------------------------------------------

def greet_user(name):
    """Return a welcome message."""
    return f"Welcome, {name}!"


def add_numbers(first_number, second_number):
    """Return the sum of two numbers."""
    return first_number + second_number


print("\nFunctions")
print(greet_user("Aliza"))
print("Sum:", add_numbers(12, 8))


# ---------------------------------------------------------
# 6. DEFAULT AND KEYWORD ARGUMENTS
# ---------------------------------------------------------

def create_profile(name, role="Intern", experience=0):
    return {
        "name": name,
        "role": role,
        "experience": experience,
    }


profile_one = create_profile("Aliza")
profile_two = create_profile(
    name="Sara",
    experience=1,
    role="Python Developer",
)

print("\nProfiles")
print(profile_one)
print(profile_two)


# ---------------------------------------------------------
# 7. *ARGS AND **KWARGS
# ---------------------------------------------------------

def calculate_total(*values):
    """Return the total of any number of values."""
    return sum(values)


def display_information(**details):
    """Print key-value information."""
    for key, value in details.items():
        print(f"{key.title()}: {value}")


print("\n*args")
print("Total:", calculate_total(10, 20, 30, 40))

print("\n**kwargs")
display_information(
    name="Aliza",
    field="Software Engineering",
    skill="Python",
)


# ---------------------------------------------------------
# 8. RETURNING MULTIPLE VALUES
# ---------------------------------------------------------

def analyze_numbers(values):
    minimum = min(values)
    maximum = max(values)
    average = sum(values) / len(values)
    return minimum, maximum, average


minimum, maximum, average = analyze_numbers([12, 45, 8, 31, 27])

print("\nNumber Analysis")
print("Minimum:", minimum)
print("Maximum:", maximum)
print("Average:", average)


# ---------------------------------------------------------
# 9. LAMBDA FUNCTIONS
# ---------------------------------------------------------

square = lambda number: number ** 2
is_even = lambda number: number % 2 == 0

print("\nLambda Functions")
print("Square of 7:", square(7))
print("Is 12 even?", is_even(12))


# ---------------------------------------------------------
# 10. MAP, FILTER, AND SORTED
# ---------------------------------------------------------

values = [1, 2, 3, 4, 5, 6]

squared_values = list(map(lambda value: value ** 2, values))
even_values = list(filter(lambda value: value % 2 == 0, values))

employees = [
    {"name": "Ali", "salary": 65000},
    {"name": "Sara", "salary": 80000},
    {"name": "Hina", "salary": 72000},
]

sorted_employees = sorted(
    employees,
    key=lambda employee: employee["salary"],
    reverse=True,
)

print("\nFunctional Tools")
print("Squared Values:", squared_values)
print("Even Values:", even_values)
print("Sorted Employees:", sorted_employees)


# ---------------------------------------------------------
# 11. RECURSION
# ---------------------------------------------------------

def factorial(number):
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if number in (0, 1):
        return 1
    return number * factorial(number - 1)


print("\nRecursion")
print("Factorial of 5:", factorial(5))


# ---------------------------------------------------------
# 12. NESTED FUNCTIONS AND CLOSURES
# ---------------------------------------------------------

def create_multiplier(multiplier):
    def multiply(value):
        return value * multiplier
    return multiply


double = create_multiplier(2)
triple = create_multiplier(3)

print("\nClosures")
print("Double 8:", double(8))
print("Triple 8:", triple(8))


# ---------------------------------------------------------
# 13. GENERATORS
# ---------------------------------------------------------

def generate_even_numbers(limit):
    for number in range(0, limit + 1, 2):
        yield number


print("\nGenerator")
for value in generate_even_numbers(10):
    print(value, end=" ")
print()


# ---------------------------------------------------------
# 14. DECORATORS
# ---------------------------------------------------------

def log_execution(function):
    def wrapper(*args, **kwargs):
        print(f"Running function: {function.__name__}")
        result = function(*args, **kwargs)
        print("Function completed")
        return result
    return wrapper


@log_execution
def multiply_numbers(a, b):
    return a * b


print("\nDecorator")
print("Result:", multiply_numbers(6, 7))


# ---------------------------------------------------------
# 15. IMPORTED MODULES
# ---------------------------------------------------------

print("\nImported Modules")
print("Square Root of 81:", sqrt(81))
print("Mean:", mean([80, 85, 90, 95]))


# ---------------------------------------------------------
# 16. MINI PROJECT: STUDENT PERFORMANCE ANALYSIS
# ---------------------------------------------------------

def calculate_student_performance(student_scores):
    """
    Calculate average, highest, lowest, and status
    for a dictionary of subject scores.
    """
    scores = list(student_scores.values())
    average_score = sum(scores) / len(scores)

    performance = {
        "average": round(average_score, 2),
        "highest": max(scores),
        "lowest": min(scores),
        "status": "Pass" if average_score >= 60 else "Fail",
    }

    return performance


subject_scores = {
    "Programming": 88,
    "Database": 82,
    "Software Quality": 91,
    "Operating Systems": 76,
}

performance = calculate_student_performance(subject_scores)

print("\nStudent Performance")
for subject, score in subject_scores.items():
    print(f"{subject}: {score}")

for key, value in performance.items():
    print(f"{key.title()}: {value}")
