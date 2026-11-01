# JavaCodes — Java Programs and Practice Archive

This folder contains **228 Java source files** collected across algorithms, data structures, console applications, desktop interfaces, and small utilities. It is a collection of independent examples, not a single Java application.

There is no shared Maven/Gradle build, package structure, or dependency manifest. Many programs are in the default package, some filenames contain spaces or hyphens, some source filenames do not match their public class name, and some files are exact copies of other examples. Compile and run one selected program at a time after checking its class name and dependencies.

## Project categories

### Data structures and algorithms

- `BSTVisualization.java` — interactive binary-search-tree visualization.
- `SinglyLinkedList.java`, `ReverseLinkedList.java`, `Merge_Two_Sorted_Linked_List.java` — linked-list operations.
- `SortingAlgos.java`, `Heapsort.java`, `Merge_Sort.java`, `Radix Sorting Algo.java` — sorting implementations.
- `4sum.java`, `Kadanes_Algorithm.java`, `Knapsack_algo.java`, `TopologicalSortGraph.java`, `Travelling Salesman Problem.java` — algorithm practice.
- `SudokuSolver.java`, `Nqueen.java`, `DPFibonacciNumber.java` — search and dynamic-programming exercises.

### Management and reservation applications

- `AirlineReservationSystem.java` — console-based flight/passenger/reservation example.
- `LibraryManagement.java` — console library-management example.
- `Employee Attendance System.java` — in-memory employee attendance prototype.
- `Hospital_scrapper.java` — despite the filename, the code is a console hospital/appointment management prototype; it does not scrape a hospital website.
- `MedicalStore.java`, `stock_management.java`, `ExpenseTracker.java` — inventory and expense examples.
- `Atm-simulator.java`, `Banking.java` — educational ATM/banking simulations.
- `Online_Exam_System.java`, `OnlineJavaTest.java`, `QuizApp.java` — quiz and exam examples.

### Swing / AWT desktop programs

- `LoginPage.java`, `BSTVisualization.java`, `CalculatorAWT.java`, `Calculator_frame.java`
- `textEditor.java`, `fileexplorer.java`, `Analog Clock.java`, `Age_Frame_Calculator.java`
- `breakOutBall.java`, `space-invader-game.java`, `mineswepper game.java`, `tik tak toe.java`

### Networking and utility examples

- `OpenWeatherMap.java` — OpenWeatherMap API example (uses the `OPENWEATHER_API_KEY` environment variable after this review).
- `Host-checker.java` — simple HTTP availability checker.
- `Web_Page_Source_Viewer.java`, `url.java`, `urlsourcegenerator.java` — URL/source utilities.
- `FibonacciGenerator.java`, `Java_password_generator.java`, `PasswordGenerator.java` — generators and small command-line tools.

### Password and security demonstrations

- `passowrd&notes.java` — Swing password/notes manager experiment.
- `Password Manager.java` — incomplete console password-manager scaffold.
- `PasswordUtil.java`, `File_Encryption.Java` — small security/cryptography examples.

**Security warning:** `passowrd&notes.java` uses the obsolete `PBEWithMD5AndDES` scheme, a fixed salt, and a very low iteration count. It should not be used to store real passwords. `Password Manager.java` is incomplete and does not implement secure master-password authentication, encrypted persistence, or safe storage. Treat all password-related examples as educational code only.

## Requirements

- JDK 8 or newer for many simple console examples.
- Some applet examples require an obsolete Java Applet environment and will not run in modern browsers/JDKs.
- Swing/AWT programs require a graphical desktop environment.
- Network examples require internet access and any documented API credentials.
- Individual dependencies, when present, must be reviewed in the corresponding source file; there is no common dependency manager.

## Compile and run one program

For a self-contained class whose public class name matches its filename:

```bash
mkdir -p out
javac -d out FibonacciGenerator.java
java -cp out FibonacciGenerator
```

For a Swing application, run it from a graphical desktop. For code with a package declaration, preserve the package output and launch it using the fully qualified class name.

Before compiling a file, check its package declaration, public class name, dependencies, and whether it contains demo credentials or insecure algorithms.

Do not try to compile every file in this folder with one `javac *.java` command: many examples have independent entry points, duplicate class definitions, and filename/package inconsistencies.

## Duplicate files

The archive contains **41 groups of byte-for-byte identical source files** (including many `- Copy` pairs). See [EXACT_DUPLICATES.md](./EXACT_DUPLICATES.md) for the full verified list. Duplicates are preserved for now; review references before deleting any.

## Improvement plan

1. Standardize class names and filenames and put each standalone example in its own package/directory.
2. Add unit tests for algorithms and edge cases.
3. Extract reusable models/services from the larger console programs.
4. Add persistence only where appropriate, using validated inputs and safe credential handling.
5. Replace legacy applets and obsolete crypto APIs before claiming modern compatibility.

## Review status

This first review adds a navigable index, documents exact duplicate source groups, improves the weather API example's credential/transport handling, and improves the host checker timeouts. The entire folder has not yet been compiled or manually tested.
