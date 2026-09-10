# Course: Python Programming
Domain: Skills Wise
Sub-Domain: Python
Course ID: 103

## Module: Core Python Syntax, Data Structures & Object-Oriented Programming
Source: Python Programming Comprehensive Curriculum — Lessons 1 to 6
Section: Core Concepts & Advanced Applications

### 1. Variables, Data Types and Mutability
Python is a dynamically typed, interpreted programming language.
- **Built-in Primitive Types**: `int`, `float`, `bool`, `str`.
- **Mutable Types**: `list`, `dict`, `set`, `bytearray`. Mutable objects can have their content modified in-place without altering their memory identity (`id()`).
- **Immutable Types**: `int`, `float`, `str`, `tuple`, `frozenset`. Any operation that modifies an immutable object creates a brand-new object in memory.

### 2. Control Flow and Iterators
- `if-elif-else`: Conditional branching based on truthy/falsy evaluation.
- `for` loop: Iterates over iterable objects using the Python iterator protocol (`__iter__()` and `__next__()`).
- `while` loop: Executes repeatedly while condition remains True.
- Loop control: `break` terminates loop, `continue` skips to next iteration, `else` block executes when loop completes without encountering `break`.

### 3. Functions, Arguments and Scope
- Functions are first-class citizens in Python; they can be passed as arguments, returned from functions, and assigned to variables.
- Variable scope follows the **LEGB rule**:
  1. **L**ocal: Inside current function.
  2. **E**nclosing: Any enclosing functions (closures).
  3. **G**lobal: Module-level variables.
  4. **B**uilt-in: Built-in Python identifiers (e.g., `len`, `range`).
- `*args`: Collects extra positional arguments into a `tuple`.
- `**kwargs`: Collects extra keyword arguments into a `dict`.
- Lambda expressions: Anonymous inline functions (`lambda x, y: x + y`).
- List comprehensions: Concise syntax for constructing lists: `[x**2 for x in items if x % 2 == 0]`.

### 4. Object-Oriented Programming (OOP) in Python
Python supports full object-oriented programming:
- **Class and Object**: A class is a blueprint for objects. Instances are initialized via the `__init__(self, ...)` constructor method.
- **Inheritance**: Subclasses inherit methods and attributes from parent classes: `class Student(Person):`. Multiple inheritance is supported via Method Resolution Order (MRO / C3 linearization algorithm).
- **Polymorphism**: Duck typing allows uniform interface execution across different object types ("If it walks like a duck and quacks like a duck, it is a duck").
- **Encapsulation**: Private attributes are denoted by a leading double underscore (e.g., `self.__balance`), invoking name mangling (`_ClassName__balance`). Protected attributes use a single underscore (`self._protected`).
- **Dunder (Magic) Methods**:
  - `__str__(self)`: Human-readable string representation (called by `str()` and `print()`).
  - `__repr__(self)`: Unambiguous representation intended for developers.
  - `__len__(self)`: Enables `len(obj)`.
  - `__getitem__(self, key)`: Enables indexing `obj[key]`.

### 5. Generators and Memory Efficiency
Generators produce sequences of values lazily on-demand using the `yield` keyword rather than allocating entire collections in RAM. They maintain local state between successive iterations and raise `StopIteration` upon exhaustion.
