import pandas as pd
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import os
import shutil  # For backup functionality
import json # For saving configuration

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Catalog")
        self.CONFIG_FILE = "config.json"
        self.DATA_FILE = self.load_config().get("data_file", None) # Load file from config or None
        self.BACKUP_DIR = "backups"  # Directory for backups
        self.data = self.load_data()
        self.isAdmin = False
        self.main_tree = None
        self.current_file_label = None  # Label to display current file path
        self.admin_stats_label = None
        self.admin_dashboard_frame = None  # Frame for the admin dashboard
        self.stats_labels = {} # Dictionary to hold the label for the stats
        self.create_main_ui()
        self.create_menu()
        # Set a custom style
        self.style = ttk.Style(self)
        self.configure_style()

    def load_config(self):
      if os.path.exists(self.CONFIG_FILE):
         with open(self.CONFIG_FILE, 'r') as f:
           return json.load(f)
      return {}
    
    def save_config(self, config):
        with open(self.CONFIG_FILE, 'w') as f:
          json.dump(config, f)
    
    def configure_style(self):
        # Define colors
        primary_color = "#2c3e50"   # Dark blueish
        secondary_color = "#f0f0f0"  # Light gray
        highlight_color = "#3498db"  # Blue when selected
        button_color = "#34495e"       # Slightly darker blueish
        button_text_color = "black"    # Black text on buttons

        # Configure style for header
        self.style.configure("Treeview.Heading", font = ('Arial', 10, 'bold'), background=secondary_color, relief="flat", borderwidth = 0, padding = 5) # flat = no border
        # Configure style for table rows
        self.style.configure("Treeview", font=('Arial', 10), rowheight=25, background = "white", foreground = "black", highlightthickness=0)
        self.style.map("Treeview", background=[('selected', highlight_color)])
         # Configure style for buttons
        self.style.configure('TButton', font=('Arial', 10), padding=8, background=button_color, relief='flat', borderwidth=0, foreground=button_text_color) # flat = no border
        self.style.map('TButton', background=[('active', '#212529')]) # Change the background to a slightly darker black when hovered
    
    def create_menu(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command = self.new_file)
        file_menu.add_command(label="Open", command = self.open_file)
        file_menu.add_command(label="Load", command = self.load_new_file) # Load option added to menu
        file_menu.add_command(label="Take Backup", command = self.take_backup)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def new_file(self):
      new_file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes = [("Excel files", "*.xlsx")])
      if new_file_path:
          self.DATA_FILE = new_file_path
          self.data = pd.DataFrame()
          self.update_data(self.data)
          self.display_table(self, self.main_tree, False)
          self.update_current_file_label()
          self.update_admin_stats()
          self.save_config({"data_file": self.DATA_FILE})
          messagebox.showinfo("Info", "New file created")
          
    def load_new_file(self):
        # Load new file, and prompt user to pick one.
          file_path = filedialog.askopenfilename(defaultextension=".xlsx", filetypes = [("Excel files", "*.xlsx")])
          if file_path:
              self.DATA_FILE = file_path
              self.data = self.load_data()
              self.display_table(self, self.main_tree, False)
              self.update_current_file_label()
              self.update_admin_stats()
              self.save_config({"data_file": self.DATA_FILE})
              messagebox.showinfo("Info", "File loaded")
          
    
    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".xlsx", filetypes = [("Excel files", "*.xlsx")])
        if file_path:
            self.DATA_FILE = file_path
            self.data = self.load_data()
            self.display_table(self, self.main_tree, False)
            self.update_current_file_label()
            self.update_admin_stats()
            self.save_config({"data_file": self.DATA_FILE})
            messagebox.showinfo("Info", "File loaded")
    
    def take_backup(self):
       if not os.path.exists(self.BACKUP_DIR):
            os.makedirs(self.BACKUP_DIR)
       backup_file = os.path.join(self.BACKUP_DIR, f"backup_{os.path.basename(self.DATA_FILE)}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}")
       try:
            shutil.copy2(self.DATA_FILE, backup_file)
            messagebox.showinfo("Success", f"Backup created: {os.path.basename(backup_file)}")
       except Exception as e:
            messagebox.showerror("Error", f"Error Creating Backup: {e}")

    def login_check(self):
        password = simpledialog.askstring("Password", "Enter Librarian Password:", show="*")
        if password == "password123":
            self.isAdmin = True
            messagebox.showinfo("Success", "Logged In as Librarian")
            self.update_admin_stats()
            if self.admin_dashboard_frame:
               self.admin_dashboard_frame.pack(fill='x')
            return True
        else:
            self.isAdmin = False
            messagebox.showinfo("Error", "Invalid password. Student access granted.")
            self.update_admin_stats()
            if self.admin_dashboard_frame:
               self.admin_dashboard_frame.pack_forget()
            return False
        
    def load_data(self):
      if self.DATA_FILE is None:
        return pd.DataFrame()
      try:
        return pd.read_excel(self.DATA_FILE)
      except Exception as e:
        messagebox.showerror("Error", f"Error loading data: {e}")
        return pd.DataFrame()

    def update_data(self, new_data):
        try:
            new_data.to_excel(self.DATA_FILE, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {e}")
    
    def display_table(self, root, tree = None, show = True, data = None):
        if data is None:
            data = self.data
        if tree is not None: # if tree is passed as argument delete all data in it before populating
            for i in tree.get_children():
                tree.delete(i)
        else:
            tree = ttk.Treeview(root, columns = ["Select"] + list(data.columns), show = "headings", style = "Treeview")
            tree.heading("Select", text = "Select")
            tree.column("Select", width=50, anchor='center')  # Adjust width if needed
            for col in data.columns:
               tree.heading(col, text = col)
        for i, row in data.iterrows():
           tree.insert("","end", values = [0] + row.tolist()) # 0 = unselected checkbox
        if show:
            tree.pack(fill="both", expand=True)
        return tree

    def create_main_ui(self):
        # Check if no file was loaded before
      if self.DATA_FILE is None:
        tk.Label(self, text = "Please Load a File to Continue.").pack(pady = 20)
        return

      if self.data.empty:
        messagebox.showerror("Error", "No Data Found, Please contact librarian to add data")
        return

      #Admin Dashboard Frame
      self.admin_dashboard_frame = tk.Frame(self)
      self.admin_dashboard_frame.pack(fill = "x")
      self.admin_dashboard_frame.pack_forget()

      #Create the Stats Labels (hide when user is not admin)
      tk.Label(self.admin_dashboard_frame, text = "Admin Dashboard", font = ("Arial", 12, "bold")).pack(pady = 10)
      self.stats_labels["total"] = tk.Label(self.admin_dashboard_frame, text = "")
      self.stats_labels["total"].pack(anchor = "w")
      self.stats_labels["genre"] = tk.Label(self.admin_dashboard_frame, text = "")
      self.stats_labels["genre"].pack(anchor = "w")
    
      # Search Bar
      search_var = tk.StringVar()
      search_entry = tk.Entry(self, textvariable = search_var)
      search_entry.pack(pady = 10)
    
      # Add placeholder
      search_entry.insert(0, "Search Now")
      search_entry.bind("<FocusIn>", lambda event: self.on_focus_in(search_entry))
      search_entry.bind("<FocusOut>", lambda event: self.on_focus_out(search_entry, "Search Now"))
      
      # Search Buttons
      if not self.isAdmin:
          button_frame = tk.Frame(self)
          button_frame.pack(pady=5)
          
          search_types = ["Title", "Author", "Genre", "ISBN", "Publisher", "Publication Year"]
          for search_type in search_types:
             button = ttk.Button(button_frame, text = search_type, command=lambda st = search_type: self.search_data_by_column(search_var, st) , style = "TButton")
             button.pack(side = "left", padx = 2)
      
      def search_data(*args):
        search_term = search_var.get()
        if search_term and search_term != "Search Now":
            filtered_data = self.data[self.data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        elif search_term == "":
            filtered_data = self.data
        else:
            filtered_data = self.data
        self.display_table(self, self.main_tree, False, filtered_data) #update table
      
      search_var.trace("w", search_data)

      if self.login_check():
            edit_button = ttk.Button(self, text = "Edit Table", command=self.open_edit_window, style = "TButton")
            edit_button.pack()
      self.main_tree = self.display_table(self, None, True)
      self.current_file_label = tk.Label(self, text=f"Current file: {os.path.abspath(self.DATA_FILE)}", anchor = "w")
      self.current_file_label.pack(side = "bottom", fill = "x")
      
      # Add Admin Stats label
      self.admin_stats_label = tk.Label(self, text="", anchor="w", font=("Arial", 10))
      self.admin_stats_label.pack(side="bottom", fill="x")
      self.update_admin_stats() # Update the stats label
      
    def update_admin_stats(self):
      if self.admin_stats_label: # Check if exists before updating
         if self.isAdmin and not self.data.empty:
            num_books = len(self.data)
            books_by_genre = self.data['Genre'].value_counts().to_dict()
            genre_text = ", ".join([f"{genre}: {count}" for genre, count in books_by_genre.items()])

            self.stats_labels["total"].config(text = f"Total Books available: {num_books}")
            self.stats_labels["genre"].config(text = f"Books per Genre: {genre_text}")
            self.admin_stats_label.config(text = f"Books available: {num_books}")
         else:
           self.admin_stats_label.config(text = "")
           self.stats_labels["total"].config(text = "")
           self.stats_labels["genre"].config(text = "")
    
    def update_current_file_label(self):
      if self.current_file_label:
        self.current_file_label.config(text = f"Current file: {os.path.abspath(self.DATA_FILE)}")
      else:
        self.current_file_label = tk.Label(self, text=f"Current file: {os.path.abspath(self.DATA_FILE)}")
        self.current_file_label.pack(side = "bottom", fill = "x")
        
    def on_focus_in(self, entry):
       if entry.get() == "Search Now":
          entry.delete(0, tk.END)
    
    def on_focus_out(self, entry, placeholder):
      if entry.get() == "":
        entry.insert(0, placeholder)
    
    def search_data_by_column(self, search_var, column):
         search_term = search_var.get()
         if search_term and search_term != "Search Now":
             filtered_data = self.data[self.data[column].astype(str).str.contains(search_term, case=False)]
         else:
           filtered_data = self.data
         self.display_table(self, self.main_tree, False, filtered_data) #update table

    def open_edit_window(self):
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Data")
        #search Bar
        search_var = tk.StringVar()
        search_entry = tk.Entry(edit_window, textvariable = search_var)
        search_entry.pack(pady = 10)
        
        # Add placeholder
        search_entry.insert(0, "Search Now")
        search_entry.bind("<FocusIn>", lambda event: self.on_focus_in(search_entry))
        search_entry.bind("<FocusOut>", lambda event: self.on_focus_out(search_entry, "Search Now"))
        
        def search_data(*args):
            search_term = search_var.get()
            if search_term and search_term != "Search Now":
               filtered_data = self.data[self.data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            elif search_term == "":
              filtered_data = self.data
            else:
              filtered_data = self.data
            self.display_table(edit_window, editable_tree, False, filtered_data)
        
        search_var.trace("w", search_data)

        editable_tree = self.display_table(edit_window, None)
        # bind the function to handle click event
        editable_tree.bind("<ButtonRelease-1>", lambda event: self.toggle_checkbox(editable_tree, event))

        def save_changes():
            updated_data = []
            for item in editable_tree.get_children():
                updated_data.append(editable_tree.item(item)["values"][1:]) # Skip the selection (checkbox column)
            new_data = pd.DataFrame(updated_data, columns = self.data.columns)
            self.update_data(new_data)
            messagebox.showinfo("Success", "Data Saved!")
            self.data = new_data # update local data with new data
            self.display_table(self, self.main_tree, False) #update main window with new data
            self.update_admin_stats() # Update admin stats after data change
            edit_window.destroy()

        def add_new_book():
            add_book_window = tk.Toplevel()
            add_book_window.title("Add New Book")
    
            entries = []
            for col in self.data.columns:
                tk.Label(add_book_window, text = col).pack()
                entry = tk.Entry(add_book_window)
                entry.pack()
                entries.append(entry)
        
            def save_new_book():
                new_row = [0] + [entry.get() for entry in entries] # Add a default unselected checkbox
                editable_tree.insert("", "end", values = new_row)
                update_data_from_table(editable_tree, self.data)
                self.display_table(self, self.main_tree, False) #update main table
                self.update_admin_stats() # Update admin stats after new book added
                add_book_window.destroy()
            ttk.Button(add_book_window, text="Save", command=save_new_book, style = "TButton").pack()
    
        save_button = ttk.Button(edit_window, text="Save Changes", command = save_changes, style = "TButton")
        save_button.pack()
        
        add_book_button = ttk.Button(edit_window, text = "Add New Book", command=add_new_book, style = "TButton")
        add_book_button.pack()
    
        def delete_selected_rows():
            selected_items = []
            for item in editable_tree.get_children():
                if editable_tree.item(item)["values"][0] == 1: # if selected
                    selected_items.append(item)
            
            if selected_items:
               for item in selected_items:
                  editable_tree.delete(item)
               update_data_from_table(editable_tree, self.data)
               self.display_table(self, self.main_tree, False)
               self.update_admin_stats() #update after delete selected rows
            else:
                messagebox.showwarning("Warning", "Please select a rows to delete.")
    
        delete_button = ttk.Button(edit_window, text="Delete Selected Rows", command=delete_selected_rows, style = "TButton")
        delete_button.pack()
        
        editable_tree.bind("<Double-1>", lambda event: self.edit_cell(editable_tree, event, self.data))

    def edit_cell(self, tree, event, data):
        selected_item = tree.selection()[0]
        col = tree.identify_column(event.x)
        col_index = int(col[1:]) - 1

        if not selected_item or col == "#1":  # Ignore the checkbox column click
            return
        
        cell_text = str(tree.item(selected_item)['values'][col_index])
        
        edit_popup = tk.Toplevel(self)
        edit_popup.title("Edit Cell")
        edit_popup.geometry("400x300")  # Set the size of the popup
    
        text_entry = tk.Text(edit_popup, wrap="word", font = ("Arial", 12))  # Use a Text widget
        text_entry.insert("1.0", cell_text)
        text_entry.pack(padx=10, pady=10, fill="both", expand=True)

        def save_edit():
           new_text = text_entry.get("1.0", "end-1c")
           current_values = list(tree.item(selected_item)['values'])
           current_values[col_index] = new_text
           tree.item(selected_item, values=current_values)
           update_data_from_table(tree, data)
           self.display_table(self, self.main_tree, False)
           self.update_admin_stats()
           edit_popup.destroy()
    
        save_button = ttk.Button(edit_popup, text="Save", command=save_edit, style="TButton")
        save_button.pack(pady=10)

    def toggle_checkbox(self, tree, event):
        item = tree.identify_row(event.y)
        if item:
            values = list(tree.item(item)['values'])
            if values[0] == 0:
                values[0] = 1
            else:
                values[0] = 0
            tree.item(item, values = values)

def update_data_from_table(editable_tree, data):
    updated_data = []
    for item in editable_tree.get_children():
        updated_data.append(editable_tree.item(item)["values"][1:]) # Skip the selection
    data.update(pd.DataFrame(updated_data, columns = data.columns))
        
if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()