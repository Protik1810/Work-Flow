# main.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter
import sqlite3
import json
import uuid
import datetime
import os
import sys
import subprocess
import copy
from pathlib import Path
from PIL import Image, ImageTk

# Local module imports
import utils
from config import (
    CONFIG_FILE_NAME, DEFAULT_ICON_PATH, DEFAULT_LOGO_PATH,
    SUBFOLDER_NAMES, initial_project_data_template
)
from ui.pages import (
    HomeView, NewProjectP1, NewProjectP2_Department, NewProjectP3_OEM,
    NewProjectP4_ProposalOrder, NewProjectP4A_Scope, NewProjectP4B_BOM,
    NewProjectP5_OEN, ProjectDetailsView, FinancialDetailsView, ProjectCreationPreview
)

class WorkflowApp(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Basic App Setup ---
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.title("WORKFLOW Project Management")
        self._app_icon_photo = None
        self.setup_icon()

        self.geometry("1200x800")
        self.minsize(900, 700)

        # --- Style Configuration ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        self.style.configure("Treeview", rowheight=25, font=('Helvetica', 9))

        # --- App State Variables ---
        self.current_project_data = None
        self.all_projects_data = []
        self.working_folder = ""
        self.db_path = ""
        self.app_ready = False

        # --- UI Frame Management ---
        self.container = customtkinter.CTkFrame(self)
        self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # ** LAZY LOADING IMPLEMENTATION **
        # Store instantiated frames here
        self.frames = {} 
        # Store the class definitions to be instantiated on demand
        self.page_classes = {
            PageClass.__name__: PageClass for PageClass in (
                HomeView, NewProjectP1, NewProjectP2_Department, NewProjectP3_OEM,
                NewProjectP4_ProposalOrder, NewProjectP4A_Scope, NewProjectP4B_BOM,
                NewProjectP5_OEN, ProjectDetailsView, FinancialDetailsView, ProjectCreationPreview
            )
        }

        self.create_menu_bar()
        self.check_initial_setup()
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select/Change Working Folder", command=self.select_working_folder_menu_action)
        file_menu.add_separator()
        file_menu.add_command(label="Restart", command=self.restart_application)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)

        themes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Themes", menu=themes_menu)
        appearance_menu = tk.Menu(themes_menu, tearoff=0)
        themes_menu.add_cascade(label="Appearance Mode", menu=appearance_menu)
        self.appearance_mode_var = customtkinter.StringVar(value=customtkinter.get_appearance_mode())
        for mode in ["Light", "Dark", "System"]:
            appearance_menu.add_radiobutton(label=mode, variable=self.appearance_mode_var, value=mode, command=self.change_appearance_mode)

        color_theme_menu = tk.Menu(themes_menu, tearoff=0)
        themes_menu.add_cascade(label="Color Theme", menu=color_theme_menu)
        self.color_theme_var = customtkinter.StringVar(value="blue")
        for theme_name in ["blue", "green", "dark-blue"]:
            color_theme_menu.add_radiobutton(label=theme_name.replace("-"," ").title(), variable=self.color_theme_var, value=theme_name, command=self.change_color_theme)

        menubar.add_command(label="About", command=self.show_about_dialog)

    def show_frame(self, page_name):
        """
        Shows a frame for the given page name. Implements lazy loading:
        if the frame doesn't exist, it's created on demand.
        This resolves the startup flickering issue.
        """
        if not self.app_ready:
            # This can happen if the user cancels the initial folder selection
            self.prompt_for_working_folder(initial_setup=True)
            return

        frame = self.frames.get(page_name)
        if not frame:
            # Frame not created yet, so create it (lazy loading)
            page_class = self.page_classes.get(page_name)
            if page_class:
                frame = page_class(parent=self.container, controller=self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                messagebox.showerror("Navigation Error", f"Page '{page_name}' not found.", parent=self)
                return
        
        # Call the on_show method if it exists, then raise the frame
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()

    def initialize_main_app(self):
        """Finalizes app setup after the working folder is confirmed."""
        if not self.working_folder or not self.db_path:
            self.prompt_for_working_folder(initial_setup=True)
            return

        self.init_db()
        self.current_project_data = copy.deepcopy(initial_project_data_template)
        
        # App is now ready to show frames
        self.app_ready = True
        self.show_frame("HomeView") # Show the initial frame

    # --- Setup and Config Methods ---

    def setup_icon(self):
        icon_path = Path(DEFAULT_ICON_PATH)
        logo_path = Path(DEFAULT_LOGO_PATH)
        try:
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
            elif logo_path.exists():
                pil_img = Image.open(logo_path).resize((32, 32), Image.Resampling.LANCZOS)
                self._app_icon_photo = ImageTk.PhotoImage(pil_img)
                self.iconphoto(True, self._app_icon_photo)
        except Exception as e:
            print(f"Error setting window icon: {e}")

    def check_initial_setup(self):
        """Loads config and prompts for working folder if not set."""
        self.load_config()
        self.appearance_mode_var.set(customtkinter.get_appearance_mode())
        try:
            theme_path = customtkinter.ThemeManager._currently_loaded_theme
            theme_name = Path(theme_path).stem
            self.color_theme_var.set(theme_name if theme_name in ["blue", "green", "dark-blue"] else "blue")
        except Exception: self.color_theme_var.set("blue")

        if self.working_folder and Path(self.working_folder).is_dir():
            self.db_path = Path(self.working_folder) / 'workflow_app.db'
            self.initialize_main_app()
        else:
            self.prompt_for_working_folder(initial_setup=True)
            
    def prompt_for_working_folder(self, initial_setup=False):
        parent_win = self if not initial_setup and self.winfo_ismapped() else None
        title = "Initial Setup" if initial_setup else "Select Working Folder"
        info = "Select a folder to store all project data and the database."
        
        messagebox.showinfo(title, info, parent=parent_win)
        folder_selected = filedialog.askdirectory(title=title, parent=parent_win)

        if folder_selected:
            self.set_working_folder(folder_selected)
            if not self.app_ready:
                self.initialize_main_app()
            else:
                self.init_db()
                home_view = self.frames.get("HomeView")
                if home_view:
                    home_view.toggle_ui_elements(True)
                    home_view.on_show()
                self.current_project_data = copy.deepcopy(initial_project_data_template)
                messagebox.showinfo("Folder Changed", f"Working folder is now:\n{self.working_folder}", parent=self)
                self.show_frame("HomeView")
        elif initial_setup:
            messagebox.showerror("Setup Required", "A working folder is required to run. Exiting.", parent=None)
            self.quit_app()

    def set_working_folder(self, folder_path):
        self.working_folder = folder_path
        self.db_path = Path(self.working_folder) / 'workflow_app.db'
        self.save_config()

    def load_config(self):
        config_path = Path(CONFIG_FILE_NAME)
        defaults = {"working_folder": "", "appearance_mode": "System", "color_theme": "blue"}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Config load error: {e}. Using defaults.")
                config = defaults
        else:
            config = defaults

        self.working_folder = config.get("working_folder", defaults["working_folder"])
        customtkinter.set_appearance_mode(config.get("appearance_mode", defaults["appearance_mode"]))
        customtkinter.set_default_color_theme(config.get("color_theme", defaults["color_theme"]))

    def save_config(self):
        config_path = Path(CONFIG_FILE_NAME)
        theme_name = "blue"
        try:
            theme_name = Path(customtkinter.ThemeManager._currently_loaded_theme).stem
        except Exception:
            theme_name = self.color_theme_var.get()

        config = {
            "working_folder": self.working_folder,
            "appearance_mode": self.appearance_mode_var.get(),
            "color_theme": theme_name
        }
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    # --- Menu and App Actions ---

    def restart_application(self):
        if messagebox.askyesno("Restart", "Are you sure you want to restart?", parent=self):
            try:
                self.save_config()
                python = sys.executable
                os.execl(python, python, *sys.argv)
            except Exception as e:
                messagebox.showerror("Restart Error", f"Could not restart: {e}", parent=self)

    def quit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit WORKFLOW?", parent=self):
            self.save_config()
            self.destroy()

    def select_working_folder_menu_action(self):
        self.prompt_for_working_folder(initial_setup=False)

    def change_appearance_mode(self):
        customtkinter.set_appearance_mode(self.appearance_mode_var.get())

    def change_color_theme(self):
        new_theme = self.color_theme_var.get()
        customtkinter.set_default_color_theme(new_theme)
        messagebox.showinfo("Theme Change", f"Theme changed. Restart may be required for a full update.", parent=self)

    def show_about_dialog(self):
        about_text = ("WORKFLOW Application\n\nVersion: 1.1.0\nCreated by: Protik\n\n"
                      "Manages project workflows, details, financials, and materials.\n"
                      "Built with Python, Tkinter, CustomTkinter, SQLite.")
        messagebox.showinfo("About WORKFLOW", about_text, parent=self)
        
    # --- Database and Project Data Methods ---

    def init_db(self):
        if not self.db_path: return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, projectName TEXT, projectLead TEXT, status TEXT,
                    departmentDetails TEXT, oemVendorDetails TEXT, scopeOfWorkDetails TEXT,
                    proposalOrderDetails TEXT, billOfMaterials TEXT, oenDetails TEXT,
                    financialDetails TEXT, workingFolder TEXT, projectFolderPath TEXT,
                    createdAt TEXT, updatedAt TEXT
                )''')
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}", parent=self)

    def create_project_specific_folder(self, project_name):
        if not self.working_folder or not Path(self.working_folder).is_dir():
            messagebox.showwarning("Folder Error", "Working folder is not set or invalid.", parent=self)
            return None

        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
        if not safe_name: safe_name = f"project_{uuid.uuid4().hex[:8]}"
        project_path = Path(self.working_folder) / safe_name

        try:
            project_path.mkdir(exist_ok=True)
            for sub_val in SUBFOLDER_NAMES.values():
                (project_path / sub_val).mkdir(exist_ok=True)
            return str(project_path)
        except OSError as e:
            messagebox.showerror("Folder Creation Error", f"Could not create folder '{project_path}':\n{e}", parent=self)
            return None

    def load_projects_from_sqlite(self):
        home_view = self.frames.get("HomeView")
        if not self.db_path or not self.db_path.exists():
            self.all_projects_data = []
            if home_view: home_view.refresh_project_list()
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects ORDER BY updatedAt DESC, id DESC")
                rows = cursor.fetchall()

                self.all_projects_data = []
                for row in rows:
                    project = dict(row)
                    for key, template_val in initial_project_data_template.items():
                        if isinstance(template_val, (dict, list)):
                            if project.get(key) and isinstance(project[key], str):
                                try:
                                    project[key] = json.loads(project[key])
                                except json.JSONDecodeError:
                                    project[key] = copy.deepcopy(template_val)
                            elif project.get(key) is None:
                                 project[key] = copy.deepcopy(template_val)
                    self.all_projects_data.append(project)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading projects: {e}", parent=self)
            self.all_projects_data = []
        
        if home_view and home_view.winfo_exists():
            home_view.refresh_project_list()

    def save_project_to_sqlite(self, project_data_to_save, is_final_step=False):
        if not self.db_path:
            messagebox.showerror("Database Error", "Database path not configured.", parent=self)
            return False

        if not project_data_to_save.get('projectName', '').strip():
            messagebox.showerror("Validation Error", "Project Name is required to save.", parent=self)
            return False

        project_data = copy.deepcopy(project_data_to_save)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        project_data['updatedAt'] = timestamp
        
        if not project_data.get('id'):
            project_data['createdAt'] = timestamp
            if self.working_folder and not project_data.get('projectFolderPath'):
                created_path = self.create_project_specific_folder(project_data['projectName'])
                if created_path: project_data['projectFolderPath'] = created_path

        project_data['workingFolder'] = self.working_folder

        data_for_sql = {}
        for key, val in project_data.items():
            if key == 'id': continue
            data_for_sql[key] = json.dumps(val) if isinstance(val, (dict, list)) else val

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if project_data.get('id'):
                    update_fields = ", ".join([f"{key} = ?" for key in data_for_sql])
                    values = list(data_for_sql.values()) + [project_data['id']]
                    cursor.execute(f"UPDATE projects SET {update_fields} WHERE id = ?", tuple(values))
                else:
                    columns = ", ".join(data_for_sql.keys())
                    placeholders = ", ".join(["?"] * len(data_for_sql))
                    cursor.execute(f"INSERT INTO projects ({columns}) VALUES ({placeholders})", tuple(data_for_sql.values()))
                    project_data['id'] = cursor.lastrowid

            self.current_project_data = project_data
            self.load_projects_from_sqlite()

            if is_final_step:
                self.set_current_project_for_editing(None)
            return True

        except (sqlite3.Error, json.JSONDecodeError) as e:
            messagebox.showerror("Save Error", f"An error occurred while saving: {e}", parent=self)
            return False

    def set_current_project_for_editing(self, project_id=None):
        if project_id is not None:
            try:
                project_id_int = int(project_id)
                project_found = next((p for p in self.all_projects_data if p.get('id') == project_id_int), None)
                if project_found:
                    self.current_project_data = copy.deepcopy(project_found)
                else:
                    raise ValueError(f"Project with ID {project_id_int} not found.")
            except (ValueError, TypeError) as e:
                messagebox.showerror("Error", f"Could not load project: {e}", parent=self)
                self.current_project_data = copy.deepcopy(initial_project_data_template)
        else: # Creating a new project
            self.current_project_data = copy.deepcopy(initial_project_data_template)

    def get_project_bom_total(self):
        if self.current_project_data and 'billOfMaterials' in self.current_project_data:
            return sum(i.get('total', 0.0) for i in self.current_project_data['billOfMaterials'].get('items', []))
        return 0.0

    def update_project_status(self, project_data):
        bom_items = project_data.get('billOfMaterials', {}).get('items', [])
        if not bom_items:
            project_data['status'] = "PENDING"
            return
        
        items_requiring_fulfillment = 0
        fulfilled_items_count = 0
        has_partial_fulfillment = False

        details_frame = self.frames.get('ProjectDetailsView')
        if not details_frame: return # Cannot update without the frame's logic

        for item in bom_items:
            details_frame._update_bom_item_summary_fields(item)
            original_qty = float(item.get('qty', 0.0))
            if original_qty > 1e-9:
                items_requiring_fulfillment += 1
                fulfilled_qty = float(item.get('totalFulfilledQty', 0.0))
                if fulfilled_qty >= original_qty - 1e-9:
                    fulfilled_items_count += 1
                elif fulfilled_qty > 1e-9:
                    has_partial_fulfillment = True
        
        if items_requiring_fulfillment == 0:
            project_data['status'] = "FULFILLED"
        elif fulfilled_items_count == items_requiring_fulfillment:
            project_data['status'] = "FULFILLED"
        elif has_partial_fulfillment or fulfilled_items_count > 0:
            project_data['status'] = "PARTIALLY_FULFILLED"
        else:
            project_data['status'] = "PENDING"
            
    def convert_number_to_words(self, number):
        """Wrapper to call the utility function."""
        return utils.convert_number_to_words(number)


if __name__ == "__main__":
    app = WorkflowApp()
    app.mainloop()