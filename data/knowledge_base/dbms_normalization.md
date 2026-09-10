# Course: Database Management Systems (DBMS)
Domain: Technologies
Sub-Domain: Database Architecture & Design
Course ID: 203

## Module: Database Normalization & Integrity
Source: DBMS Course Curriculum — Module 4: Relational Database Design
Section: Lesson 4.1 to 4.4

### 1. Introduction to Normalization
Normalization is the systematic approach of decomposing tables to eliminate data redundancy (repetition) and undesirable characteristics like Insertion, Deletion, and Update Anomalies. It is a multi-step process that places database tables into normal forms (1NF, 2NF, 3NF, BCNF) based on functional dependencies between attributes.

### 2. Database Anomalies
Without normalization, relational tables suffer from severe anomalies:
1. **Update Anomaly**: If a student's address is stored in multiple records, updating it in one record but not others leads to inconsistent data.
2. **Insertion Anomaly**: We cannot insert a record for a course if no student has enrolled in it yet, because the Primary Key (e.g., student_id) cannot be null.
3. **Deletion Anomaly**: Deleting the only student enrolled in a course inadvertently deletes the entire course information.

### 3. Functional Dependency
A Functional Dependency (FD) is a relationship between attributes denoted as `X -> Y` (read as "X functionally determines Y"), meaning that for any two tuples with the same value of X, their value of Y must also be identical.
- **Trivial FD**: `X -> Y` where Y is a subset of X (e.g., `{student_id, name} -> student_id`).
- **Non-Trivial FD**: `X -> Y` where Y is not a subset of X (e.g., `student_id -> email`).

### 4. Normal Forms

#### First Normal Form (1NF)
A relation is in 1NF if and only if:
1. Every attribute contains only **atomic (indivisible) values**.
2. There are no repeating groups or multi-valued attributes (e.g., a phone_numbers column containing multiple comma-separated numbers violates 1NF).
3. Each column has a unique name and the order of rows does not matter.

#### Second Normal Form (2NF)
A relation is in 2NF if and only if:
1. It is already in **First Normal Form (1NF)**.
2. It contains **no partial dependency**. A partial dependency occurs when a non-prime attribute depends on only a subset of a composite candidate key rather than the whole key.
*Rule*: If the candidate key is composite (e.g., `{student_id, course_id}`), all non-key attributes (like `student_name`) must depend on both keys, not just `student_id`. If `student_name` depends only on `student_id`, it must be decomposed into a separate table.

#### Third Normal Form (3NF)
A relation is in 3NF if and only if:
1. It is already in **Second Normal Form (2NF)**.
2. It contains **no transitive dependency**. A transitive dependency occurs when a non-prime attribute depends on another non-prime attribute (`X -> Y` and `Y -> Z`, so `X -> Z` through Y).
*Formal Definition*: For every non-trivial functional dependency `X -> Y`, either:
- `X` is a Super Key, OR
- `Y` is a Prime Attribute (member of any candidate key).

#### Boyce-Codd Normal Form (BCNF)
BCNF is a stricter version of 3NF, often called 3.5NF.
A relation is in BCNF if and only if:
For every non-trivial functional dependency `X -> Y`, **X MUST be a Super Key**.
Unlike 3NF, BCNF does not allow `Y` to be a prime attribute if `X` is not a super key. Every relation in BCNF is in 3NF, but not all 3NF relations are in BCNF.

### 5. ACID Properties in DBMS Transactions
A transaction is a logical unit of work. To ensure integrity, transactions must satisfy the ACID properties:
1. **Atomicity**: The "all-or-nothing" rule. Either all operations of the transaction complete successfully, or the entire transaction is rolled back to its initial state.
2. **Consistency**: The database must remain in a valid state before and after the transaction, respecting all schema constraints, cascades, and integrity rules.
3. **Isolation**: Concurrent execution of transactions yields the same database state as if they were executed serially. Common isolation levels include Read Uncommitted, Read Committed, Repeatable Read, and Serializable.
4. **Durability**: Once a transaction is committed, its changes are permanently written to non-volatile storage and survive any subsequent system crash.

### 6. SQL Joins Summary
- **INNER JOIN**: Returns only matching rows where join predicate is satisfied in both tables.
- **LEFT (OUTER) JOIN**: Returns all rows from left table and matching rows from right table (fills NULL where no match).
- **RIGHT (OUTER) JOIN**: Returns all rows from right table and matching rows from left table.
- **FULL (OUTER) JOIN**: Returns all rows from both tables, filling NULLs where no join match exists.
