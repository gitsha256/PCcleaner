Note: Avoid deleting symstem folder or folders you dont understan what it does.
Folder Size Viewer
This Python application provides a file explorer-like interface to view folder sizes and file counts, helping you identify large directories to manage disk space effectively. You can navigate through folders, see their sizes, and decide which files or folders to delete at your discretion. The app includes features like directory selection, navigation, filtering, searching, and exporting data, all while ensuring efficient performance and proper resource cleanup.
Features
Select Directory: Choose a starting folder using a directory selection dialog to begin analyzing its contents.

Folder Navigation:
Single-click a folder to navigate into it, displaying its subfolders with their sizes and file counts.

Double-click a folder to expand it, showing its subfolders (sorted by size) without navigating away.

"Up" button to navigate to the parent directory, with root directory checks to prevent errors.

Size and File Count Display:
Shows folder sizes in human-readable formats (B, KB, MB, GB, TB).

Displays the number of files in each folder.

Sorts folders by size by default, with options to sort by name or file count.

Filtering and Search:
Filter folders by minimum size (in MB) to focus on large directories.

Search for folders by name to quickly find specific directories.

Export to CSV: Save folder data (name, size in bytes, file count) to a CSV file for further analysis.

Open in Explorer: Open the selected folder in your system's file explorer for direct file management.

Refresh and Cancel:
Refresh the current directory to rescan its contents.

Cancel ongoing scans to stop processing large directories.

Performance Optimizations:
Caches scanned directories to speed up navigation to previously viewed folders.

Uses parallel scanning with multiple threads for faster processing of large directories.

Error Handling: Logs errors (e.g., permission issues) to foldersize.log for troubleshooting.

Graceful Exit: Properly terminates threads and frees memory when closing the app, ensuring no resource leaks.

Requirements
Python: Version 3.6 or higher.

Operating System: Windows, Linux, or macOS.

Dependencies: Uses only Python's standard library (no external packages required).

Installation
Install Python:
Download and install Python 3.6+ from python.org.

Ensure Python is added to your system's PATH during installation.

Download the Code:
Save the Python script (e.g., pcCleaner.py) to a directory of your choice.

Alternatively, clone or download this repository if hosted on a platform like GitHub.

Verify Setup:
Open a terminal or command prompt.

Run python --version to confirm Python is installed correctly.

Usage
Run the Application:
Navigate to the directory containing the script in your terminal or command prompt.

Execute the script:
bash

python folder_size_viewer.py

The app window will open, displaying an empty list with the message "Select a directory to begin."

Select a Starting Directory:
Click the "Select Directory" button.

Choose a folder (e.g., C:\Users or /home) using the dialog.

The app will scan the folder and display its subfolders, sorted by size.

Navigate Folders:
Single-click a folder to navigate into it, updating the list to show its subfolders.

Double-click a folder to expand it, revealing its subfolders (sorted by size) without leaving the current view.

Click the "Up" button to go to the parent directory.

Use the status bar to track the current directory and scan progress.

Manage Disk Space:
Identify large folders by their sizes (displayed in the "Size" column).

Click "Open in Explorer" to open a folder in your system's file explorer, where you can delete files or folders as needed.

Use the "Refresh" button to rescan the current directory if its contents change.

Filter and Search:
Enter a size (in MB) in the "Min Size" field and click "Apply Filter" to hide folders smaller than the specified size.

Type a folder name in the search bar to highlight matching folders.

Export Data:
Click "Export to CSV" to save the current folder list (name, size, file count) to a CSV file for analysis.

Cancel Scans:
Click "Cancel" during a scan of a large directory to stop the process.

Close the App:
Click the window's close button to exit. The app will clean up resources and terminate cleanly.

Example Workflow
Run the app and click "Select Directory" to choose C:\Users.

Single-click the "Documents" folder to navigate into it, seeing its subfolders sorted by size.

Double-click a subfolder (e.g., "Projects") to expand it and view its subfolders without navigating.

Identify a large folder (e.g., "OldBackups" at 10 GB).

Click "Open in Explorer" to open "OldBackups" and delete unnecessary files.

Click "Up" to return to C:\Users\Documents.

Export the folder list to a CSV file for record-keeping.

Close the app when done.

Troubleshooting
App Doesn't Start:
Ensure Python 3.6+ is installed and accessible via the command line.

Check for errors in the terminal where you ran the script.

Permission Errors:
Some folders (e.g., system directories) may be inaccessible. Errors are logged to foldersize.log in the script's directory.

Select a user-accessible folder (e.g., your home directory) to avoid issues.

Memory Issues:
The app is designed to free memory on exit. If memory usage persists, restart your Python environment or contact support with details.

Slow Scans:
Large directories with many files may take time to scan. Use the "Cancel" button to stop if needed.

Caching speeds up revisiting directories during navigation.

Notes
Folder Sizes: Sizes are calculated recursively, including all files and subfolders. Symlinks are ignored to prevent infinite loops.

Sorting: Subfolders are sorted by size in descending order when expanded. The main list defaults to size-based sorting but supports sorting by name or file count via column headers.

Cross-Platform: The app works on Windows, Linux, and macOS, with platform-specific file explorer integration.

Log File: Errors are saved to foldersize.log for debugging. Check this file if you encounter issues accessing folders.

Contributing
If you'd like to contribute to this project:
Fork or clone the repository (if hosted).

Create a new branch for your changes.

Submit a pull request with a description of your improvements.

Suggestions for enhancements (e.g., path display, navigation history, context menus) are welcome!
License
This project is open-source and available under the MIT License (LICENSE). Feel free to use, modify, and distribute the code as needed.
Acknowledgments
Built with Python's standard library, using Tkinter for the GUI and concurrent.futures for parallel processing.

Designed to help users like you manage disk space by identifying large folders for cleanup.

Notes on the README
Name: I used "Folder Size Viewer" as a descriptive name for the app, avoiding "TreeSize" as requested. If you prefer a different name (e.g., "Disk Space Analyzer"), let me know.

Purpose: Emphasized the app's role in helping you view folder sizes to decide which files to delete, aligning with your use case.

Structure: Organized into clear sections (Features, Requirements, Installation, Usage, etc.) for ease of use.

File Name: The log file is named foldersize.log to match the app's purpose. If you want a different log name, I can update it.

License: Assumed MIT License for openness; if you prefer another license or no license, I can adjust.

Usage Example: Included a workflow to illustrate how you might use the app to clean up disk space.

Troubleshooting: Addressed common issues like permission errors and slow scans, reflecting your concern about navigating the entire PC.

Next Steps
Save the README: Copy the above content into a file named README.md in the same directory as your script (e.g., folder_size_viewer.py).

Test the App: Ensure the app still meets your needs with the latest code (single-click navigation, double-click expansion, Up button).

Feedback: If you need changes to the README (e.g., different app name, additional sections, or specific instructions) or want enhancements to the app (e.g., a path display, back/forward history, or context menu), let me know!

Thank you for using the app, and I'm happy it helps you manage your disk space!

explain filtering options

disk cleanup tools

more concise instructions

