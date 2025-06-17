import tkinter as tk
from tkinter import ttk, filedialog
import os
import threading
import time
import logging
import csv
from concurrent.futures import ThreadPoolExecutor
import platform
import subprocess
import sys

# Configure logging
logging.basicConfig(filename="treesize.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

class DirectoryScanner:
    """Handles directory scanning logic for TreeSizeApp."""
    
    def __init__(self, app):
        self.app = app
        self.cancel_flag = False

    def scan(self, path):
        """Scans a directory and returns folder sizes and file counts.

        Args:
            path (str): Directory path to scan.

        Returns:
            dict: Dictionary mapping folder names to (size, files) tuples.
        """
        results = {}
        try:
            for item in os.scandir(path):
                if self.cancel_flag:
                    return {}
                if item.is_dir(follow_symlinks=False):
                    size, files = self.get_folder_info(item.path)
                    results[item.name] = (size, files)
        except (PermissionError, FileNotFoundError, OSError) as e:
            logging.error(f"Error scanning {path}: {e}")
        return results

    def get_folder_info(self, directory):
        """Recursively calculates total size and file count in a directory.

        Args:
            directory (str): Directory path to analyze.

        Returns:
            tuple: (total_size, total_files)
        """
        total_size = 0
        total_files = 0
        try:
            for item in os.scandir(directory):
                if self.cancel_flag:
                    return 0, 0
                if item.is_file(follow_symlinks=False):
                    total_size += item.stat(follow_symlinks=False).st_size
                    total_files += 1
                elif item.is_dir(follow_symlinks=False):
                    size, files = self.get_folder_info(item.path)
                    total_size += size
                    total_files += files
        except (PermissionError, FileNotFoundError, OSError):
            pass
        return total_size, total_files

class TreeSizeApp(tk.Tk):
    """A Tkinter application to display directory sizes and file counts in a file explorer-like interface."""
    
    def __init__(self):
        super().__init__()
        self.title("Cleaner")
        self.geometry("800x600")

        # Initialize data
        self.item_data = {}
        self.cache = {}
        self.sort_by = "size"
        self.sort_descending = True
        self.last_path = None  # No initial directory
        self.scanner = DirectoryScanner(self)
        self.cancel_scan_flag = False
        self.executor = None  # To manage ThreadPoolExecutor

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # --- Create GUI Elements ---

        # Top frame for buttons and filters
        self.top_frame = ttk.Frame(self, padding="5")
        self.top_frame.pack(side="top", fill="x")

        # Select Directory button
        self.select_button = ttk.Button(self.top_frame, text="Select Directory", command=self.select_directory)
        self.select_button.pack(side="left", padx=5)

        # Up button
        self.up_button = ttk.Button(self.top_frame, text="Up", command=self.navigate_up, state="disabled")
        self.up_button.pack(side="left", padx=5)

        # Cancel button
        self.cancel_button = ttk.Button(self.top_frame, text="Cancel", command=self.cancel_scan, state="disabled")
        self.cancel_button.pack(side="left", padx=5)

        # Refresh button
        self.refresh_button = ttk.Button(self.top_frame, text="Refresh", command=self.refresh_scan)
        self.refresh_button.pack(side="left", padx=5)

        # Export button
        self.export_button = ttk.Button(self.top_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(side="left", padx=5)

        # Open in Explorer button
        self.open_explorer_button = ttk.Button(self.top_frame, text="Open in Explorer", command=self.open_in_explorer)
        self.open_explorer_button.pack(side="left", padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.top_frame, mode='indeterminate')
        self.progress.pack(side="left", padx=5)
        self.progress.pack_forget()

        # Search bar
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.top_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=5)
        self.search_var.trace("w", self.filter_by_search)

        # Filter frame
        self.filter_frame = ttk.Frame(self.top_frame)
        self.filter_frame.pack(side="left", padx=5)
        ttk.Label(self.filter_frame, text="Min Size (MB):").pack(side="left")
        self.filter_size = ttk.Entry(self.filter_frame, width=10)
        self.filter_size.pack(side="left", padx=2)
        ttk.Button(self.filter_frame, text="Apply Filter", command=self.apply_filter).pack(side="left")

        # Treeview frame
        self.tree_frame = ttk.Frame(self, padding="5")
        self.tree_frame.pack(side="top", fill="both", expand=True)

        # Treeview widget
        self.tree = ttk.Treeview(self.tree_frame, columns=("size", "files"), selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configure Treeview columns
        self.tree.heading("#0", text="Directory", command=lambda: self.sort_by_column("#0", False))
        self.tree.heading("size", text="Size ▼", command=lambda: self.sort_by_column("size", True))
        self.tree.heading("files", text="Files", command=lambda: self.sort_by_column("files", True))

        self.tree.column("#0", width=400, anchor="w", stretch=True)
        self.tree.column("size", width=150, anchor="e", stretch=True)
        self.tree.column("files", width=100, anchor="e", stretch=True)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Bind events
        self.tree.bind("<Button-1>", self.navigate_into_directory)  # Single-click to navigate
        self.tree.bind("<Double-1>", self.expand_directory)  # Double-click to expand

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding="2")
        self.status_bar.pack(side="bottom", fill="x")
        self.status_var.set("Select a directory to begin.")

        # Handle window close for graceful exit
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handles cleanup when the window is closed."""
        self.cancel_scan_flag = True
        self.scanner.cancel_flag = True
        if self.executor:
            self.executor.shutdown(wait=False)  # Forcefully terminate threads
        self.destroy()  # Destroy Tkinter window
        sys.exit(0)  # Ensure complete program exit

    def select_directory(self):
        """Opens a directory dialog and starts scanning."""
        path = filedialog.askdirectory()
        if path:
            if path in self.cache:
                self.populate_tree_from_cache(path)
            else:
                self.scan_directory(path)

    def scan_directory(self, path):
        """Scans the selected directory and populates the tree.

        Args:
            path (str): Directory path to scan.
        """
        start_time = time.time()
        self.last_path = path
        # Clear previous results
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.item_data.clear()

        # Disable sorting and buttons
        self.tree.heading("size", command=None)
        self.tree.heading("#0", command=None)
        self.tree.heading("files", command=None)
        self.cancel_button.configure(state="normal")
        self.up_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        self.cancel_scan_flag = False

        self.status_var.set(f"Scanning: {path}...")
        self.progress.pack(side="left", padx=5)
        self.progress.start()

        try:
            self.executor = ThreadPoolExecutor(max_workers=4)
            futures = []
            update_counter = 0
            for item in os.scandir(path):
                if item.is_dir(follow_symlinks=False):
                    node = self.tree.insert("", "end", text=item.name, values=("Calculating...", ""), open=False)
                    self.item_data[node] = {'raw_size': 0, 'raw_files': 0}
                    futures.append(self.executor.submit(self.scanner.get_folder_info, item.path))
                    update_counter += 1
                    if update_counter % 10 == 0:
                        self.update_idletasks()
            
            for node, future in zip(self.tree.get_children(), futures):
                if self.cancel_scan_flag:
                    break
                total_size, total_files = future.result()
                self.item_data[node] = {'raw_size': total_size, 'raw_files': total_files}
                self.tree.item(node, values=(self.format_size(total_size), f"{total_files:,}"))
                self.update_idletasks()

            # Cache results
            self.cache[path] = {self.tree.item(node, "text"): (data['raw_size'], data['raw_files']) 
                               for node, data in self.item_data.items()}
            
            # Calculate totals
            total_size = sum(data["raw_size"] for data in self.item_data.values())
            total_files = sum(data["raw_files"] for data in self.item_data.values())
            
            end_time = time.time()
            self.status_var.set(f"Scan complete in {end_time - start_time:.2f} seconds. "
                               f"Total: {self.format_size(total_size)}, {total_files:,} files. "
                               f"Current: {path}")

        except PermissionError as e:
            logging.error(f"Permission denied: {path}")
            self.status_var.set(f"Error: Permission denied to access some folders. Current: {path}")
        except Exception as e:
            logging.error(f"Error in scan_directory: {e}")
            self.status_var.set(f"An error occurred: {e}. Current: {path}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.cancel_button.configure(state="disabled")
            self.up_button.configure(state="normal")
            self.select_button.configure(state="normal")
            self.tree.heading("size", text="Size ▼", command=lambda: self.sort_by_column("size", True))
            self.tree.heading("#0", text="Directory", command=lambda: self.sort_by_column("#0", False))
            self.tree.heading("files", text="Files", command=lambda: self.sort_by_column("files", True))
            self.sort_by_column("size", True, initial_sort=True)
            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None

    def populate_tree_from_cache(self, path):
        """Populates the Treeview from cached data.

        Args:
            path (str): Directory path to load from cache.
        """
        self.last_path = path
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.item_data.clear()
        for name, (size, files) in self.cache[path].items():
            node = self.tree.insert("", "end", text=name, values=(self.format_size(size), f"{files:,}"), open=False)
            self.item_data[node] = {'raw_size': size, 'raw_files': files}
        self.sort_by_column("size", True, initial_sort=True)
        self.status_var.set(f"Loaded from cache: {path}")

    def sort_by_column(self, col, is_numeric, initial_sort=False):
        """Sorts Treeview items by a column.

        Args:
            col (str): Column identifier.
            is_numeric (bool): Whether the column contains numeric data.
            initial_sort (bool): Whether this is the initial sort after scanning.
        """
        if not initial_sort and col == self.sort_by:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_descending = True
        self.sort_by = col
        
        # Update heading text
        self.tree.heading("size", text="Size")
        self.tree.heading("#0", text="Directory")
        self.tree.heading("files", text="Files")
        arrow = "▼" if self.sort_descending else "▲"
        self.tree.heading(col, text=f"{col.capitalize() if col != '#0' else 'Directory'} {arrow}")

        # Sort items
        if is_numeric:
            data_key = 'raw_size' if col == 'size' else 'raw_files'
            l = [(self.item_data[item_id].get(data_key, 0), item_id) for item_id in self.tree.get_children('')]
        else:
            l = [(self.tree.item(item_id, 'text').lower(), item_id) for item_id in self.tree.get_children('')]

        l.sort(reverse=self.sort_descending)

        # Rearrange items
        for index, (val, item_id) in enumerate(l):
            self.tree.move(item_id, '', index)

    def expand_directory(self, event):
        """Expands a directory to show subdirectories on double-click, sorted by size.

        Args:
            event: Tkinter event object.
        """
        item = self.tree.identify_row(event.y)
        if not item or self.tree.identify_element(event.x, event.y) not in ("image", "text"):
            return
        # Build the full path
        path_parts = []
        current_item = item
        while current_item:
            path_parts.append(self.tree.item(current_item, "text"))
            current_item = self.tree.parent(current_item)
        path_parts.reverse()
        full_path = os.path.join(self.last_path, *path_parts)
        
        # Clear existing children to refresh
        for child in self.tree.get_children(item):
            self.tree.delete(child)
        
        try:
            # Scan subdirectories
            subdirs = {}
            for subitem in os.scandir(full_path):
                if subitem.is_dir(follow_symlinks=False):
                    total_size, total_files = self.scanner.get_folder_info(subitem.path)
                    subdirs[subitem.name] = {'raw_size': total_size, 'raw_files': total_files}
            
            # Sort subdirectories by size
            sorted_subdirs = sorted(subdirs.items(), key=lambda x: x[1]['raw_size'], reverse=True)
            
            # Populate Treeview
            for name, data in sorted_subdirs:
                node = self.tree.insert(item, "end", text=name, values=(self.format_size(data['raw_size']), f"{data['raw_files']:,}"), open=False)
                self.item_data[node] = data
            self.tree.item(item, open=True)  # Expand the node
        except Exception as e:
            logging.error(f"Error expanding directory {full_path}: {e}")
            self.status_var.set(f"Error expanding directory: {e}")

    def navigate_into_directory(self, event):
        """Navigates into a directory on single-click.

        Args:
            event: Tkinter event object.
        """
        item = self.tree.identify_row(event.y)
        if not item or self.tree.identify_element(event.x, event.y) not in ("image", "text"):
            return
        # Build the full path
        path_parts = []
        current_item = item
        while current_item:
            path_parts.append(self.tree.item(current_item, "text"))
            current_item = self.tree.parent(current_item)
        path_parts.reverse()
        full_path = os.path.join(self.last_path, *path_parts)
        
        # Check if directory exists and is accessible
        if os.path.isdir(full_path):
            if full_path in self.cache:
                self.populate_tree_from_cache(full_path)
            else:
                self.scan_directory(full_path)

    def navigate_up(self):
        """Navigates to the parent directory."""
        if self.last_path:
            parent_path = os.path.dirname(self.last_path)
            if os.path.isdir(parent_path) and parent_path != self.last_path:  # Avoid infinite loop at root
                if parent_path in self.cache:
                    self.populate_tree_from_cache(parent_path)
                else:
                    self.scan_directory(parent_path)
            else:
                self.status_var.set("Cannot navigate up: already at root.")
        else:
            self.status_var.set("No directory selected.")

    def open_in_explorer(self):
        """Opens the selected directory in the system's file explorer."""
        item = self.tree.selection()
        if not item:
            self.status_var.set("No directory selected.")
            return
        item = item[0]
        # Build the full path
        path_parts = []
        current_item = item
        while current_item:
            path_parts.append(self.tree.item(current_item, "text"))
            current_item = self.tree.parent(current_item)
        path_parts.reverse()
        full_path = os.path.join(self.last_path, *path_parts)
        
        try:
            if platform.system() == "Windows":
                os.startfile(full_path)
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", full_path], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", full_path], check=True)
            else:
                self.status_var.set("Unsupported platform for opening directory.")
                return
            self.status_var.set(f"Opened {full_path} in file explorer.")
        except Exception as e:
            logging.error(f"Error opening directory {full_path}: {e}")
            self.status_var.set(f"Error opening directory: {e}")

    def cancel_scan(self):
        """Cancels the current scan."""
        self.cancel_scan_flag = True
        self.scanner.cancel_flag = True
        if self.executor:
            self.executor.shutdown(wait=False)  # Forcefully terminate threads
            self.executor = None
        self.status_var.set("Scan cancelled.")
        self.cancel_button.configure(state="disabled")
        self.up_button.configure(state="normal")
        self.select_button.configure(state="normal")
        self.progress.stop()
        self.progress.pack_forget()

    def refresh_scan(self):
        """Refreshes the scan for the current directory."""
        if self.last_path:
            # Clear cache for the current path to force a rescan
            if self.last_path in self.cache:
                del self.cache[self.last_path]
            self.scan_directory(self.last_path)
        else:
            self.status_var.set("No directory selected.")

    def export_to_csv(self):
        """Exports Treeview data to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Directory", "Size (Bytes)", "Files"])
                    for item in self.tree.get_children():
                        name = self.tree.item(item, "text")
                        size = self.item_data[item]["raw_size"]
                        files = self.item_data[item]["raw_files"]
                        writer.writerow([name, size, files])
                self.status_var.set(f"Exported to {file_path}")
            except Exception as e:
                logging.error(f"Error exporting CSV: {e}")
            self.status_var.set(f"Error exporting CSV: {e}")

    def apply_filter(self):
        """Filters directories by minimum size."""
        try:
            min_size_mb = float(self.filter_size.get()) * 1024 * 1024
        except ValueError:
            min_size_mb = 0
        for item in self.tree.get_children():
            size = self.item_data[item]["raw_size"]
            if size < min_size_mb:
                self.tree.delete(item)
            else:
                self.tree.item(item, values=(self.format_size(self.item_data[item]["raw_size"]), 
                                            f"{self.item_data[item]['raw_files']:,}"))
        self.status_var.set(f"Filtered directories smaller than {min_size_mb/1024/1024:.2f} MB")

    def filter_by_search(self, *args):
        """Filters Treeview items by search term."""
        search_term = self.search_var.get().lower()
        for item in self.tree.get_children():
            name = self.tree.item(item, "text").lower()
            if search_term in name:
                self.tree.item(item, tags=())
            else:
                self.tree.item(item, tags=("hidden",))
        self.tree.tag_configure("hidden", foreground="gray")

    def format_size(self, size_bytes):
        """Formats a size in bytes to a human-readable string.

        Args:
            size_bytes (int): Size in bytes.

        Returns:
            str: Formatted size string.
        """
        if size_bytes is None:
            return "N/A"
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/1024**2:.2f} MB"
        elif size_bytes < 1024**4:
            return f"{size_bytes/1024**3:.2f} GB"
        else:
            return f"{size_bytes/1024**4:.2f} TB"

if __name__ == "__main__":
    app = TreeSizeApp()
    app.mainloop()