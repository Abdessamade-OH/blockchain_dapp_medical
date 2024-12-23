from tkinter import messagebox
import customtkinter
import requests
import os
import sys
import tempfile
import subprocess
from datetime import datetime
from PIL import Image, ImageTk
import mimetypes
import customtkinter as ctk


def show_patient_dashboard(app, patient_info):
    # Clear the current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Set color scheme
    COLORS = {
        'primary': "#2563eb",      # Blue
        'secondary': "#f8fafc",    # Light gray
        'accent': "#3b82f6",       # Lighter blue
        'text': "#1e293b",         # Dark gray
        'success': "#22c55e",      # Green
        'warning': "#f59e0b"       # Orange
    }

    # Configure app background
    app.configure(fg_color=COLORS['secondary'])

    # Dashboard Header with modern styling
    header_frame = customtkinter.CTkFrame(
        app, 
        height=100,
        fg_color="white",
        corner_radius=0
    )
    header_frame.pack(fill="x", pady=(0, 20))

    # Profile section in header
    profile_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
    profile_frame.pack(side="left", padx=30, pady=10)

    # Profile icon
    profile_label = customtkinter.CTkLabel(
        profile_frame,
        text="👤",
        font=("Arial", 32)
    )
    profile_label.pack(side="left", padx=(0, 15))

    # Welcome text with name
    welcome_frame = customtkinter.CTkFrame(profile_frame, fg_color="transparent")
    welcome_frame.pack(side="left")
    
    welcome_text = customtkinter.CTkLabel(
        welcome_frame,
        text="Welcome back,",
        font=("Arial", 14),
        text_color=COLORS['text']
    )
    welcome_text.pack(anchor="w")
    
    name_label = customtkinter.CTkLabel(
        welcome_frame,
        text=patient_info.get('name', 'Patient'),
        font=("Arial", 24, "bold"),
        text_color=COLORS['primary']
    )
    name_label.pack(anchor="w")

    def handle_logout():
        # Show confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to logout?"
        )
        if confirm:
            # Clear any session data or cookies if needed
            # patient_info.clear()  # Clear patient info if needed
            
            # Import the show_auth_page function at the top of your file
            from auth import show_auth_page  # Assuming auth_page.py contains show_auth_page
            
            # Return to auth page
            show_auth_page(app)

    # Logout button with modern styling
    logout_button = customtkinter.CTkButton(
        header_frame,
        text="Logout",
        font=("Arial", 14),
        fg_color=COLORS['warning'],
        hover_color="#ea580c",
        width=120,
        height=40,
        command=handle_logout
    )
    logout_button.pack(side="right", padx=30, pady=10)

    # Main Content Area
    content_frame = customtkinter.CTkFrame(
        app,
        fg_color="transparent"
    )
    content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    # Modern tab view
    tab_view = customtkinter.CTkTabview(
        content_frame,
        fg_color="transparent",
        segmented_button_fg_color=COLORS['primary'],
        segmented_button_selected_color=COLORS['accent'],
        segmented_button_selected_hover_color=COLORS['accent'],
        text_color="white",
        corner_radius=15
    )
    tab_view.pack(fill="both", expand=True)

    # Add tabs with icons
    personal_info_tab = tab_view.add("👤 Personal Info")
    medical_records_tab = tab_view.add("📋 Medical Records")
    access_management_tab = tab_view.add("🔒 Access Management")
    audit_logs_tab = tab_view.add("📊 Audit Logs")

    # Create sections with modern styling
    create_personal_info_section(personal_info_tab, patient_info)
    create_medical_records_section(medical_records_tab, patient_info)
    create_access_management_section(access_management_tab, patient_info)
    audit_logs_section(audit_logs_tab, patient_info)


def create_personal_info_section(parent, patient_info):
    info_frame = customtkinter.CTkFrame(parent, fg_color="white")
    info_frame.pack(fill="both", expand=True, padx=20, pady=5)

    # Display current personal info and allow editing
    info_labels = [
        ("Wallet Address", patient_info.get("walletAddress", "N/A")),
        ("Name", patient_info.get("name", "N/A")),
        ("Date of Birth", patient_info.get("dateOfBirth", "N/A")),
        ("Gender", patient_info.get("gender", "N/A")),
        ("Blood Group", patient_info.get("bloodGroup", "N/A")),
        ("Home Address", patient_info.get("homeAddress", "N/A")),
        ("Email", patient_info.get("email", "N/A")),
        ("Health Number", patient_info.get("hhNumber", "N/A"))
    ]

    for label, value in info_labels:
        row = customtkinter.CTkFrame(info_frame, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=20)
        customtkinter.CTkLabel(
            row,
            text=f"{label}:",
            font=("Arial", 14),
            text_color="#64748b",
            anchor="w"
        ).pack(side="left", padx=5)
        customtkinter.CTkLabel(
            row,
            text=value,
            font=("Arial", 14, "bold"),
            text_color="#1e293b",
            anchor="w"
        ).pack(side="left", padx=5)

    # Editable fields with modern styling
    edit_frame = customtkinter.CTkFrame(info_frame, fg_color="#f8fafc", corner_radius=10)
    edit_frame.pack(fill="x", pady=5, padx=20)

    # Home address input
    home_address_frame = customtkinter.CTkFrame(edit_frame, fg_color="transparent")
    home_address_frame.pack(fill="x", pady=5, padx=15)
    customtkinter.CTkLabel(
        home_address_frame,
        text="Home Address:",
        font=("Arial", 14),
        text_color="#64748b"
    ).pack(side="left", padx=5)
    home_address_entry = customtkinter.CTkEntry(
        home_address_frame,
        width=300,
        height=35,
        corner_radius=8,
        border_color="#e2e8f0"
    )
    home_address_entry.insert(0, patient_info.get("homeAddress", ""))
    home_address_entry.pack(side="left", padx=5)

    # Email input
    email_frame = customtkinter.CTkFrame(edit_frame, fg_color="transparent")
    email_frame.pack(fill="x", pady=5, padx=15)
    customtkinter.CTkLabel(
        email_frame,
        text="Email:",
        font=("Arial", 14),
        text_color="#64748b"
    ).pack(side="left", padx=5)
    email_entry = customtkinter.CTkEntry(
        email_frame,
        width=300,
        height=35,
        corner_radius=8,
        border_color="#e2e8f0"
    )
    email_entry.insert(0, patient_info.get("email", ""))
    email_entry.pack(side="left", padx=5)

    # Function to handle the update
    def update_patient_info():
        # Get the updated values
        new_home_address = home_address_entry.get()
        new_email = email_entry.get()
        hh_number = patient_info.get("hhNumber")

        if not new_home_address or not new_email:
            messagebox.showerror("Error", "Please fill in both the home address and email fields.")
            return

        # Make a POST request to update the information
        url = "http://localhost:5000/updatePatientInfo"  # Adjust based on your backend URL
        payload = {
            "hhNumber": hh_number,
            "homeAddress": new_home_address,
            "email": new_email
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200 and data.get("status") == "success":
                messagebox.showinfo("Success", "Patient information updated successfully.")
                # Update the displayed information with the new values
                patient_info["homeAddress"] = new_home_address
                patient_info["email"] = new_email
                # Refresh the UI with the updated information
                #create_personal_info_section(parent, patient_info)
            else:
                messagebox.showerror("Error", data.get("message", "Failed to update information"))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # Button to trigger the update
    update_button = customtkinter.CTkButton(info_frame, text="Update Info", command=update_patient_info)
    update_button.pack(pady=10)

def create_medical_records_section(parent, patient_info):
    records_frame = customtkinter.CTkFrame(parent, fg_color="white", corner_radius=15)
    records_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Header with actions
    header_frame = customtkinter.CTkFrame(records_frame, fg_color="transparent")
    header_frame.pack(fill="x", pady=(20, 15), padx=20)

    refresh_button = customtkinter.CTkButton(
        header_frame,
        text="↻ Refresh Records",
        font=("Arial", 14),
        fg_color="#2563eb",
        hover_color="#1d4ed8",
        width=150,
        height=35,
        corner_radius=8,
        command=lambda: refresh_records_table(patient_info, table_frame)
    )
    refresh_button.pack(side="right")

    # Table frame with modern styling
    table_frame = customtkinter.CTkFrame(
        records_frame,
        fg_color="#f8fafc",
        corner_radius=10
    )
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Initial load of records
    refresh_records_table(patient_info, table_frame)

def refresh_records_table(patient_info, table_frame):
    # Clear existing table rows
    for widget in table_frame.winfo_children():
        widget.destroy()

    # Fetch records
    records = fetch_patient_records(patient_info.get("hhNumber"))

    if not records:
        no_data_label = customtkinter.CTkLabel(table_frame, text="No medical records found.", font=("Arial", 14))
        no_data_label.pack(pady=10)
        return

    # Table headers
    header_row = customtkinter.CTkFrame(table_frame, fg_color="#f1f5f9")
    header_row.pack(fill="x", pady=5)
    headers = ["Filename", "Type", "Notes", "Date", "Actions"]
    for header in headers:
        customtkinter.CTkLabel(header_row, text=header, width=150, anchor="w", font=("Arial", 14, "bold")).pack(side="left", padx=5)

    # Table rows
    for record in records:
        row_frame = customtkinter.CTkFrame(table_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        # Convert timestamp to readable date
        date_str = datetime.fromtimestamp(record["timestamp"]).strftime("%Y-%m-%d %H:%M")

        # Add record details
        customtkinter.CTkLabel(row_frame, text=record["filename"], width=150, anchor="w").pack(side="left", padx=5)
        customtkinter.CTkLabel(row_frame, text=record["content_type"], width=150, anchor="w").pack(side="left", padx=5)
        customtkinter.CTkLabel(row_frame, text=record["notes"], width=150, anchor="w").pack(side="left", padx=5)
        customtkinter.CTkLabel(row_frame, text=date_str, width=150, anchor="w").pack(side="left", padx=5)

        # View Button
        view_button = customtkinter.CTkButton(
            row_frame,
            text="View",
            command=lambda r=record: view_record(r, patient_info)
        )
        view_button.pack(side="left", padx=5)

def fetch_patient_records(patient_hh_number):
    if not patient_hh_number:
        print("Patient HH Number is required to fetch records.")
        return []

    url = "http://127.0.0.1:5000/get_patient_own_records"
    params = {"patient_hh_number": patient_hh_number}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("records", [])
        else:
            print(f"Failed to fetch records: {response.json().get('error', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Error fetching records: {e}")
        return []

def view_record(record, patient_info):
    try:
        # Prepare the request parameters with content type
        params = {
            "ipfs_hash": record["ipfs_hash"],
            "patient_hh_number": patient_info.get("hhNumber"),
            "content_type": record["content_type"]  # Pass the content type
        }
        
        if patient_info.get("doctorHhNumber"):
            params["doctor_hh_number"] = patient_info.get("doctorHhNumber")
        
        response = requests.get(
            "http://127.0.0.1:5000/get_medical_record_file",
            params=params,
            stream=True
        )
        
        if response.status_code != 200:
            error_msg = response.json().get('error', 'Unknown error')
            messagebox.showerror("Error", f"Failed to fetch record: {error_msg}")
            return

        # Enhanced extension guessing
        content_type = record["content_type"]
        ext = guess_extension(content_type)
        if ext == '' or ext == '.tmp':
            # Fallback to extension from filename if available
            filename = record["filename"]
            if '.' in filename:
                ext = '.' + filename.split('.')[-1]
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tf:
            for chunk in response.iter_content(chunk_size=8192):
                tf.write(chunk)
            tf.flush()
            
            # Enhanced content type handling
            if content_type.startswith(("image/", "application/pdf", "text/")):
                if content_type.startswith("image/"):
                    show_image_viewer(tf.name, record["filename"])
                elif content_type.startswith("application/pdf"):
                    open_pdf(tf.name)
                elif content_type.startswith("text/"):
                    show_text_viewer(tf.name, record["filename"])
            else:
                # If content type is octet-stream, try to guess from filename
                if content_type == "application/octet-stream":
                    filename = record["filename"].lower()
                    if filename.endswith(('.pdf', '.PDF')):
                        open_pdf(tf.name)
                    elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        show_image_viewer(tf.name, record["filename"])
                    elif filename.endswith(('.txt', '.text', '.md')):
                        show_text_viewer(tf.name, record["filename"])
                    else:
                        open_with_system_default(tf.name)
                else:
                    open_with_system_default(tf.name)

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Network error: {str(e)}")
    except IOError as e:
        messagebox.showerror("Error", f"File operation error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

def show_image_viewer(file_path, title):
    """Display image files in a new window."""
    try:
        viewer_window = customtkinter.CTkToplevel()
        viewer_window.title(f"Image Viewer - {title}")
        viewer_window.geometry("800x600")

        # Load and display the image
        image = Image.open(file_path)
        
        # Resize image if it's too large while maintaining aspect ratio
        max_size = (780, 580)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Create label to display image
        label = customtkinter.CTkLabel(viewer_window)
        label.configure(image=photo)
        label.image = photo  # Keep a reference
        label.pack(expand=True, fill="both", padx=10, pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display image: {str(e)}")

def show_text_viewer(file_path, title):
    """Display text files in a new window."""
    try:
        viewer_window = customtkinter.CTkToplevel()
        viewer_window.title(f"Text Viewer - {title}")
        viewer_window.geometry("800x600")

        # Create text widget
        text_widget = customtkinter.CTkTextbox(viewer_window)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Read and display the content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            text_widget.insert("1.0", content)
            text_widget.configure(state="disabled")  # Make read-only
    except UnicodeDecodeError:
        messagebox.showerror("Error", "Unable to read the text file. It might be in an unsupported format.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display text: {str(e)}")

def open_pdf(file_path):
    """Open PDF files."""
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', file_path], check=True)
        elif sys.platform == 'win32':  # Windows
            os.startfile(file_path)
        else:  # Linux
            subprocess.run(['xdg-open', file_path], check=True)
    except (subprocess.SubprocessError, OSError) as e:
        messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")

def open_with_system_default(file_path):
    """Open file with system default application."""
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', file_path], check=True)
        elif sys.platform == 'win32':  # Windows
            os.startfile(file_path)
        else:  # Linux
            subprocess.run(['xdg-open', file_path], check=True)
    except (subprocess.SubprocessError, OSError) as e:
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")

def guess_extension(content_type):
    """Get file extension from content type."""
    try:
        extensions = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'text/plain': '.txt',
            'text/html': '.html',
            'application/pdf': '.pdf',
            'application/json': '.json',
            'application/xml': '.xml',
            'application/octet-stream': '',  # Handle octet-stream specially
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx'
        }
        return extensions.get(content_type.lower(), '')
    except Exception:
        return ''  # Return empty string instead of .tmp

def create_access_management_section(parent, patient_info):
    access_frame = customtkinter.CTkFrame(parent, fg_color="white")
    access_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Input section with modern styling
    input_frame = customtkinter.CTkFrame(access_frame, fg_color="#f8fafc", corner_radius=10)
    input_frame.pack(fill="x", padx=20, pady=(0, 20))

    # Doctor HH number input
    input_container = customtkinter.CTkFrame(input_frame, fg_color="transparent")
    input_container.pack(fill="x", pady=15, padx=15)

    customtkinter.CTkLabel(
        input_container,
        text="Doctor HH Number:",
        font=("Arial", 14),
        text_color="#64748b"
    ).pack(side="left", padx=5)
    
    doctor_hh_entry = customtkinter.CTkEntry(
        input_container,
        width=250,
        height=35,
        corner_radius=8,
        border_color="#e2e8f0"
    )
    doctor_hh_entry.pack(side="left", padx=10)

    grant_button = customtkinter.CTkButton(
        input_container,
        text="Grant Access",
        font=("Arial", 14),
        fg_color="#22c55e",
        hover_color="#16a34a",
        width=150,
        height=35,
        corner_radius=8,
        command=lambda: grant_access(patient_info, doctor_hh_entry.get(), table_frame)
    )
    grant_button.pack(side="left")

    # Table frame with modern styling
    table_frame = customtkinter.CTkFrame(
        access_frame,
        fg_color="#f8fafc",
        corner_radius=10
    )
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    refresh_access_table(patient_info, table_frame)

def refresh_access_table(patient_info, table_frame):
    # Clear existing table rows
    for widget in table_frame.winfo_children():
        widget.destroy()

    # Fetch data
    doctors = fetch_patient_doctors(patient_info.get("hhNumber"))

    if not doctors:
        no_data_label = customtkinter.CTkLabel(table_frame, text="No doctors with access.", font=("Arial", 14))
        no_data_label.pack(pady=10)
        return

    # Table headers
    header_row = customtkinter.CTkFrame(table_frame, fg_color="#f1f5f9")
    header_row.pack(fill="x", pady=5)
    headers = ["Name", "HH Number", "Actions"]
    for header in headers:
        customtkinter.CTkLabel(header_row, text=header, width=200, anchor="w", font=("Arial", 14, "bold")).pack(side="left", padx=5)

    # Table rows
    for doctor in doctors:
        row_frame = customtkinter.CTkFrame(table_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        customtkinter.CTkLabel(row_frame, text=doctor["name"], width=200, anchor="w").pack(side="left", padx=5)
        customtkinter.CTkLabel(row_frame, text=doctor["hhNumber"], width=200, anchor="w").pack(side="left", padx=5)

        # Revoke Button
        revoke_button = customtkinter.CTkButton(
            row_frame, 
            text="Revoke", 
            command=lambda d=doctor["hhNumber"]: revoke_access(patient_info, d, table_frame)
        )
        revoke_button.pack(side="left", padx=5)

def revoke_access(patient_info, doctor_hh_number, table_frame):
    if not doctor_hh_number:
        print("Doctor HH Number is required.")
        return

    url = "http://127.0.0.1:5000/revoke_doctor_access"
    payload = {
        "patient_hh_number": patient_info.get("hhNumber"),
        "doctor_hh_number": doctor_hh_number
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Access revoked successfully!")
            refresh_access_table(patient_info, table_frame)  # Refresh the table
        else:
            print(f"Failed to revoke access: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error revoking access: {e}")

def grant_access(patient_info, doctor_hh_number, table_frame):
    if not doctor_hh_number:
        print("Doctor HH Number is required.")
        return

    url = "http://127.0.0.1:5000/grant_doctor_access"
    payload = {
        "patient_hh_number": patient_info.get("hhNumber"),
        "doctor_hh_number": doctor_hh_number
    }

    print(payload)

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Access granted successfully!")
            refresh_access_table(patient_info, table_frame)  # Refresh the table
        else:
            print(f"Failed to grant access: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error granting access: {e}")

def fetch_patient_doctors(patient_hh_number):
    if not patient_hh_number:
        print("Patient HH Number is required to fetch doctors.")
        return []

    url = f"http://127.0.0.1:5000/get_patient_doctors"
    params = {"patient_hh_number": patient_hh_number}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("doctors", [])
        else:
            print(f"Failed to fetch doctors: {response.json().get('error', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return []
    
def audit_logs_section(parent, patient_info):
    logs_frame = customtkinter.CTkFrame(parent, fg_color="white", corner_radius=15)
    logs_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Header with refresh button
    header_frame = customtkinter.CTkFrame(logs_frame, fg_color="transparent")
    header_frame.pack(fill="x", pady=(20, 15), padx=20)

    refresh_button = customtkinter.CTkButton(
        header_frame,
        text="↻ Refresh Logs",
        font=("Arial", 14),
        fg_color="#2563eb",
        hover_color="#1d4ed8",
        width=150,
        height=35,
        corner_radius=8,
        command=lambda: refresh_audit_logs(patient_info, table_frame)
    )
    refresh_button.pack(side="right")

    # Filters section
    filters_frame = customtkinter.CTkFrame(logs_frame, fg_color="#f8fafc", corner_radius=10)
    filters_frame.pack(fill="x", padx=20, pady=(0, 20))

    # Action type filter
    filter_container = customtkinter.CTkFrame(filters_frame, fg_color="transparent")
    filter_container.pack(fill="x", pady=15, padx=15)

    action_types = ["All Actions", "CREATE", "UPDATE", "VIEW", "GRANT_ACCESS", "REVOKE_ACCESS"]
    action_var = customtkinter.StringVar(value="All Actions")

    customtkinter.CTkLabel(
        filter_container,
        text="Filter by Action:",
        font=("Arial", 14),
        text_color="#64748b"
    ).pack(side="left", padx=5)

    action_dropdown = customtkinter.CTkOptionMenu(
        filter_container,
        values=action_types,
        variable=action_var,
        width=200,
        height=35,
        corner_radius=8,
        fg_color="#2563eb",
        button_color="#1d4ed8",
        button_hover_color="#1e40af",
        dropdown_hover_color="#1e40af",
        command=lambda _: refresh_audit_logs(patient_info, table_frame, action_filter=action_var.get())
    )
    action_dropdown.pack(side="left", padx=10)

    # Table frame with modern styling
    table_frame = customtkinter.CTkScrollableFrame(
        logs_frame,
        fg_color="#f8fafc",
        corner_radius=10,
        height=400
    )
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Initial load of audit logs
    refresh_audit_logs(patient_info, table_frame)

def refresh_audit_logs(patient_info, table_frame, action_filter="All Actions"):
    """Refresh the audit logs table with current data."""
    # Clear existing table
    for widget in table_frame.winfo_children():
        widget.destroy()

    try:
        # Fetch audit logs from backend using patient endpoint
        response = requests.get(
            "http://127.0.0.1:5000/get_patient_audit_logs",
            params={"patient_hh_number": patient_info["hhNumber"]}
        )

        if response.status_code != 200:
            show_error_message(table_frame, "Failed to fetch audit logs")
            return

        logs_data = response.json()
        audit_logs = logs_data.get("audit_logs", [])

        if not audit_logs:
            show_empty_message(table_frame)
            return

        # Filter logs if action filter is set
        if action_filter != "All Actions":
            audit_logs = [log for log in audit_logs if log["actionType"] == action_filter]

        # Create headers
        headers = ["Timestamp", "Doctor", "Action", "Description"]
        header_frame = ctk.CTkFrame(table_frame, fg_color="#f1f5f9")
        header_frame.pack(fill="x", pady=(0, 5))

        for header in headers:
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                width=150,
                anchor="w"
            ).pack(side="left", padx=5)

        # Add log entries
        for log in audit_logs:
            row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            # Timestamp
            ctk.CTkLabel(
                row_frame,
                text=log["datetime"],
                width=150,
                anchor="w"
            ).pack(side="left", padx=5)

            # Doctor Name
            ctk.CTkLabel(
                row_frame,
                text=f"Dr. {log['doctorName']}",
                width=150,
                anchor="w"
            ).pack(side="left", padx=5)

            # Action
            action_label = ctk.CTkLabel(
                row_frame,
                text=log["actionType"],
                width=150,
                anchor="w"
            )
            action_label.pack(side="left", padx=5)

            # Color-code action types
            action_colors = {
                "CREATE": "green",
                "UPDATE": "orange",
                "VIEW": "blue",
                "GRANT_ACCESS": "purple",
                "REVOKE_ACCESS": "red"
            }
            action_label.configure(text_color=action_colors.get(log["actionType"], "gray"))

            # Action Description
            ctk.CTkLabel(
                row_frame,
                text=log["action_description"],
                width=150,
                anchor="w"
            ).pack(side="left", padx=5)

    except Exception as e:
        show_error_message(table_frame, f"Error loading audit logs: {str(e)}")

def show_error_message(parent, message):
    """Display error message in the table frame."""
    ctk.CTkLabel(
        parent,
        text=message,
        text_color="red",
        font=("Arial", 14)
    ).pack(pady=20)

def show_empty_message(parent):
    """Display message when no logs are available."""
    ctk.CTkLabel(
        parent,
        text="No audit logs available",
        font=("Arial", 14)
    ).pack(pady=20)
    
