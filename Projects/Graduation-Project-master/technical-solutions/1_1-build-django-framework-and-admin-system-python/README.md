# Django, Python, and Smart-Home Database Research

This folder contains historical Django/admin-framework research notes, two small Python practice scripts, and SQL files for a smart-home database design.

## Files and purpose

- `python-practice-code/test_oop_py.py` and `test_py.py` — small Python learning exercises.
- `db_smart_home_sql/db_smart_home_v1.0.sql` — database schema/design script for the smart-home concept.
- `db_smart_home_sql/db_design_test.sql/` — supporting SQL experiments, table notes, and a secondary schema script.
- `README.md` — links and notes from the original Django learning research.

## Important distinction

No Django `manage.py`, Django settings module, installed-app configuration, or dependency manifest was found in this folder. The folder is therefore a **research and database-design archive**, not a complete Django web application that can be started with `python manage.py runserver`.

## Safe way to inspect the SQL

1. Read the SQL file before execution.
2. Import only into a disposable local MySQL database.
3. Use a dedicated local database account with limited privileges.
4. Do not point these historical scripts at a production database.
5. Keep local database passwords outside version control.

The SQL files may contain legacy schema assumptions and should be reviewed before use with a modern MySQL version.

## Python exercises

Run an individual practice script with a local Python 3 interpreter:

    python python-practice-code/test_py.py
    python python-practice-code/test_oop_py.py

These are educational scripts rather than a packaged Python application. No pinned Python dependencies are declared.
