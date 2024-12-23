Description:
This Python application provides a user-friendly interface for managing a library's book catalog. Built using tkinter for the graphical user interface and pandas for data handling, the application allows users to view, search, and (if logged in as an admin) edit the book catalog data stored in an Excel file.
Functionality:
Data Handling:
Loads and saves book data from and to Excel files (.xlsx).
Uses pandas DataFrames to efficiently manage tabular data.
Supports creating new, opening, and loading existing data files.

User Interface:
Utilizes tkinter for creating the application's window and widgets.
Displays the book catalog in a ttk.Treeview table with column headers.
Includes a search bar for filtering books by any term in any column.
Provides button that filter by a specific column
Has a menu for file operations (new, open, backup, load).
Displays the currently loaded file path and statistics at the bottom of the window.
Implements a custom style for a modern look.
User Roles:
Student Users: Can view and search the book catalog.

Librarian (Admin) Users:
Can log in using a password.
Can edit, add, delete books, and save changes in the data (using the "Edit Table" button)
Can view a dashboard with statistics (Total books, books by genre).

Features:
File Management:
Users can load new files and the last file will be saved in config.json to load next time the app run
Creates backup copies of the catalog file before making changes to it.

Data Editing:
Admin users can edit book details, add new books, and delete books using a separate editing window.
Uses a checkbox column to allow selection of rows for deletion.
Utilizes double-click to edit cell value

Search:
Real-time filtering using the search bar.
Search by column option using buttons.
Configuration:
Persists application settings, such as the last opened file, using a config.json file.
Custom Styles:
Implements a custom style using ttk.Style to create a better-looking interface with colors.
Technologies Used:
Python: The primary programming language.
tkinter: For creating the graphical user interface (GUI).
pandas: For data manipulation and handling Excel files.
tkinter.ttk: For styled widgets (modern look).
os: For file path manipulation and working with the operating system.
shutil: For backup functionality (copying files).
json: For saving configuration.
Additional Notes:
The code is designed with some error handling (using try...except blocks).
The application uses a basic password system for admin login ("password123").
Improvements:
Robust password management: Consider using a more secure password storage/handling method.
Better data validation: Currently no validation is implemented for data changes.
Advanced search: Consider implementing search functionality with more filters, etc.
Advanced UI: Creating a more advance UI would create a better experience.
