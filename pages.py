# ui/pages.py
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter
import datetime
import sys
import os
import subprocess
from pathlib import Path
from tkcalendar import DateEntry

# Local imports from within the 'ui' package and the project root
from .base_frame import PageFrame
from .dialogs import AddFulfillmentDialog
from config import SUBFOLDER_NAMES # Import from root config

#
# --- PASTE ALL YOUR PAGE CLASSES HERE ---
# (HomeView, NewProjectP1, NewProjectP2_Department, NewProjectP3_OEM,
#  NewProjectP4_ProposalOrder, NewProjectP4A_Scope, NewProjectP4B_BOM,
#  NewProjectP5_OEN, ProjectDetailsView, FinancialDetailsView, ProjectCreationPreview)
#
# Example of one class start:
class HomeView(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # ... rest of your HomeView code ...

# Make sure all other page classes follow here...

# --- Example of where your classes would go ---

class HomeView(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        top_bar = customtkinter.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill=tk.X, pady=5, padx=5)

        self.select_folder_button = customtkinter.CTkButton(top_bar, text="SELECT/CHANGE WORKING FOLDER",
                   command=self.select_working_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=5)

        self.working_folder_display_frame = customtkinter.CTkFrame(top_bar, border_width=0)
        self.working_folder_display_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.working_folder_display_text_label = customtkinter.CTkLabel(self.working_folder_display_frame, text="Working Folder: <NOT SET>", anchor="w")
        self.working_folder_display_text_label.pack(fill=tk.X, expand=True, padx=5, pady=3)


        self.main_content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        left_panel = customtkinter.CTkFrame(self.main_content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        columns = ("sl_no", "projects", "project_lead", "status")
        self.project_tree = ttk.Treeview(left_panel, columns=columns, show="headings", selectmode="browse")
        self.project_tree.heading("sl_no", text="SL. No.")
        self.project_tree.column("sl_no", width=50, minwidth=40, anchor=tk.W)
        self.project_tree.heading("projects", text="Projects")
        self.project_tree.column("projects", width=350, minwidth=200, anchor=tk.W)
        self.project_tree.heading("project_lead", text="Project Lead")
        self.project_tree.column("project_lead", width=200, minwidth=150, anchor=tk.W)
        self.project_tree.heading("status", text="Status")
        self.project_tree.column("status", width=120, minwidth=100, anchor=tk.CENTER)

        self.project_tree.tag_configure('fulfilled_status', foreground='dark green', font=('Helvetica', 9, 'bold'))
        self.project_tree.tag_configure('partially_fulfilled_status', foreground='#FF8C00', font=('Helvetica', 9, 'bold'))
        self.project_tree.tag_configure('pending_status', foreground='dim gray', font=('Helvetica', 9))


        tree_ysb = ttk.Scrollbar(left_panel, orient="vertical", command=self.project_tree.yview)
        tree_xsb = ttk.Scrollbar(left_panel, orient="horizontal", command=self.project_tree.xview)
        self.project_tree.configure(yscrollcommand=tree_ysb.set, xscrollcommand=tree_xsb.set)

        tree_ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_tree.pack(fill=tk.BOTH, expand=True, pady=(5,0), padx=5)
        tree_xsb.pack(side=tk.BOTTOM, fill=tk.X, padx=5)

        self.project_tree.bind("<Double-1>", self.on_project_double_click)


        search_bar = customtkinter.CTkFrame(left_panel, fg_color="transparent")
        search_bar.pack(fill=tk.X, pady=5, padx=5)
        customtkinter.CTkLabel(search_bar, text="Search:").pack(side=tk.LEFT)
        self.search_entry = customtkinter.CTkEntry(search_bar)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_projects)

        # --- REFRESH BUTTON ADDED HERE ---
        self.refresh_button = customtkinter.CTkButton(search_bar, text="Refresh",
                   command=self.controller.load_projects_from_sqlite, width=90)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_update_button = customtkinter.CTkButton(search_bar, text="EDIT/UPDATE PROJECT",
                   command=self.edit_selected_project)
        self.edit_update_button.pack(side=tk.LEFT, padx=5)

        right_panel = customtkinter.CTkFrame(self.main_content_frame, fg_color="transparent", width=220)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
        right_panel.pack_propagate(False)

        button_width = 200

        self.new_project_button = customtkinter.CTkButton(right_panel, text="NEW PROJECT CREATION", width=button_width,
                   command=lambda: [self.controller.set_current_project_for_editing(None), self.controller.show_frame("NewProjectP1")])
        self.new_project_button.pack(pady=5, fill=tk.X)

        self.open_folder_button = customtkinter.CTkButton(right_panel, text="OPEN PROJECT FOLDER", width=button_width,
                   command=self.open_project_folder_action)
        self.open_folder_button.pack(pady=5, fill=tk.X)

        self.preview_button = customtkinter.CTkButton(right_panel, text="PROJECT CREATION PREVIEW", width=button_width,
                   command=self.preview_project_action)
        self.preview_button.pack(pady=5, fill=tk.X)

        self.details_button = customtkinter.CTkButton(right_panel, text="PROJECT DETAILS", width=button_width,
                   command=self.view_project_details, fg_color="#10B981", hover_color="#059669")
        self.details_button.pack(pady=5, fill=tk.X)

        customtkinter.CTkFrame(right_panel, fg_color="transparent").pack(pady=10, expand=True, fill=tk.Y)

        self.exit_button_home = customtkinter.CTkButton(right_panel, text="EXIT", width=button_width,
                   command=self.handle_exit, fg_color="#EF4444", hover_color="#DC2626")
        self.exit_button_home.pack(pady=20, fill=tk.X)

        self.update_working_folder_display()
        self.toggle_ui_elements(self.controller.app_ready)

    def update_working_folder_display(self):
        folder_path = self.controller.working_folder
        theme_manager = customtkinter.ThemeManager()

        if folder_path and os.path.isdir(folder_path):
            status_text = f"Working Folder: {folder_path}"
            self.working_folder_display_frame.configure(border_width=0)
            text_color = theme_manager.theme["CTkLabel"]["text_color"]
            self.working_folder_display_text_label.configure(text=status_text, text_color=text_color)
        else:
            status_text = "Working Folder: <NOT SET - CLICK SELECT/CHANGE BUTTON>"
            self.working_folder_display_frame.configure(border_width=1, border_color="orange")
            text_color_not_set = theme_manager.theme["CTkEntry"]["text_color_disabled"]
            self.working_folder_display_text_label.configure(text=status_text, text_color=text_color_not_set)



    def toggle_ui_elements(self, enable):
        state = tk.NORMAL if enable else tk.DISABLED
        ctk_state = "normal" if enable else "disabled"

        try:
            if self.project_tree.winfo_exists():
                if enable:
                    self.project_tree.bind("<Double-1>", self.on_project_double_click)
                else:
                    self.project_tree.unbind("<Double-1>")
                    for i in self.project_tree.get_children():
                        self.project_tree.delete(i)
                    self.project_tree.insert("", tk.END, values=("", "Select a working folder to load projects.", "", ""))

            if self.search_entry.winfo_exists(): self.search_entry.configure(state=ctk_state)
            
            # --- TOGGLE REFRESH BUTTON STATE ---
            if self.refresh_button.winfo_exists(): self.refresh_button.configure(state=ctk_state)

            if self.edit_update_button.winfo_exists(): self.edit_update_button.configure(state=ctk_state)
            if self.new_project_button.winfo_exists(): self.new_project_button.configure(state=ctk_state)
            if self.open_folder_button.winfo_exists(): self.open_folder_button.configure(state=ctk_state)
            if self.preview_button.winfo_exists(): self.preview_button.configure(state=ctk_state)
            if self.details_button.winfo_exists(): self.details_button.configure(state=ctk_state)
        except Exception as e:
            print(f"Error toggling HomeView UI elements: {e}")


    def on_show(self):
        super().on_show()
        self.update_working_folder_display()
        if self.controller.app_ready:
            self.controller.load_projects_from_sqlite()
            self.toggle_ui_elements(True)
        else:
            self.toggle_ui_elements(False)


    def refresh_project_list(self, search_term=""):
        if not self.project_tree.winfo_exists(): return
        for i in self.project_tree.get_children():
            self.project_tree.delete(i)

        if not self.controller.app_ready:
            self.project_tree.insert("", tk.END, values=("", "Set working folder to view projects.", "", ""))
            return

        projects_to_display = self.controller.all_projects_data
        if search_term:
            search_term = search_term.lower()
            projects_to_display = [
                p for p in projects_to_display
                if search_term in p.get('projectName', '').lower() or \
                   search_term in p.get('projectLead', '').lower() or \
                   search_term in p.get('status', '').lower()
            ]

        if not projects_to_display:
            if search_term:
                self.project_tree.insert("", tk.END, values=("", f"No projects found matching '{search_term}'.", "", ""))
            else:
                self.project_tree.insert("", tk.END, values=("", "No projects found in this working folder.", "", ""))
        else:
            for idx, project in enumerate(projects_to_display):
                status = project.get('status', 'N/A').upper()
                tags_to_apply = ()

                if status == "FULFILLED":
                    tags_to_apply = ('fulfilled_status',)
                elif status == "PARTIALLY_FULFILLED":
                    tags_to_apply = ('partially_fulfilled_status',)
                elif status == "PENDING":
                    tags_to_apply = ('pending_status',)

                self.project_tree.insert("", tk.END, iid=project.get('id'), values=(
                    idx + 1,
                    project.get('projectName', 'N/A'),
                    project.get('projectLead', 'N/A'),
                    project.get('status', 'N/A')
                ), tags=tags_to_apply)


    def filter_projects(self, event=None):
        if not self.controller.app_ready: return
        search_term = self.search_entry.get()
        self.refresh_project_list(search_term)

    def on_project_double_click(self, event):
        if not self.controller.app_ready: return
        self.view_project_details()

    def get_selected_project_id(self):
        if not self.controller.app_ready: return None
        if not self.project_tree.winfo_exists(): return None
        selected_item_iid = self.project_tree.focus()
        if not selected_item_iid:
            selection = self.project_tree.selection()
            if selection:
                selected_item_iid = selection[0]
            else:
                return None
        return selected_item_iid

    def edit_selected_project(self):
        if not self.controller.app_ready: return
        project_id = self.get_selected_project_id()
        if project_id is not None:
            self.controller.set_current_project_for_editing(project_id)
            self.controller.show_frame("NewProjectP1")
        else:
            messagebox.showinfo("Selection", "Please select a project to edit/update.", parent=self)


    def view_project_details(self):
        if not self.controller.app_ready: return
        project_id = self.get_selected_project_id()
        if project_id is not None:
            self.controller.set_current_project_for_editing(project_id)
            self.controller.show_frame("ProjectDetailsView")
        else:
            if self.controller.all_projects_data:
                first_project_id = self.controller.all_projects_data[0].get('id')
                if first_project_id is not None:
                    self.controller.set_current_project_for_editing(first_project_id)
                    self.controller.show_frame("ProjectDetailsView")
                    return
            messagebox.showinfo("Info", "No projects available or selected to view details.", parent=self)

    def preview_project_action(self):
        if not self.controller.app_ready: return
        project_id = self.get_selected_project_id()
        if project_id:
            self.controller.set_current_project_for_editing(project_id)
            self.controller.show_frame("ProjectCreationPreview")
        else:
            if self.controller.current_project_data and self.controller.current_project_data.get('projectName'):
                 self.controller.show_frame("ProjectCreationPreview")
            else:
                messagebox.showinfo("Selection", "Please select a project to preview or start creating a new one.", parent=self)


    def select_working_folder(self):
        self.controller.prompt_for_working_folder(initial_setup=False)


    def open_project_folder_action(self):
        if not self.controller.app_ready: return
        
        folder_to_open_path = Path(self.controller.working_folder)
        project_id = self.get_selected_project_id()

        if project_id:
            project = next((p for p in self.controller.all_projects_data if str(p.get('id')) == str(project_id)), None)
            if project:
                project_folder_str = project.get('projectFolderPath')
                if project_folder_str and Path(project_folder_str).is_dir():
                    folder_to_open_path = Path(project_folder_str)
                else:
                    messagebox.showinfo("Project Folder", f"Specific folder for '{project.get('projectName')}' not found. Opening general working folder.", parent=self)

        if not folder_to_open_path or not folder_to_open_path.is_dir():
            messagebox.showwarning("No Folder Set", "Working folder is not set or is invalid. Please select one.", parent=self)
            return

        try:
            if sys.platform == "win32":
                os.startfile(folder_to_open_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder_to_open_path)])
            else:
                subprocess.Popen(["xdg-open", str(folder_to_open_path)])
        except Exception as e:
            messagebox.showerror("Error Opening Folder", f"Could not open folder: {e}", parent=self)

# IMPORTANT: Paste the rest of your page classes (NewProjectP1, NewProjectP2_Department, etc.) here.
# Ensure their `__init__` methods still call `super().__init__(parent, controller)`.
# ...
class NewProjectP1(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="NEW PROJECT CREATION", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold"))
        self.project_name_header_label.pack(pady=(0, 20), anchor="w")

        main_form_area = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        main_form_area.pack(fill=tk.X, pady=10, expand=False)

        name_row_frame = customtkinter.CTkFrame(main_form_area, fg_color="transparent")
        name_row_frame.pack(fill=tk.X, pady=(0, 10))
        customtkinter.CTkLabel(name_row_frame, text="ENTER PROJECT NAME:", width=220, anchor="w").pack(side=tk.LEFT, padx=(0,10))
        self.project_name_entry = customtkinter.CTkEntry(name_row_frame)
        self.project_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        lead_row_frame = customtkinter.CTkFrame(main_form_area, fg_color="transparent")
        lead_row_frame.pack(fill=tk.X, pady=(0, 10))
        customtkinter.CTkLabel(lead_row_frame, text="ENTER PROJECT LEAD / MANAGER NAME:", width=220, anchor="w").pack(side=tk.LEFT, padx=(0,10))
        self.project_lead_entry = customtkinter.CTkEntry(lead_row_frame)
        self.project_lead_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        save_button_frame = customtkinter.CTkFrame(main_form_area, fg_color="transparent")
        save_button_frame.pack(fill=tk.X, pady=(10,0))
        customtkinter.CTkButton(save_button_frame, text="SAVE PAGE DETAILS", command=self.handle_save_page_details,
                                fg_color="#10B981", hover_color="#059669").pack(anchor="e")

        customtkinter.CTkFrame(content_frame, fg_color="transparent").pack(fill=tk.BOTH, expand=True)

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="HomeView", next_page_or_action="NewProjectP2_Department")

    def on_show(self):
        super().on_show()
        if self.controller.current_project_data is None:
            self.controller.set_current_project_for_editing(None)

        project_name = self.controller.current_project_data.get('projectName', '')
        project_lead = self.controller.current_project_data.get('projectLead', '')

        self.project_name_entry.delete(0, tk.END)
        self.project_name_entry.insert(0, project_name)
        self.project_lead_entry.delete(0, tk.END)
        self.project_lead_entry.insert(0, project_lead)
        self.project_name_entry.focus()

    def update_controller_project_data_from_form(self):
        if self.controller.current_project_data is None:
            self.controller.set_current_project_for_editing(None)
        self.controller.current_project_data['projectName'] = self.project_name_entry.get().strip()
        self.controller.current_project_data['projectLead'] = self.project_lead_entry.get().strip()

    def handle_save_page_details(self):
        self.update_controller_project_data_from_form()
        if not self.controller.current_project_data.get('projectName'):
            messagebox.showerror("Validation Error", "Project Name cannot be empty to save.", parent=self)
            return

        if not self.controller.current_project_data.get('id') and \
           not self.controller.current_project_data.get('projectFolderPath') and \
           self.controller.working_folder and \
           self.controller.current_project_data.get('projectName'):
            created_path = self.controller.create_project_specific_folder(self.controller.current_project_data['projectName'])
            if created_path:
                self.controller.current_project_data['projectFolderPath'] = created_path

        if self.controller.save_project_to_sqlite(self.controller.current_project_data):
             messagebox.showinfo("Saved", "Project details saved.", parent=self)

    def handle_next(self, target_page):
        self.update_controller_project_data_from_form()
        if not self.controller.current_project_data.get('projectName'):
            messagebox.showerror("Validation Error", "Project Name cannot be empty to proceed.", parent=self)
            return
        super().handle_next(target_page)

class NewProjectP2_Department(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='departmentDetails')
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<NEW PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=14))
        self.project_name_header_label.pack(pady=(0, 5), anchor=tk.W)
        customtkinter.CTkLabel(content_frame, text="DEPARTMENT DETAILS:", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0, 20), anchor=tk.W)

        self.entries = {}
        form_fields_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        form_fields_frame.pack(fill=tk.X, pady=5, expand=False)

        name_frame = customtkinter.CTkFrame(form_fields_frame, fg_color="transparent")
        name_frame.pack(fill=tk.X, pady=3)
        customtkinter.CTkLabel(name_frame, text="Department Name:", width=180, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        self.entries['name'] = customtkinter.CTkEntry(name_frame)
        self.entries['name'].pack(side=tk.LEFT, expand=True, fill=tk.X)

        addr_frame = customtkinter.CTkFrame(form_fields_frame, fg_color="transparent")
        addr_frame.pack(fill=tk.X, pady=3)
        customtkinter.CTkLabel(addr_frame, text="Department Address:", width=180, anchor="nw").pack(side=tk.LEFT, padx=(0,5))
        self.entries['address'] = customtkinter.CTkTextbox(addr_frame, height=70)
        self.entries['address'].pack(side=tk.LEFT, expand=True, fill=tk.X)

        memoid_frame = customtkinter.CTkFrame(form_fields_frame, fg_color="transparent")
        memoid_frame.pack(fill=tk.X, pady=3)
        customtkinter.CTkLabel(memoid_frame, text="Department Memo ID:", width=180, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        self.entries['memoId'] = customtkinter.CTkEntry(memoid_frame)
        self.entries['memoId'].pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.entries['memoDate'] = self._create_date_entry(form_fields_frame, 'memoDate', "Memo Date:", label_width=30)

        self.doc_path_label = self._create_document_widgets(form_fields_frame, 'documents', subfolder_target_key="departmentDetails")

        save_button_frame = customtkinter.CTkFrame(form_fields_frame, fg_color="transparent")
        save_button_frame.pack(fill=tk.X, pady=(10, 5))
        customtkinter.CTkButton(save_button_frame, text="SAVE DEPARTMENT DETAILS",
                                command=self.handle_save_page_details,
                                fg_color="#10B981", hover_color="#059669").pack(anchor="e")


        customtkinter.CTkFrame(content_frame, fg_color="transparent").pack(fill=tk.BOTH, expand=True)
        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="NewProjectP1", next_page_or_action="NewProjectP3_OEM")

    def on_show(self):
        super().on_show()
        dept_details = self._get_section_data()

        for key, widget in self.entries.items():
            value = dept_details.get(key, '')
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
            elif isinstance(widget, customtkinter.CTkTextbox):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", str(value))
            elif isinstance(widget, DateEntry):
                if value and isinstance(value, str):
                    try: widget.set_date(datetime.datetime.strptime(value, "%Y-%m-%d").date())
                    except ValueError: widget.set_date(datetime.date.today())
                else: widget.set_date(datetime.date.today())

        docs = dept_details.get('documents', [])
        self.doc_path_label.configure(text=docs[0].get('name', "No file selected.") if docs and isinstance(docs[0], dict) else "No file selected.")

    def update_controller_project_data_from_form(self):
        dept_details = self._get_section_data()
        if dept_details is None: return

        for key, widget in self.entries.items():
            if isinstance(widget, customtkinter.CTkEntry):
                dept_details[key] = widget.get().strip()
            elif isinstance(widget, customtkinter.CTkTextbox):
                dept_details[key] = widget.get("1.0", tk.END).strip()
            elif isinstance(widget, DateEntry):
                try: dept_details[key] = widget.get_date().strftime("%Y-%m-%d")
                except AttributeError: dept_details[key] = ""

    def handle_save_page_details(self):
        self.update_controller_project_data_from_form()
        if not self._get_section_data().get('name'):
            messagebox.showwarning("Missing Info", "Department Name is recommended before saving.", parent=self)
        if self.controller.save_project_to_sqlite(self.controller.current_project_data):
             messagebox.showinfo("Saved", "Department details saved.", parent=self)

    def handle_next(self, target_page):
        self.update_controller_project_data_from_form()
        super().handle_next(target_page)

class NewProjectP3_OEM(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='oemVendorDetails')
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<NEW PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=14))
        self.project_name_header_label.pack(pady=(0, 5), anchor=tk.W)
        customtkinter.CTkLabel(content_frame, text="OEM-VENDOR DETAILS:", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0, 10), anchor=tk.W)

        self.entries = {}
        form_fields_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        form_fields_frame.pack(fill=tk.X, pady=5, expand=False)

        field_defs = [
            ("OEM Name:", "oemName", 180),
            ("Vendor Name:", "vendorName", 180),
            ("Price Provided by OEM (Rs):", "price", 180)
        ]
        for label_text, key, label_width in field_defs:
            field_frame = customtkinter.CTkFrame(form_fields_frame, fg_color="transparent")
            field_frame.pack(fill=tk.X, pady=3)
            customtkinter.CTkLabel(field_frame, text=label_text, width=label_width, anchor="w").pack(side=tk.LEFT, padx=(0,5))
            entry = customtkinter.CTkEntry(field_frame)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.entries[key] = entry

        self.entries['date'] = self._create_date_entry(form_fields_frame, 'date', "Date:", label_width=30)

        doc_management_frame = customtkinter.CTkFrame(form_fields_frame, fg_color="transparent")
        doc_management_frame.pack(fill=tk.X, pady=(10,5))
        customtkinter.CTkLabel(doc_management_frame, text="OEM/Vendor Documents:", anchor="w").pack(side=tk.LEFT, padx=(0,5))

        doc_buttons_frame = customtkinter.CTkFrame(doc_management_frame, fg_color="transparent")
        doc_buttons_frame.pack(side=tk.RIGHT, padx=(5,0))

        customtkinter.CTkButton(doc_buttons_frame, text="Add Document(s)", command=self._add_oem_documents, width=120).pack(side=tk.LEFT, padx=(0,5))
        customtkinter.CTkButton(doc_buttons_frame, text="Remove Selected", command=self._remove_selected_oem_document, width=120, fg_color="#EF4444", hover_color="#DC2626").pack(side=tk.LEFT)

        doc_tree_frame = customtkinter.CTkFrame(form_fields_frame)
        doc_tree_frame.pack(fill=tk.X, pady=5, expand=True)

        self.oem_documents_tree = ttk.Treeview(doc_tree_frame, columns=("filename", "type"), show="headings", height=3)
        self.oem_documents_tree.heading("filename", text="File Name")
        self.oem_documents_tree.column("filename", anchor=tk.W, width=350)
        self.oem_documents_tree.heading("type", text="Storage Type")
        self.oem_documents_tree.column("type", anchor=tk.W, width=150)
        
        doc_tree_ysb = ttk.Scrollbar(doc_tree_frame, orient="vertical", command=self.oem_documents_tree.yview)
        self.oem_documents_tree.configure(yscrollcommand=doc_tree_ysb.set)
        doc_tree_ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.oem_documents_tree.pack(fill=tk.BOTH, expand=True, pady=(0,0), padx=0)


        customtkinter.CTkFrame(content_frame, fg_color="transparent").pack(fill=tk.BOTH, expand=True)
        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="NewProjectP2_Department", next_page_or_action="NewProjectP4_ProposalOrder")

    def _refresh_oem_documents_tree(self):
        for i in self.oem_documents_tree.get_children():
            self.oem_documents_tree.delete(i)

        oem_details = self._get_section_data()
        if oem_details and 'documents' in oem_details:
            for idx, doc_data in enumerate(oem_details['documents']):
                if isinstance(doc_data, dict):
                    self.oem_documents_tree.insert("", tk.END, iid=str(idx), values=(
                        doc_data.get('name', 'N/A'),
                        doc_data.get('type', 'N/A')
                    ))

    def _add_oem_documents(self):
        target_subfolder = SUBFOLDER_NAMES.get(self.page_data_key, SUBFOLDER_NAMES["miscDocuments"])
        # Use the generic document handler from the base class
        self._handle_document_selection(
            doc_key_name_in_section='documents',
            display_label=None, # Not needed for a tree view
            target_subfolder_name=target_subfolder,
            allow_multiple=True
        )

    def _remove_selected_oem_document(self):
        selected_items = self.oem_documents_tree.selection()
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select a document from the list to remove.", parent=self)
            return

        if not messagebox.askyesno("Confirm Removal", "Are you sure you want to remove the selected document(s) from the list? This does not delete the files from disk.", parent=self):
            return

        oem_details_section = self._get_section_data()
        if oem_details_section is None or 'documents' not in oem_details_section:
            messagebox.showerror("Error", "Cannot access OEM documents list.", parent=self)
            return

        indices_to_remove = sorted([int(item_id) for item_id in selected_items], reverse=True)

        removed_count = 0
        for index in indices_to_remove:
            try:
                oem_details_section['documents'].pop(index)
                removed_count += 1
            except IndexError:
                messagebox.showwarning("Error", f"Could not remove document at index {index}.", parent=self)

        if removed_count > 0:
            self._refresh_oem_documents_tree()
            messagebox.showinfo("Documents Removed", f"{removed_count} document reference(s) removed.", parent=self)

    def on_show(self):
        super().on_show()
        oem_details = self._get_section_data()
        
        if 'documents' not in oem_details or not isinstance(oem_details['documents'], list):
            oem_details['documents'] = []

        for key, widget in self.entries.items():
            value = oem_details.get(key, '')
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
            elif isinstance(widget, DateEntry):
                if value and isinstance(value, str):
                    try: widget.set_date(datetime.datetime.strptime(value, "%Y-%m-%d").date())
                    except ValueError: widget.set_date(datetime.date.today())
                else: widget.set_date(datetime.date.today())
        
        self._refresh_oem_documents_tree()

    def update_controller_project_data_from_form(self):
        oem_details = self._get_section_data()
        if oem_details is None: return

        for key, widget in self.entries.items():
            if isinstance(widget, customtkinter.CTkEntry):
                oem_details[key] = widget.get().strip()
            elif isinstance(widget, DateEntry):
                try: oem_details[key] = widget.get_date().strftime("%Y-%m-%d")
                except AttributeError: oem_details[key] = ""

    def handle_next(self, target_page):
        self.update_controller_project_data_from_form()
        super().handle_next(target_page)


class NewProjectP4_ProposalOrder(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='proposalOrderDetails')
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<NEW PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=14))
        self.project_name_header_label.pack(pady=(0, 5), anchor=tk.W)
        customtkinter.CTkLabel(content_frame, text="PROPOSAL & ORDER DETAILS:", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0, 15), anchor=tk.W)

        self.entries = {}
        self.doc_labels = {}

        scrollable_frame_container = customtkinter.CTkScrollableFrame(content_frame, fg_color="transparent")
        scrollable_frame_container.pack(fill=tk.BOTH, expand=True)

        s1_frame = customtkinter.CTkFrame(scrollable_frame_container, border_width=1)
        customtkinter.CTkLabel(s1_frame, text="Office Proposal", font=customtkinter.CTkFont(family="Helvetica", size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,2))
        s1_frame.pack(fill=tk.X, pady=5, padx=5)

        prop_id_frame = customtkinter.CTkFrame(s1_frame, fg_color="transparent")
        prop_id_frame.pack(fill=tk.X, padx=10, pady=(5,0))
        customtkinter.CTkLabel(prop_id_frame, text="Office Proposal ID:", width=180, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        self.entries['officeProposalId'] = customtkinter.CTkEntry(prop_id_frame)
        self.entries['officeProposalId'].pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entries['proposalDate'] = self._create_date_entry(s1_frame, 'proposalDate', "Proposal Date:", label_width=30)
        self.doc_labels['proposalDocuments'] = self._create_document_widgets(s1_frame, 'proposalDocuments', subfolder_target_key='proposalDocuments')

        s2_frame = customtkinter.CTkFrame(scrollable_frame_container, border_width=1)
        customtkinter.CTkLabel(s2_frame, text="CEO Approval", font=customtkinter.CTkFont(family="Helvetica", size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,2))
        s2_frame.pack(fill=tk.X, pady=10, padx=5)
        self.doc_labels['ceoApprovalDocuments'] = self._create_document_widgets(s2_frame, 'ceoApprovalDocuments', subfolder_target_key='ceoApprovalDocuments')

        s3_frame = customtkinter.CTkFrame(scrollable_frame_container, border_width=1)
        customtkinter.CTkLabel(s3_frame, text="Department Work Order", font=customtkinter.CTkFont(family="Helvetica", size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,2))
        s3_frame.pack(fill=tk.X, pady=5, padx=5)

        work_id_frame = customtkinter.CTkFrame(s3_frame, fg_color="transparent")
        work_id_frame.pack(fill=tk.X, padx=10, pady=(5,0))
        customtkinter.CTkLabel(work_id_frame, text="Dept. Work Order ID:", width=180, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        self.entries['departmentWorkOrderId'] = customtkinter.CTkEntry(work_id_frame)
        self.entries['departmentWorkOrderId'].pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entries['issuingDate'] = self._create_date_entry(s3_frame, 'issuingDate', "Issuing Date:", label_width=30)
        self.doc_labels['workOrderDocuments'] = self._create_document_widgets(s3_frame, 'workOrderDocuments', subfolder_target_key='workOrderDocuments')

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="NewProjectP3_OEM", next_page_or_action="NewProjectP4A_Scope")

    def on_show(self):
        super().on_show()
        details = self._get_section_data()

        for key, widget in self.entries.items():
            value = details.get(key, '')
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
            elif isinstance(widget, DateEntry):
                if value and isinstance(value, str):
                    try: widget.set_date(datetime.datetime.strptime(value, "%Y-%m-%d").date())
                    except ValueError: widget.set_date(datetime.date.today())
                else: widget.set_date(datetime.date.today())

        for doc_key, label_widget in self.doc_labels.items():
            docs_list = details.get(doc_key, [])
            label_widget.configure(text=docs_list[0].get('name', "No file selected.") if docs_list and isinstance(docs_list[0], dict) else "No file selected.")

    def update_controller_project_data_from_form(self):
        details = self._get_section_data()
        if details is None: return

        for key, widget in self.entries.items():
            if isinstance(widget, customtkinter.CTkEntry):
                 details[key] = widget.get().strip()
            elif isinstance(widget, DateEntry):
                 try: details[key] = widget.get_date().strftime("%Y-%m-%d")
                 except AttributeError: details[key] = ""

    def handle_next(self, target_page):
        self.update_controller_project_data_from_form()
        super().handle_next(target_page)

class NewProjectP4A_Scope(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='scopeOfWorkDetails')
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<NEW PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=14))
        self.project_name_header_label.pack(pady=(0, 5), anchor=tk.W)
        customtkinter.CTkLabel(content_frame, text="SCOPE OF WORK DETAILS:", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0, 20), anchor=tk.W)

        scope_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        scope_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        customtkinter.CTkLabel(scope_frame, text="Scope of Work:", width=150, anchor="nw").pack(side=tk.LEFT, padx=(0,5))
        self.scope_text = customtkinter.CTkTextbox(scope_frame, height=100)
        self.scope_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        doc_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        doc_frame.pack(fill=tk.X, pady=5)
        self.doc_path_label = self._create_document_widgets(doc_frame, 'documents', subfolder_target_key="scopeOfWorkDetails")

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="NewProjectP4_ProposalOrder", next_page_or_action="NewProjectP4B_BOM")

    def on_show(self):
        super().on_show()
        details = self._get_section_data()

        self.scope_text.delete("1.0", tk.END)
        self.scope_text.insert("1.0", details.get('scope', ''))

        docs = details.get('documents', [])
        self.doc_path_label.configure(text=docs[0].get('name', "No file selected.") if docs and isinstance(docs[0], dict) else "No file selected.")

    def update_controller_project_data_from_form(self):
        details = self._get_section_data()
        if details:
            details['scope'] = self.scope_text.get("1.0", tk.END).strip()

    def handle_next(self, target_page):
        self.update_controller_project_data_from_form()
        super().handle_next(target_page)

class NewProjectP4B_BOM(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='billOfMaterials')
        self.item_entries = {}

        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<NEW PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=14))
        self.project_name_header_label.pack(pady=(0, 5), anchor=tk.W)
        customtkinter.CTkLabel(content_frame, text="BILL OF MATERIALS DETAILS:", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0, 10), anchor=tk.W)

        entry_form_frame = customtkinter.CTkFrame(content_frame, border_width=1)
        customtkinter.CTkLabel(entry_form_frame, text="Add Item", font=customtkinter.CTkFont(family="Helvetica", size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        entry_form_frame.pack(fill=tk.X, pady=5, padx=5)

        item_fields = [
            ("HSN:", "hsn"), ("Item:", "item"), ("Specs:", "specs"),
            ("Qty:", "qty"), ("Unit Price:", "unitPrice"), ("GST%:", "gstPercent")
        ]

        row1_frame = customtkinter.CTkFrame(entry_form_frame, fg_color="transparent")
        row1_frame.pack(fill=tk.X, pady=2)
        row2_frame = customtkinter.CTkFrame(entry_form_frame, fg_color="transparent")
        row2_frame.pack(fill=tk.X, pady=2)

        for i, (label_text, key) in enumerate(item_fields):
            parent_row = row1_frame if i < 3 else row2_frame
            field_frame = customtkinter.CTkFrame(parent_row, fg_color="transparent")
            field_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            customtkinter.CTkLabel(field_frame, text=label_text, anchor="w").pack(side=tk.LEFT, padx=(0,3))
            entry = customtkinter.CTkEntry(field_frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.item_entries[key] = entry

        customtkinter.CTkButton(entry_form_frame, text="Add Item to BoM", command=self.add_item_to_bom).pack(pady=(8,5), anchor="e", padx=10)

        table_frame = customtkinter.CTkFrame(content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.bom_columns = {
            "sl_no": "SL.", "hsn": "HSN", "item": "Item", "specs": "Specs",
            "qty": "Qty", "unitPrice": "Unit Price", "amount": "Amount",
            "gstPercent": "GST%", "gstAmount": "GST Amt.", "total": "Total"
        }
        self.bom_tree = ttk.Treeview(table_frame, columns=list(self.bom_columns.keys()), show="headings", height=7)

        col_widths = {"sl_no": 30, "hsn": 70, "item": 200, "specs": 250, "qty":60, "unitPrice":90, "amount":90, "gstPercent":60, "gstAmount":90, "total":100}
        min_widths = {"sl_no": 30, "hsn": 50, "item": 100, "specs": 150, "qty":40, "unitPrice":70, "amount":70, "gstPercent":40, "gstAmount":70, "total":80}

        for key, heading_text in self.bom_columns.items():
            self.bom_tree.heading(key, text=heading_text)
            anchor_pos = tk.E if key in ["qty", "unitPrice", "amount", "gstAmount", "total"] else tk.W
            self.bom_tree.column(key, width=col_widths.get(key, 70), minwidth=min_widths.get(key,50), anchor=anchor_pos)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.bom_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.bom_tree.xview)
        self.bom_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        self.bom_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        hsb.pack(side=tk.BOTTOM, fill='x')

        customtkinter.CTkButton(table_frame, text="Remove Selected Item", command=self.remove_selected_item, fg_color="#EF4444", hover_color="#DC2626").pack(pady=5, side=tk.LEFT, anchor="sw")

        summary_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        summary_frame.pack(fill=tk.X, pady=5, padx=5)
        self.total_bom_amount_label = customtkinter.CTkLabel(summary_frame, text="Total BoM Amount (INR): 0.00", font=customtkinter.CTkFont(family="Helvetica", size=10, weight="bold"))
        self.total_bom_amount_label.pack(anchor="e", padx=10)
        self.amount_in_words_label = customtkinter.CTkLabel(summary_frame, text="Amount in Words (INR): Zero", font=customtkinter.CTkFont(family="Helvetica", size=9, slant="italic"))
        self.amount_in_words_label.pack(anchor="e", padx=10)

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="NewProjectP4A_Scope", next_page_or_action="NewProjectP5_OEN")

    def on_show(self):
        super().on_show()
        self._get_section_data() # Ensures 'billOfMaterials' section is initialized
        self.refresh_bom_table()
        self.update_summary_fields()

    def add_item_to_bom(self):
        bom_data = self._get_section_data()
        if bom_data is None: return

        new_item = {}
        try:
            for key, entry_widget in self.item_entries.items():
                value = entry_widget.get().strip()
                if key in ['qty', 'unitPrice', 'gstPercent']:
                    new_item[key] = float(value) if value else 0.0
                else:
                    new_item[key] = value

            if not new_item.get('item'):
                messagebox.showwarning("Missing Info", "Item name is required.", parent=self)
                return

            qty = new_item.get('qty', 0.0)
            unit_price = new_item.get('unitPrice', 0.0)
            gst_percent = new_item.get('gstPercent', 0.0)

            new_item['amount'] = qty * unit_price
            new_item['gstAmount'] = new_item['amount'] * (gst_percent / 100.0)
            new_item['total'] = new_item['amount'] + new_item['gstAmount']
            new_item['sl_no'] = len(bom_data.get('items', [])) + 1
            new_item['fulfillments'] = []

            bom_data.setdefault('items', []).append(new_item)
            self.refresh_bom_table()
            self.update_summary_fields()

            for entry_widget in self.item_entries.values():
                entry_widget.delete(0, tk.END)
            if 'hsn' in self.item_entries: self.item_entries['hsn'].focus()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for Qty, Unit Price, and GST%.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add item: {e}", parent=self)

    def remove_selected_item(self):
        selected_tree_items_ids = self.bom_tree.selection()
        if not selected_tree_items_ids:
            messagebox.showinfo("No Selection", "Please select an item from the table to remove.", parent=self)
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to remove the selected item(s)?", parent=self):
            return

        bom_data = self._get_section_data()
        if bom_data is None or 'items' not in bom_data: return

        sl_nos_to_remove = {int(self.bom_tree.item(item_iid, 'values')[0]) for item_iid in selected_tree_items_ids}
        
        current_items = bom_data.get('items', [])
        items_to_keep = [item for item in current_items if item.get('sl_no') not in sl_nos_to_remove]

        for i, item in enumerate(items_to_keep):
            item['sl_no'] = i + 1

        bom_data['items'] = items_to_keep
        self.refresh_bom_table()
        self.update_summary_fields()

    def refresh_bom_table(self):
        for i in self.bom_tree.get_children():
            self.bom_tree.delete(i)

        bom_data = self._get_section_data()
        if bom_data and 'items' in bom_data and isinstance(bom_data['items'], list):
            for item in bom_data['items']:
                if not isinstance(item, dict): continue
                values = [
                    item.get('sl_no', ''), item.get('hsn', ''), item.get('item', ''),
                    item.get('specs', ''), f"{item.get('qty', 0.0):.2f}", f"{item.get('unitPrice', 0.0):.2f}",
                    f"{item.get('amount', 0.0):.2f}", f"{item.get('gstPercent', 0.0):.2f}%",
                    f"{item.get('gstAmount', 0.0):.2f}", f"{item.get('total', 0.0):.2f}"
                ]
                self.bom_tree.insert("", tk.END, iid=str(item.get('sl_no')), values=values)

    def update_summary_fields(self):
        bom_data = self._get_section_data()
        total_sum = 0.0
        if bom_data and 'items' in bom_data and isinstance(bom_data['items'], list):
            total_sum = sum(item.get('total', 0.0) for item in bom_data['items'] if isinstance(item, dict))

        self.total_bom_amount_label.configure(text=f"Total BoM Amount (INR): {total_sum:.2f}")

        amount_words = self.controller.convert_number_to_words(total_sum)
        self.amount_in_words_label.configure(text=f"Amount in Words (INR): {amount_words}")
        if bom_data:
            bom_data['amountInWords'] = amount_words

    def update_controller_project_data_from_form(self):
        # Data is updated directly via add/remove actions, no form fields to poll
        pass

    def handle_next(self, target_page):
        self.update_summary_fields() # Ensure summary is up to date before leaving
        super().handle_next(target_page)

class NewProjectP5_OEN(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='oenDetails')
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<NEW PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=14))
        self.project_name_header_label.pack(pady=(0, 5), anchor=tk.W)
        customtkinter.CTkLabel(content_frame, text="OEN DETAILS:", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0, 20), anchor=tk.W)

        self.entries = {}
        oen_fields_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        oen_fields_frame.pack(fill=tk.X, pady=5, expand=False)

        oen_reg_no_frame = customtkinter.CTkFrame(oen_fields_frame, fg_color="transparent")
        oen_reg_no_frame.pack(fill=tk.X, pady=3)
        customtkinter.CTkLabel(oen_reg_no_frame, text="OEN Registration No:", width=180, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        self.entries['oenRegistrationNo'] = customtkinter.CTkEntry(oen_reg_no_frame)
        self.entries['oenRegistrationNo'].pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.entries['registrationDate'] = self._create_date_entry(oen_fields_frame, 'registrationDate', "OEN Registration Date:", label_width=30)

        office_oen_no_frame = customtkinter.CTkFrame(oen_fields_frame, fg_color="transparent")
        office_oen_no_frame.pack(fill=tk.X, pady=3)
        customtkinter.CTkLabel(office_oen_no_frame, text="Office OEN No:", width=180, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        self.entries['officeOenNo'] = customtkinter.CTkEntry(office_oen_no_frame)
        self.entries['officeOenNo'].pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.entries['oenDate'] = self._create_date_entry(oen_fields_frame, 'oenDate', "Office OEN Date:", label_width=30)

        self.doc_path_label = self._create_document_widgets(oen_fields_frame, 'documents', subfolder_target_key="oenDetails")

        customtkinter.CTkFrame(content_frame, fg_color="transparent").pack(fill=tk.BOTH, expand=True)
        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(
            bottom_bar,
            back_page="NewProjectP4B_BOM",
            next_page_or_action=None,
            finish_action_details={
                "text": "FINISH PROJECT CREATION",
                "command": self.handle_finish_project,
                "fg_color": "#10B981", "hover_color": "#059669"
            }
        )

    def on_show(self):
        super().on_show()
        details = self._get_section_data()

        for key, widget in self.entries.items():
            value = details.get(key, '')
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
            elif isinstance(widget, DateEntry):
                if value and isinstance(value, str):
                    try: widget.set_date(datetime.datetime.strptime(value, "%Y-%m-%d").date())
                    except ValueError: widget.set_date(datetime.date.today())
                else: widget.set_date(datetime.date.today())

        docs = details.get('documents', [])
        self.doc_path_label.configure(text=docs[0].get('name', "No file selected.") if docs and isinstance(docs[0], dict) else "No file selected.")

    def update_controller_project_data_from_form(self):
        details = self._get_section_data()
        if details is None: return

        for key, widget in self.entries.items():
            if isinstance(widget, customtkinter.CTkEntry):
                details[key] = widget.get().strip()
            elif isinstance(widget, DateEntry):
                try: details[key] = widget.get_date().strftime("%Y-%m-%d")
                except AttributeError: details[key] = ""

    def handle_finish_project(self):
        self.update_controller_project_data_from_form()
        if self.controller.save_project_to_sqlite(self.controller.current_project_data, is_final_step=True):
            messagebox.showinfo("Project Created", "The new project has been successfully created and saved.", parent=self)
            self.controller.show_frame("HomeView")


class ProjectDetailsView(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key=None) # This view uses the whole project data

        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_info_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        top_info_frame.pack(fill=tk.X, pady=(0,10))
        self.project_name_header_label = customtkinter.CTkLabel(top_info_frame, text="<PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=16, weight="bold"))
        self.project_name_header_label.pack(anchor=tk.W)
        self.dept_lead_label = customtkinter.CTkLabel(top_info_frame, text="<DEPT. NAME | PROJECT LEAD>", font=customtkinter.CTkFont(family="Helvetica", size=12))
        self.dept_lead_label.pack(anchor=tk.W)
        self.status_label = customtkinter.CTkLabel(top_info_frame, text="STATUS: <CONDITIONAL>", font=customtkinter.CTkFont(family="Helvetica", size=12, weight="bold"))
        self.status_label.pack(anchor=tk.W)

        main_details_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        main_details_frame.pack(fill=tk.BOTH, expand=True)

        left_column = customtkinter.CTkFrame(main_details_frame, fg_color="transparent")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        bom_summary_frame = customtkinter.CTkFrame(left_column, border_width=1)
        customtkinter.CTkLabel(bom_summary_frame, text="Bill of Materials - Fulfillment Summary", font=customtkinter.CTkFont(family="Helvetica",size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        bom_summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        tree_container = customtkinter.CTkFrame(bom_summary_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

        self.details_tree_columns = {
            "sl_no": "SL.", "item": "Item", "hsn": "HSN", "qty": "Orig. Qty",
            "unitPrice": "Unit Price", "totalFulfilledQty": "Total Fulfilled",
            "lastFulfillmentDate": "Last Fulfill Date", "itemFulfilledAmt": "Fulfilled Val.",
            "pendingQty": "Pending Qty", "itemPendingAmt": "Pending Val.", "total": "Item Total Val."
        }
        self.details_tree = ttk.Treeview(tree_container, columns=list(self.details_tree_columns.keys()), show="headings", height=8)

        dt_col_widths = {"sl_no":30, "item":180, "hsn":70, "qty":70, "unitPrice":80, "totalFulfilledQty":90, "lastFulfillmentDate":100, "itemFulfilledAmt":90, "pendingQty":80, "itemPendingAmt":90, "total":90}
        dt_min_widths = {"sl_no":30, "item":100, "hsn":50, "qty":50, "unitPrice":60, "totalFulfilledQty":70, "lastFulfillmentDate":80, "itemFulfilledAmt":70, "pendingQty":60, "itemPendingAmt":70, "total":70}

        for key, heading in self.details_tree_columns.items():
            anchor = tk.W if key in ["item", "hsn"] else tk.E
            self.details_tree.heading(key, text=heading)
            self.details_tree.column(key, width=dt_col_widths.get(key,75), minwidth=dt_min_widths.get(key,50), anchor=anchor)

        details_vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.details_tree.yview)
        details_hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.details_tree.xview)
        self.details_tree.configure(yscrollcommand=details_vsb.set, xscrollcommand=details_hsb.set)
        details_vsb.pack(side='right', fill='y')
        self.details_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        details_hsb.pack(side=tk.BOTTOM, fill='x')
        self.details_tree.bind("<<TreeviewSelect>>", self.on_bom_item_select)


        history_frame = customtkinter.CTkFrame(left_column, border_width=1)
        customtkinter.CTkLabel(history_frame, text="Fulfillment History (for selected BoM item)", font=customtkinter.CTkFont(family="Helvetica",size=11, weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        history_tree_container = customtkinter.CTkFrame(history_frame)
        history_tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        self.fulfillment_history_tree_columns = {"date": "Date", "qty": "Qty Fulfilled", "remarks": "Remarks"}
        self.fulfillment_history_tree = ttk.Treeview(history_tree_container, columns=list(self.fulfillment_history_tree_columns.keys()), show="headings", height=4)
        self.fulfillment_history_tree.heading("date", text="Date")
        self.fulfillment_history_tree.column("date", width=100, minwidth=80, anchor=tk.CENTER)
        self.fulfillment_history_tree.heading("qty", text="Qty Fulfilled")
        self.fulfillment_history_tree.column("qty", width=100, minwidth=80, anchor=tk.E)
        self.fulfillment_history_tree.heading("remarks", text="Remarks")
        self.fulfillment_history_tree.column("remarks", width=300, minwidth=150, anchor=tk.W)

        history_vsb = ttk.Scrollbar(history_tree_container, orient="vertical", command=self.fulfillment_history_tree.yview)
        history_hsb = ttk.Scrollbar(history_tree_container, orient="horizontal", command=self.fulfillment_history_tree.xview)
        self.fulfillment_history_tree.configure(yscrollcommand=history_vsb.set, xscrollcommand=history_hsb.set)
        history_vsb.pack(side='right', fill='y')
        self.fulfillment_history_tree.pack(side=tk.TOP,fill=tk.BOTH, expand=True)
        history_hsb.pack(side=tk.BOTTOM, fill='x')


        right_column = customtkinter.CTkFrame(main_details_frame, fg_color="transparent", width=350)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5,0))
        right_column.pack_propagate(False)

        scope_frame = customtkinter.CTkFrame(right_column, border_width=1)
        customtkinter.CTkLabel(scope_frame, text="Scope of Work", font=customtkinter.CTkFont(family="Helvetica",size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        scope_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        self.scope_text_display = customtkinter.CTkTextbox(scope_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.scope_text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        left_nav_buttons = customtkinter.CTkFrame(bottom_bar, fg_color="transparent")
        left_nav_buttons.pack(side=tk.LEFT)
        customtkinter.CTkButton(left_nav_buttons, text="<< BACK TO HOME", command=lambda: self.controller.show_frame("HomeView"), fg_color="#D1D5DB", text_color="black", hover_color="#9CA3AF").pack(side=tk.LEFT, padx=5)

        right_nav_buttons = customtkinter.CTkFrame(bottom_bar, fg_color="transparent")
        right_nav_buttons.pack(side=tk.RIGHT)
        customtkinter.CTkButton(right_nav_buttons, text="EXIT", command=self.handle_exit, fg_color="#EF4444", hover_color="#DC2626").pack(side=tk.RIGHT, padx=5)
        customtkinter.CTkButton(right_nav_buttons, text="ADD FULFILLMENT", command=self.add_fulfillment_entry_action, fg_color="#10B981", hover_color="#059669").pack(side=tk.RIGHT, padx=5)
        customtkinter.CTkButton(right_nav_buttons, text="FINANCIAL DETAILS", command=lambda: self.controller.show_frame("FinancialDetailsView")).pack(side=tk.RIGHT, padx=5)


    def _update_bom_item_summary_fields(self, item_dict):
        if not isinstance(item_dict, dict): return

        fulfillments = item_dict.get('fulfillments', [])
        total_fulfilled_qty = sum(float(f.get('fulfilledQty', 0.0)) for f in fulfillments if isinstance(f, dict))
        item_dict['totalFulfilledQty'] = total_fulfilled_qty

        original_qty = float(item_dict.get('qty', 0.0))
        pending_qty = original_qty - total_fulfilled_qty
        item_dict['pendingQty'] = max(0.0, pending_qty)

        original_total_value = float(item_dict.get('total', 0.0))
        value_per_unit = (original_total_value / original_qty) if original_qty > 1e-9 else 0

        item_dict['itemFulfilledAmt'] = total_fulfilled_qty * value_per_unit
        item_dict['itemPendingAmt'] = item_dict['pendingQty'] * value_per_unit

        last_fulfillment_date_str = "N/A"
        if fulfillments:
            try:
                valid_dates = [f.get('fulfilledDate') for f in fulfillments if isinstance(f, dict) and f.get('fulfilledDate')]
                if valid_dates:
                    latest_date_str = max(valid_dates)
                    last_fulfillment_date_str = datetime.datetime.strptime(latest_date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            except (TypeError, ValueError, AttributeError) : last_fulfillment_date_str = "Error"
        item_dict['lastFulfillmentDate'] = last_fulfillment_date_str

    def on_show(self):
        super().on_show()
        project = self.controller.current_project_data
        if not project:
            messagebox.showerror("Error", "No project data to display.", parent=self)
            self.controller.show_frame("HomeView")
            return

        dept_name = project.get('departmentDetails', {}).get('name', 'N/A')
        lead = project.get('projectLead', 'N/A')
        self.dept_lead_label.configure(text=f"Dept: {dept_name} | Lead: {lead}")
        self.status_label.configure(text=f"STATUS: {project.get('status', 'N/A').upper()}")

        self.scope_text_display.configure(state=tk.NORMAL)
        self.scope_text_display.delete("1.0", tk.END)
        self.scope_text_display.insert("1.0", project.get('scopeOfWorkDetails', {}).get('scope', 'Not specified.'))
        self.scope_text_display.configure(state=tk.DISABLED)

        for i in self.details_tree.get_children(): self.details_tree.delete(i)

        bom_items = project.get('billOfMaterials', {}).get('items', [])
        if not isinstance(bom_items, list): bom_items = []

        for item_dict in bom_items:
            if not isinstance(item_dict, dict): continue
            self._update_bom_item_summary_fields(item_dict)

            values = [
                item_dict.get('sl_no', ''), item_dict.get('item', ''), item_dict.get('hsn', ''),
                f"{item_dict.get('qty', 0.0):.2f}", f"{item_dict.get('unitPrice', 0.0):.2f}",
                f"{item_dict.get('totalFulfilledQty', 0.0):.2f}", item_dict.get('lastFulfillmentDate', 'N/A'),
                f"{item_dict.get('itemFulfilledAmt', 0.0):.2f}", f"{item_dict.get('pendingQty', 0.0):.2f}",
                f"{item_dict.get('itemPendingAmt', 0.0):.2f}", f"{item_dict.get('total', 0.0):.2f}"
            ]
            self.details_tree.insert("", tk.END, iid=str(item_dict.get('sl_no')), values=values)
        self.clear_fulfillment_history()

    def on_bom_item_select(self, event=None):
        selected_item_iids = self.details_tree.selection()
        if not selected_item_iids:
            self.clear_fulfillment_history()
            return

        try:
            selected_sl_no = int(self.details_tree.item(selected_item_iids[0], "values")[0])
            bom_items = self.controller.current_project_data.get('billOfMaterials', {}).get('items', [])
            selected_item = next((item for item in bom_items if isinstance(item, dict) and item.get('sl_no') == selected_sl_no), None)
            if selected_item:
                self.populate_fulfillment_history(selected_item)
            else:
                self.clear_fulfillment_history()
        except (ValueError, IndexError):
            self.clear_fulfillment_history()

    def populate_fulfillment_history(self, bom_item_dict):
        self.clear_fulfillment_history()
        fulfillments = bom_item_dict.get('fulfillments', [])
        if not isinstance(fulfillments, list): return

        for entry in sorted(fulfillments, key=lambda x: str(x.get('fulfilledDate', '0000-00-00'))):
            if not isinstance(entry, dict): continue
            display_date = "N/A"
            if entry.get('fulfilledDate'):
                try: display_date = datetime.datetime.strptime(entry.get('fulfilledDate'), "%Y-%m-%d").strftime("%d/%m/%Y")
                except (ValueError, TypeError): pass

            values = [display_date, f"{float(entry.get('fulfilledQty', 0.0)):.2f}", entry.get('remarks', '')]
            self.fulfillment_history_tree.insert("", tk.END, values=values)

    def clear_fulfillment_history(self):
        for i in self.fulfillment_history_tree.get_children(): self.fulfillment_history_tree.delete(i)

    def add_fulfillment_entry_action(self):
        project_data = self.controller.current_project_data
        if not project_data or 'billOfMaterials' not in project_data:
            messagebox.showinfo("Info", "No Bill of Materials found for this project.", parent=self)
            return

        selected_item_iids = self.details_tree.selection()
        if not selected_item_iids:
            messagebox.showinfo("Selection Needed", "Please select a BoM item to add fulfillment.", parent=self)
            return

        try: selected_sl_no = int(self.details_tree.item(selected_item_iids[0], "values")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid item selected.", parent=self); return

        bom_items = project_data.get('billOfMaterials', {}).get('items', [])
        selected_bom_item = next((item for item in bom_items if isinstance(item,dict) and item.get('sl_no') == selected_sl_no), None)
        if not selected_bom_item:
            messagebox.showerror("Error", f"BoM item not found in project data.", parent=self)
            return

        dialog = AddFulfillmentDialog(self, selected_bom_item, self.controller)
        self.master.wait_window(dialog)

        if hasattr(dialog, 'new_fulfillment_added') and dialog.new_fulfillment_added:
            self.controller.update_project_status(project_data)

            if self.controller.save_project_to_sqlite(project_data):
                messagebox.showinfo("Success", "Fulfillment entry added. Project saved.", parent=self)
                self.on_show() # Refresh view
                # Reselect the item in the tree
                for iid_in_tree in self.details_tree.get_children():
                    if self.details_tree.item(iid_in_tree, "values")[0] == str(selected_sl_no):
                        self.details_tree.selection_set(iid_in_tree)
                        self.details_tree.focus(iid_in_tree)
                        self.on_bom_item_select()
                        break
            else:
                messagebox.showerror("Save Error", "Could not save fulfillment updates.", parent=self)

class FinancialDetailsView(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, page_data_key='financialDetails')
        self.transaction_entries = {}

        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_info_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        top_info_frame.pack(fill=tk.X, pady=(0,10))
        self.project_name_header_label = customtkinter.CTkLabel(top_info_frame, text="<PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=16, weight="bold"))
        self.project_name_header_label.pack(anchor=tk.W)
        self.dept_lead_label = customtkinter.CTkLabel(top_info_frame, text="<DEPT. NAME | PROJECT LEAD>", font=customtkinter.CTkFont(family="Helvetica", size=12))
        self.dept_lead_label.pack(anchor=tk.W)
        customtkinter.CTkLabel(top_info_frame, text="FINANCIAL DETAILS", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(5,0), anchor=tk.W)

        history_frame = customtkinter.CTkFrame(content_frame, border_width=1)
        customtkinter.CTkLabel(history_frame, text="Transaction History", font=customtkinter.CTkFont(family="Helvetica",size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.trans_tree_columns = {
            "sl_no": "SL.", "transactionDetails": "Transaction Details", "date": "Date",
            "amountReceived": "Amt. Received", "amountPending": "Amt. Pending After"
        }
        tree_container_fin = customtkinter.CTkFrame(history_frame)
        tree_container_fin.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        self.trans_tree = ttk.Treeview(tree_container_fin, columns=list(self.trans_tree_columns.keys()), show="headings", height=6)

        fin_col_widths = {"sl_no":30, "transactionDetails":300, "date":100, "amountReceived":120, "amountPending":140}
        for key, heading in self.trans_tree_columns.items():
            anchor = tk.W if key == "transactionDetails" else tk.E
            self.trans_tree.heading(key, text=heading)
            self.trans_tree.column(key, width=fin_col_widths.get(key,100), minwidth=70, anchor=anchor)

        trans_vsb = ttk.Scrollbar(tree_container_fin, orient="vertical", command=self.trans_tree.yview)
        trans_hsb = ttk.Scrollbar(tree_container_fin, orient="horizontal", command=self.trans_tree.xview)
        self.trans_tree.configure(yscrollcommand=trans_vsb.set, xscrollcommand=trans_hsb.set)
        trans_vsb.pack(side='right', fill='y')
        self.trans_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        trans_hsb.pack(side=tk.BOTTOM, fill='x')

        payment_form = customtkinter.CTkFrame(content_frame, border_width=1)
        customtkinter.CTkLabel(payment_form, text="Enter Payment Details", font=customtkinter.CTkFont(family="Helvetica",size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,5))
        payment_form.pack(fill=tk.X, pady=10, padx=5)

        entry_fields_data = [ ("Transaction Details:", "transactionDetails"), ("Amount Received (INR):", "amountReceived") ]
        for label_text, key in entry_fields_data:
            field_frame = customtkinter.CTkFrame(payment_form, fg_color="transparent")
            field_frame.pack(fill=tk.X, pady=3, padx=5)
            customtkinter.CTkLabel(field_frame, text=label_text, width=150, anchor="w").pack(side=tk.LEFT, padx=(0,5))
            entry = customtkinter.CTkEntry(field_frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.transaction_entries[key] = entry

        self.transaction_entries['date'] = self._create_date_entry(payment_form, 'date', "Transaction Date:", label_width=25)

        customtkinter.CTkButton(payment_form, text="Add Transaction", command=self.add_transaction).pack(pady=(8,5), anchor="e", padx=10)

        summary_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        summary_frame.pack(fill=tk.X, pady=5, padx=5)
        self.total_pending_label = customtkinter.CTkLabel(summary_frame, text="TOTAL PENDING IN WORDS: <CALCULATING>", font=customtkinter.CTkFont(family="Helvetica",size=10, weight="bold"))
        self.total_pending_label.pack(anchor="e", padx=10)

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        left_nav_buttons_fin = customtkinter.CTkFrame(bottom_bar, fg_color="transparent")
        left_nav_buttons_fin.pack(side=tk.LEFT)
        customtkinter.CTkButton(left_nav_buttons_fin, text="<< BACK TO PROJECT DETAILS", command=lambda: self.controller.show_frame("ProjectDetailsView"), fg_color="#D1D5DB", text_color="black", hover_color="#9CA3AF").pack(side=tk.LEFT, padx=5)


        right_nav_buttons_fin = customtkinter.CTkFrame(bottom_bar, fg_color="transparent")
        right_nav_buttons_fin.pack(side=tk.RIGHT)
        customtkinter.CTkButton(right_nav_buttons_fin, text="EXIT", command=self.handle_exit, fg_color="#EF4444", hover_color="#DC2626").pack(side=tk.RIGHT, padx=5)
        customtkinter.CTkButton(right_nav_buttons_fin, text="SAVE FINANCIALS", command=self.save_financial_details, fg_color="#10B981", hover_color="#059669").pack(side=tk.RIGHT, padx=5)


    def on_show(self):
        super().on_show()
        project = self.controller.current_project_data
        if not project:
            messagebox.showerror("Error", "No project data.", parent=self)
            self.controller.show_frame("HomeView")
            return

        self._get_section_data() # Ensure section is initialized

        dept_name = project.get('departmentDetails', {}).get('name', 'N/A')
        lead = project.get('projectLead', 'N/A')
        self.dept_lead_label.configure(text=f"Dept: {dept_name} | Lead: {lead}")

        self.refresh_transaction_table()
        self.update_financial_summary()

    def add_transaction(self):
        fin_data = self._get_section_data()
        if fin_data is None: return

        try:
            details = self.transaction_entries['transactionDetails'].get().strip()
            amount_str = self.transaction_entries['amountReceived'].get().strip()
            amount = float(amount_str) if amount_str else 0.0
            
            if not details:
                messagebox.showwarning("Missing Info", "Transaction details are required.", parent=self)
                return
            if amount <= 1e-9:
                messagebox.showwarning("Invalid Amount", "Amount received must be greater than zero.", parent=self)
                return
            
            new_trans = {
                'transactionDetails': details,
                'amountReceived': amount,
                'date': self.transaction_entries['date'].get_date().strftime("%Y-%m-%d"),
                'sl_no': len(fin_data.get('transactions', [])) + 1
            }

            fin_data.setdefault('transactions', []).append(new_trans)
            self.recalculate_pending_amounts()
            self.refresh_transaction_table()
            self.update_financial_summary()

            self.transaction_entries['transactionDetails'].delete(0, tk.END)
            self.transaction_entries['amountReceived'].delete(0, tk.END)
            self.transaction_entries['date'].set_date(datetime.date.today())
            self.transaction_entries['transactionDetails'].focus()

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for Amount Received.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add transaction: {e}", parent=self)

    def recalculate_pending_amounts(self):
        fin_data = self._get_section_data()
        bom_total = self.controller.get_project_bom_total()
        
        sorted_transactions = sorted(
            fin_data.get('transactions', []),
            key=lambda x: (str(x.get('date', '0000-00-00')), x.get('sl_no', 0))
        )
        
        cumulative_received = 0
        for trans in sorted_transactions:
            cumulative_received += trans.get('amountReceived', 0.0)
            trans['amountPending'] = bom_total - cumulative_received
        
        fin_data['transactions'] = sorted_transactions


    def refresh_transaction_table(self):
        for i in self.trans_tree.get_children(): self.trans_tree.delete(i)

        fin_data = self._get_section_data()
        if fin_data and 'transactions' in fin_data:
            for trans in fin_data.get('transactions', []):
                if not isinstance(trans, dict): continue
                display_date = "N/A"
                if trans.get('date'):
                    try: display_date = datetime.datetime.strptime(trans.get('date'), "%Y-%m-%d").strftime("%d/%m/%Y")
                    except ValueError: pass

                values = [
                    trans.get('sl_no', ''), trans.get('transactionDetails', ''), display_date,
                    f"{trans.get('amountReceived', 0.0):.2f}", f"{trans.get('amountPending', 0.0):.2f}"
                ]
                self.trans_tree.insert("", tk.END, values=values)

    def update_financial_summary(self):
        fin_data = self._get_section_data()
        bom_total = self.controller.get_project_bom_total()
        
        total_received = sum(t.get('amountReceived', 0.0) for t in fin_data.get('transactions', []))
        overall_pending = bom_total - total_received

        fin_data['totalAmountReceived'] = total_received
        fin_data['totalAmountPending'] = overall_pending
        
        pending_words = self.controller.convert_number_to_words(overall_pending)
        fin_data['totalPendingInWords'] = pending_words
        
        self.total_pending_label.configure(text=f"TOTAL PENDING IN WORDS: {pending_words.upper()}")

    def save_financial_details(self):
        self.recalculate_pending_amounts()
        self.update_financial_summary()
        if self.controller.save_project_to_sqlite(self.controller.current_project_data):
            messagebox.showinfo("Saved", "Financial details saved with the project.", parent=self)
        else:
            messagebox.showerror("Save Error", "Could not save financial details.", parent=self)


class ProjectCreationPreview(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.project_name_header_label = customtkinter.CTkLabel(content_frame, text="<PROJECT NAME>", font=customtkinter.CTkFont(family="Helvetica", size=16, weight="bold"))
        self.project_name_header_label.pack(pady=(0, 10), anchor=tk.W)

        customtkinter.CTkLabel(content_frame, text="PROJECT CREATION PREVIEW", font=customtkinter.CTkFont(family="Helvetica", size=18, weight="bold")).pack(pady=(0,10), anchor=tk.W)

        self.preview_text = customtkinter.CTkTextbox(content_frame, wrap=tk.WORD, state=tk.DISABLED, height=300)
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        self.preview_text.tag_config("hyperlink", foreground="blue", underline=True)
        self.preview_text.tag_bind("hyperlink", "<Enter>", lambda e: self.preview_text.configure(cursor="hand2"))
        self.preview_text.tag_bind("hyperlink", "<Leave>", lambda e: self.preview_text.configure(cursor=""))

        bottom_bar = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        self._create_navigation_buttons(bottom_bar, back_page="HomeView", next_page_or_action=None, save_and_return_home=False, exit_action=True)

    def _open_document_file(self, file_path_str):
        if not file_path_str:
            messagebox.showwarning("No Path", "Document path is not available.", parent=self)
            return
        
        file_path = Path(file_path_str)
        if not file_path.exists():
            messagebox.showerror("Error", f"File not found or path is invalid:\n{file_path}", parent=self)
            return
            
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(file_path)])
            else:
                subprocess.Popen(["xdg-open", str(file_path)])
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open file '{file_path.name}':\n{e}", parent=self)

    def _insert_doc_links(self, section_title, doc_list_data, project_folder_path_str, unique_prefix):
        self.preview_text.insert(tk.END, f"  {section_title}: ")
        if not doc_list_data:
            self.preview_text.insert(tk.END, "None\n")
            return

        project_folder_path = Path(project_folder_path_str) if project_folder_path_str else None

        for i, doc_data in enumerate(doc_list_data):
            if not isinstance(doc_data, dict): continue

            doc_name = doc_data.get('name', 'file')
            relative_path = doc_data.get('path', '')
            doc_type = doc_data.get('type', 'project_file')
            full_doc_path = None

            if doc_type == 'project_file':
                if project_folder_path and relative_path:
                    full_doc_path = project_folder_path / relative_path
                else:
                    doc_name += " (Path Incomplete)"
            elif 'local_file_link' in doc_type:
                full_doc_path = Path(relative_path)
            else:
                doc_name += f" (Type: {doc_type})"

            if full_doc_path:
                tag_name = f"{unique_prefix}_doc_{i}"
                self.preview_text.insert(tk.END, doc_name, ("hyperlink", tag_name))
                self.preview_text.tag_bind(tag_name, "<Button-1>", lambda e, p=str(full_doc_path): self._open_document_file(p))
            else:
                self.preview_text.insert(tk.END, doc_name)

            if i < len(doc_list_data) - 1: self.preview_text.insert(tk.END, ", ")
        
        self.preview_text.insert(tk.END, "\n")

    def on_show(self):
        super().on_show()
        project = self.controller.current_project_data
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)

        if not project or not project.get('projectName'):
            self.preview_text.insert(tk.END, "No project selected or being created to preview.")
            if hasattr(self, 'project_name_header_label'): self.project_name_header_label.configure(text="<NO PROJECT SELECTED>")
            self.preview_text.configure(state=tk.DISABLED)
            return

        if hasattr(self, 'project_name_header_label'):
            self.project_name_header_label.configure(text=project.get('projectName', '<PROJECT NAME>'))

        project_folder_path = project.get('projectFolderPath')

        self.preview_text.insert(tk.END, f"Project Name: {project.get('projectName', 'N/A')}\n")
        self.preview_text.insert(tk.END, f"Project Lead: {project.get('projectLead', 'N/A')}\n")
        self.preview_text.insert(tk.END, f"Status: {project.get('status', 'N/A')}\n")
        self.preview_text.insert(tk.END, f"Project Folder Path: {project_folder_path if project_folder_path else 'N/A'}\n\n")

        # --- Details Sections ---
        details_map = {
            "Department": ("departmentDetails", ["name", "address", "memoId", "memoDate"]),
            "OEM-Vendor": ("oemVendorDetails", ["oemName", "vendorName", "price", "date"]),
            "Proposal & Order": ("proposalOrderDetails", ["officeProposalId", "proposalDate", "departmentWorkOrderId", "issuingDate"]),
            "Scope of Work": ("scopeOfWorkDetails", ["scope"]),
            "OEN": ("oenDetails", ["oenRegistrationNo", "registrationDate", "officeOenNo", "oenDate"]),
        }

        for title, (key, fields) in details_map.items():
            self.preview_text.insert(tk.END, f"--- {title} Details ---\n")
            data = project.get(key, {})
            for field in fields:
                label = ' '.join(word.capitalize() for word in field.replace('Id', 'ID').split(' ')).replace("Oem", "OEM")
                value = data.get(field, 'N/A')
                if 'Date' in field: value = self.format_date_for_display(value)
                self.preview_text.insert(tk.END, f"  {label}: {value}\n")
            
            # Document handling
            doc_keys = [k for k in data.keys() if 'ocuments' in k]
            for doc_key in doc_keys:
                doc_title = "Documents" if len(doc_keys) == 1 else ' '.join(word.capitalize() for word in doc_key.replace("Documents","").split(' '))
                self._insert_doc_links(doc_title, data.get(doc_key, []), project_folder_path, key)

            self.preview_text.insert(tk.END, "\n")

        # Bill of Materials
        bom = project.get('billOfMaterials', {})
        self.preview_text.insert(tk.END, "--- Bill of Materials ---\n")
        bom_items = bom.get('items', [])
        if bom_items:
            for item in bom_items:
                self.preview_text.insert(tk.END, f"  - SL:{item.get('sl_no','N/A')} {item.get('item','N/A')} (HSN:{item.get('hsn','N/A')}), Qty:{item.get('qty',0):.2f}, Total:{item.get('total',0.0):.2f}\n")
        else:
            self.preview_text.insert(tk.END, "  No items in Bill of Materials.\n")
        self.preview_text.insert(tk.END, f"  Amount in Words: {bom.get('amountInWords', 'N/A')}\n\n")

        # Financial Summary
        fin = project.get('financialDetails', {})
        self.preview_text.insert(tk.END, "--- Financial Summary ---\n")
        self.preview_text.insert(tk.END, f"  Total Amount Received: {fin.get('totalAmountReceived', 0.0):.2f}\n")
        self.preview_text.insert(tk.END, f"  Total Amount Pending: {fin.get('totalAmountPending', 0.0):.2f}\n")
        self.preview_text.insert(tk.END, f"  Pending in Words: {fin.get('totalPendingInWords', 'N/A')}\n")

        self.preview_text.configure(state=tk.DISABLED)

    def format_date_for_display(self, date_str):
        if not date_str or not isinstance(date_str, str): return "N/A"
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return date_str
