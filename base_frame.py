# ui/base_frame.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter
import shutil
import copy
import datetime
from pathlib import Path
from tkcalendar import DateEntry

from config import initial_project_data_template, SUBFOLDER_NAMES

class PageFrame(customtkinter.CTkFrame):
    """Base class for all page frames in the application."""
    def __init__(self, parent, controller, page_data_key=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.parent_container = parent
        self.page_data_key = page_data_key  # Key for this page's data in the main project dictionary

        # Signature label
        signature = customtkinter.CTkLabel(self, text="© Protik", font=customtkinter.CTkFont(family="Helvetica", size=10, slant="italic"))
        signature.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor=tk.SE)

    def on_show(self):
        """Called every time the frame is shown."""
        if not self.controller.app_ready:
            return
        if self.controller.current_project_data is None:
            self.controller.current_project_data = copy.deepcopy(initial_project_data_template)

        # Update the project name header if it exists on the page
        if hasattr(self, 'project_name_header_label') and self.controller.current_project_data:
            project_name = self.controller.current_project_data.get('projectName', '<NEW PROJECT NAME>')
            self.project_name_header_label.configure(text=project_name if project_name else "<NEW PROJECT NAME>")

    def _get_section_data(self):
        """Gets the data dictionary specific to this page from the controller."""
        if self.controller.current_project_data is None or self.page_data_key is None:
            return None
        
        # Ensure the section exists and is a dictionary
        if self.page_data_key not in self.controller.current_project_data or \
           not isinstance(self.controller.current_project_data[self.page_data_key], dict):
            # If missing, initialize it from the template
            template_section = initial_project_data_template.get(self.page_data_key, {})
            self.controller.current_project_data[self.page_data_key] = copy.deepcopy(template_section)
            
        return self.controller.current_project_data[self.page_data_key]

    def _create_navigation_buttons(self, bottom_frame, back_page, next_page_or_action, save_and_return_home=True, exit_action=True, finish_action_details=None):
        """Creates the standard bottom navigation buttons."""
        left_buttons_frame = customtkinter.CTkFrame(bottom_frame, fg_color="transparent")
        left_buttons_frame.pack(side=tk.LEFT, padx=5, pady=5)
        right_buttons_frame = customtkinter.CTkFrame(bottom_frame, fg_color="transparent")
        right_buttons_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        if back_page:
            customtkinter.CTkButton(left_buttons_frame, text="<< BACK", command=lambda: self.controller.show_frame(back_page),
                                   fg_color="#D1D5DB", text_color="black", hover_color="#9CA3AF").pack(side=tk.LEFT, padx=5)
        if save_and_return_home:
             customtkinter.CTkButton(left_buttons_frame, text="SAVE & RETURN HOME", command=self.handle_save_and_return_home,
                                   fg_color="#F59E0B", text_color="black", hover_color="#D97706").pack(side=tk.LEFT, padx=5)
        if finish_action_details:
            customtkinter.CTkButton(right_buttons_frame, text=finish_action_details["text"], command=finish_action_details["command"],
                                   fg_color=finish_action_details.get("fg_color", "#10B981"),
                                   text_color=finish_action_details.get("text_color", "white"),
                                   hover_color=finish_action_details.get("hover_color", "#059669")).pack(side=tk.RIGHT, padx=5)
        if next_page_or_action:
            cmd = lambda p=next_page_or_action: self.handle_next(p) if isinstance(p, str) else p()
            customtkinter.CTkButton(right_buttons_frame, text="NEXT >>", command=cmd).pack(side=tk.RIGHT, padx=5)
        if exit_action:
            customtkinter.CTkButton(right_buttons_frame, text="EXIT", command=self.handle_exit,
                                   fg_color="#EF4444", hover_color="#DC2626", text_color="white").pack(side=tk.RIGHT, padx=5 if next_page_or_action or finish_action_details else 0)

    def handle_save_and_return_home(self):
        """Saves current data and returns to the home screen."""
        if hasattr(self, 'update_controller_project_data_from_form'):
            self.update_controller_project_data_from_form()

        if self.controller.current_project_data:
            # Create project folder if it doesn't exist
            if not self.controller.current_project_data.get('id') and \
               not self.controller.current_project_data.get('projectFolderPath') and \
               self.controller.working_folder and \
               self.controller.current_project_data.get('projectName'):
                created_path = self.controller.create_project_specific_folder(self.controller.current_project_data['projectName'])
                if created_path:
                    self.controller.current_project_data['projectFolderPath'] = created_path
            
            # Save and navigate
            if self.controller.save_project_to_sqlite(self.controller.current_project_data):
                self.controller.show_frame("HomeView")
        else:
            self.controller.show_frame("HomeView")

    def handle_next(self, target_page_or_command):
        """Saves current page data and proceeds to the next page."""
        if hasattr(self, 'update_controller_project_data_from_form'):
            self.update_controller_project_data_from_form()
        
        # Save project data if it's a new project
        if not self.controller.current_project_data.get('id') and \
           not self.controller.current_project_data.get('projectFolderPath') and \
           self.controller.working_folder and \
           self.controller.current_project_data.get('projectName'):
            created_path = self.controller.create_project_specific_folder(self.controller.current_project_data['projectName'])
            if created_path:
                self.controller.current_project_data['projectFolderPath'] = created_path
            self.controller.save_project_to_sqlite(self.controller.current_project_data)

        if isinstance(target_page_or_command, str):
            self.controller.show_frame(target_page_or_command)
        elif callable(target_page_or_command):
            target_page_or_command()

    def handle_exit(self):
        """Shows exit confirmation dialog."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit? Unsaved changes might be lost.", parent=self):
            self.controller.quit_app()

    def _create_document_widgets(self, parent_frame, doc_key_name, subfolder_target_key=None):
        """Creates a standard set of widgets for single document uploads."""
        doc_input_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        doc_input_frame.pack(fill=tk.X, pady=(5, 5), padx=5)
        customtkinter.CTkLabel(doc_input_frame, text="Documents:", width=15*6, anchor="w").pack(side=tk.LEFT, padx=(0,5))
        doc_path_label = customtkinter.CTkLabel(doc_input_frame, text="No file selected.", anchor="w")
        doc_path_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))

        actual_subfolder_key = subfolder_target_key if subfolder_target_key else doc_key_name
        target_subfolder = SUBFOLDER_NAMES.get(actual_subfolder_key, SUBFOLDER_NAMES["miscDocuments"])

        browse_button = customtkinter.CTkButton(doc_input_frame, text="Browse",
                                   command=lambda dk=doc_key_name, lbl=doc_path_label, sf=target_subfolder: self._handle_document_selection(dk, lbl, sf, allow_multiple=False),
                                   width=80)
        browse_button.pack(side=tk.LEFT)
        return doc_path_label

    def _handle_document_selection(self, doc_key_name_in_section, display_label, target_subfolder_name, allow_multiple=False):
        """Handles Browse, copying, and linking of selected document files."""
        section_data = self._get_section_data()
        if section_data is None:
            messagebox.showerror("Data Error", "Cannot access the project data section to save documents.", parent=self)
            return

        # Prompt user to select file(s)
        if allow_multiple:
            filepaths = filedialog.askopenfilenames(parent=self, title="Select one or more documents")
        else:
            filepaths = [filedialog.askopenfilename(parent=self, title="Select a single document")]

        filepaths = [fp for fp in filepaths if fp]  # Filter out empty results
        if not filepaths:
            return

        project_data = self.controller.current_project_data
        project_main_folder = project_data.get('projectFolderPath')

        # Ensure Project Folder Exists
        if not project_main_folder and project_data.get('projectName') and self.controller.working_folder:
            created_path = self.controller.create_project_specific_folder(project_data['projectName'])
            if created_path:
                project_main_folder = created_path
                project_data['projectFolderPath'] = created_path
                self.controller.save_project_to_sqlite(project_data)  # Save path update
            else:
                messagebox.showwarning("File Management", "Could not create project folder. Files will be linked to original locations.", parent=self)

        # Process Each File
        files_processed_count = 0
        target_full_subfolder_path = None
        if project_main_folder:
            target_full_subfolder_path = Path(project_main_folder) / target_subfolder_name
            try:
                target_full_subfolder_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                messagebox.showerror("Folder Error", f"Could not create subfolder '{target_full_subfolder_path}': {e}", parent=self)
                target_full_subfolder_path = None  # Fallback to linking

        if 'documents' not in section_data or not isinstance(section_data.get('documents'), list):
            section_data['documents'] = []
            
        if not allow_multiple:  # For single-file uploads, clear the existing list
            section_data.setdefault(doc_key_name_in_section, []).clear()

        for original_filepath_str in filepaths:
            original_file = Path(original_filepath_str)
            relative_doc_path = Path(target_subfolder_name) / original_file.name
            new_doc_data = {'name': original_file.name, 'path': str(relative_doc_path), 'type': 'project_file'}

            if target_full_subfolder_path:
                destination_path = target_full_subfolder_path / original_file.name
                try:
                    shutil.copy2(original_file, destination_path)
                except Exception as e:
                    messagebox.showerror("File Copy Error", f"Could not copy file: {e}", parent=self)
                    new_doc_data.update({'path': str(original_file), 'type': 'local_file_link_copy_failed'})
            else:  # Fallback to linking if project folder/subfolder failed
                new_doc_data.update({'path': str(original_file), 'type': 'local_file_link'})

            section_data.setdefault(doc_key_name_in_section, []).append(new_doc_data)
            files_processed_count += 1

        # Update UI
        if files_processed_count > 0:
            if allow_multiple:
                # If there's a specific treeview to refresh (like in OEM page)
                if hasattr(self, '_refresh_oem_documents_tree'):
                    self._refresh_oem_documents_tree()
                messagebox.showinfo("Documents Added", f"{files_processed_count} document(s) processed.", parent=self)
            elif display_label:  # For single file uploads with a label
                last_doc_name = section_data[doc_key_name_in_section][-1]['name']
                display_label.configure(text=last_doc_name)

    def _create_date_entry(self, parent_frame, key_name, label_text, label_width=25, label_font_weight="bold"):
        """Creates a labeled DateEntry widget."""
        date_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        date_frame.pack(fill=tk.X, pady=3, padx=5)
        label_font = customtkinter.CTkFont(weight=label_font_weight)
        customtkinter.CTkLabel(date_frame, text=label_text, width=label_width*6, anchor="w", font=label_font).pack(side=tk.LEFT, padx=(0,5))

        date_input_container = customtkinter.CTkFrame(date_frame, fg_color="transparent")
        date_input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        date_input = DateEntry(date_input_container, width=12,
                               date_pattern='dd/MM/yyyy',
                               firstweekday='monday')
        date_input.pack(side=tk.LEFT, padx=0)
        return date_input