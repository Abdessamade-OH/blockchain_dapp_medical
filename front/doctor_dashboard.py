import customtkinter as ctk
import requests
from tkinter import filedialog
from utils import show_message
import os
from cryptography.fernet import Fernet
import ipfsapi

def add_medical_records_section(parent, doctor_info):
    records_frame = ctk.CTkFrame(parent)
    records_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Patient HH Number Entry
    patient_hh_frame = ctk.CTkFrame(records_frame)
    patient_hh_frame.pack(fill="x", pady=10)

    patient_hh_entry = ctk.CTkEntry(
        patient_hh_frame,
        placeholder_text="Patient HH Number",
        width=300
    )
    patient_hh_entry.pack(side="left", padx=10)

    # Notes Entry
    notes_frame = ctk.CTkFrame(records_frame)
    notes_frame.pack(fill="x", pady=10)
    
    notes_entry = ctk.CTkTextbox(
        notes_frame,
        height=100,
        width=300
    )
    notes_entry.pack(side="left", padx=10)
    notes_entry.insert("1.0", "Enter notes here...")

    # File Selection
    file_frame = ctk.CTkFrame(records_frame)
    file_frame.pack(fill="x", pady=10)

    selected_file_label = ctk.CTkLabel(
        file_frame, 
        text="No file selected", 
        width=300
    )
    selected_file_label.pack(side="left", padx=10)

    selected_file = {}  # Use a dictionary to store file path

    def select_medical_record_file():
        file_types = [
            ('PDF files', '*.pdf'),
            ('Image files', '*.jpg;*.jpeg;*.png'),
            ('Text files', '*.txt'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Medical Record File",
            filetypes=file_types
        )
        
        if filename:
            selected_file['path'] = filename
            selected_file_label.configure(
                text=os.path.basename(filename)
            )

    select_file_btn = ctk.CTkButton(
        file_frame,
        text="Select Medical Record File",
        command=select_medical_record_file
    )
    select_file_btn.pack(side="left", padx=10)

    # Status message
    status_label = ctk.CTkLabel(
        records_frame,
        text="",
        text_color="gray"
    )
    status_label.pack(pady=5)

    def update_status(message, is_error=False):
        status_label.configure(
            text=message,
            text_color="red" if is_error else "green"
        )
        # Reset status after 5 seconds
        records_frame.after(5000, lambda: status_label.configure(text=""))

    # Create Medical Record Button
    def create_medical_record():
        try:
            patient_hh = patient_hh_entry.get()
            if not patient_hh:
                update_status("Please enter patient HH number", True)
                return
            
            if 'path' not in selected_file:
                update_status("Please select a file", True)
                return

            # Prepare form data
            form_data = {
                'patient_hh_number': patient_hh,
                'doctor_hh_number': doctor_info['hhNumber'],
                'notes': notes_entry.get("1.0", "end-1c")
            }

            # Prepare file
            files = {
                'file': (
                    os.path.basename(selected_file['path']),
                    open(selected_file['path'], 'rb'),
                    'application/octet-stream'
                )
            }

            # Show loading status
            update_status("Creating medical record...")
            
            # Send to backend
            response = requests.post(
                "http://127.0.0.1:5000/create_medical_record",
                data=form_data,
                files=files
            )
            
            if response.status_code == 200:
                response_data = response.json()
                success_message = (
                    f"Medical record created successfully\n"
                    f"Transaction Hash: {response_data['data']['transaction_hash'][:10]}..."
                )
                update_status(success_message)
                
                # Reset form
                patient_hh_entry.delete(0, 'end')
                notes_entry.delete("1.0", "end")
                notes_entry.insert("1.0", "Enter notes here...")
                selected_file_label.configure(text="No file selected")
                if 'path' in selected_file:
                    del selected_file['path']
            
            elif response.status_code == 403:
                update_status("Error: No access to this patient's records", True)
            else:
                error_message = response.json().get('error', 'Failed to create medical record')
                update_status(f"Error: {error_message}", True)

        except Exception as e:
            update_status(f"Error: {str(e)}", True)
        finally:
            # Close file if it was opened
            if 'path' in selected_file and 'file' in files:
                files['file'][1].close()

    create_record_btn = ctk.CTkButton(
        records_frame,
        text="Create Medical Record",
        command=create_medical_record
    )
    create_record_btn.pack(pady=10)

    return records_frame


def show_doctor_dashboard(app, doctor_info):
    # Clear the current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Dashboard Header
    header_frame = ctk.CTkFrame(app, height=80, fg_color="#EAF6F6")
    header_frame.pack(fill="x", pady=10)
    welcome_label = ctk.CTkLabel(
        header_frame, 
        text=f"Welcome, Dr. {doctor_info.get('name', 'Doctor')}", 
        font=("Arial", 24)
    )
    welcome_label.pack(side="left", padx=20)
    logout_button = ctk.CTkButton(
        header_frame, 
        text="Logout", 
        command=lambda: app.destroy()
    )
    logout_button.pack(side="right", padx=20)

    # Main Content Area
    content_frame = ctk.CTkFrame(app, fg_color="#EAF6F6")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tabs for different sections
    tab_view = ctk.CTkTabview(content_frame, width=700)
    tab_view.pack(fill="both", expand=True)

    # Personal Info Tab
    personal_info_tab = tab_view.add("Personal Info")
    create_doctor_info_section(personal_info_tab, doctor_info)

    # Patient Records Tab
    patient_records_tab = tab_view.add("Patient Records")
    create_patient_records_section(patient_records_tab)

    # Medical Records Tab
    medical_records_tab = tab_view.add("Medical Records")
    add_medical_records_section(medical_records_tab, doctor_info)

    # Access Management Tab
    access_management_tab = tab_view.add("Access Management")
    create_access_management_section(access_management_tab, doctor_info)

from tkinter import messagebox

def create_doctor_info_section(parent, doctor_info):
    info_frame = ctk.CTkFrame(parent)
    info_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Display doctor info and allow editing
    info_labels = [
        ("Wallet Address", doctor_info.get("walletAddress", "N/A")),
        ("Name", doctor_info.get("name", "N/A")),
        ("Specialization", doctor_info.get("specialization", "N/A")),
        ("Hospital", doctor_info.get("hospitalName", "N/A")),
        ("Health Number", doctor_info.get("hhNumber", "N/A"))
    ]

    # Create labels for static info (don't show wallet address)
    for label, value in info_labels:
        if label != "Wallet Address":  # Hide wallet address
            row = ctk.CTkFrame(info_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"{label}:", anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=5)

    # Fields for editable information (specialization and hospital)
    row_specialization = ctk.CTkFrame(info_frame)
    row_specialization.pack(fill="x", pady=5)
    ctk.CTkLabel(row_specialization, text="Specialization:", anchor="w").pack(side="left", padx=5)
    specialization_entry = ctk.CTkEntry(row_specialization)
    specialization_entry.insert(0, doctor_info.get("specialization", ""))
    specialization_entry.pack(side="left", padx=5)

    row_hospital = ctk.CTkFrame(info_frame)
    row_hospital.pack(fill="x", pady=5)
    ctk.CTkLabel(row_hospital, text="Hospital:", anchor="w").pack(side="left", padx=5)
    hospital_entry = ctk.CTkEntry(row_hospital)
    hospital_entry.insert(0, doctor_info.get("hospitalName", ""))
    hospital_entry.pack(side="left", padx=5)

    # Function to handle the update
    def update_doctor_info():
        # Get the updated values
        new_specialization = specialization_entry.get()
        new_hospital = hospital_entry.get()
        hh_number = doctor_info.get("hhNumber")

        if not new_specialization or not new_hospital:
            messagebox.showerror("Error", "Please fill in both specialization and hospital fields.")
            return

        # Make a POST request to update the information
        url = "http://localhost:5000/updateDoctorInfo"  # Adjust based on your backend URL
        payload = {
            "hhNumber": hh_number,
            "specialization": new_specialization,
            "hospitalName": new_hospital
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200 and data.get("status") == "success":
                messagebox.showinfo("Success", "Doctor information updated successfully.")
                # Update the displayed information with the new values
                doctor_info["specialization"] = new_specialization
                doctor_info["hospitalName"] = new_hospital
                # Refresh the UI with the updated information
                #create_doctor_info_section(parent, doctor_info)
            else:
                messagebox.showerror("Error", data.get("message", "Failed to update information"))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # Button to trigger the update
    update_button = ctk.CTkButton(info_frame, text="Update Info", command=update_doctor_info)
    update_button.pack(pady=20)


def create_patient_records_section(parent):
    records_frame = ctk.CTkFrame(parent)
    records_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Search patient section
    search_frame = ctk.CTkFrame(records_frame)
    search_frame.pack(fill="x", pady=10)

    patient_hh_entry = ctk.CTkEntry(
        search_frame,
        placeholder_text="Patient HH Number",
        width=300
    )
    patient_hh_entry.pack(side="left", padx=10)

    search_button = ctk.CTkButton(
        search_frame,
        text="Search Patient",
        command=lambda: search_patient(patient_hh_entry.get(), results_frame)
    )
    search_button.pack(side="left", padx=10)

    # Results section
    results_frame = ctk.CTkFrame(records_frame)
    results_frame.pack(fill="both", expand=True, pady=10)

    # Add a label to show initial state
    initial_label = ctk.CTkLabel(
        results_frame,
        text="Search for a patient to view their details",
        font=("Arial", 14)
    )
    initial_label.pack(pady=20)

def create_access_management_section(parent, doctor_info):
    access_frame = ctk.CTkFrame(parent)
    access_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Patient access request section
    request_frame = ctk.CTkFrame(access_frame)
    request_frame.pack(fill="x", pady=10)

    patient_hh_entry = ctk.CTkEntry(
        request_frame,
        placeholder_text="Patient HH Number",
        width=300
    )
    patient_hh_entry.pack(side="left", padx=10)

    request_access_btn = ctk.CTkButton(
        request_frame,
        text="Request Access",
        command=lambda: request_patient_access(patient_hh_entry.get(), doctor_info['hhNumber'])
    )
    request_access_btn.pack(side="left", padx=10)

def update_patient_results(results_frame, patient_data):
    # Clear existing content
    for widget in results_frame.winfo_children():
        widget.destroy()

    if not patient_data:
        # Show no results message
        no_results_label = ctk.CTkLabel(
            results_frame,
            text="No patient found or access denied",
            font=("Arial", 14)
        )
        no_results_label.pack(pady=20)
        return

    # Create scrollable frame for patient info
    info_frame = ctk.CTkFrame(results_frame)
    info_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Display patient information
    info_labels = [
        ("Name", patient_data.get("name", "N/A")),
        ("Date of Birth", patient_data.get("dateOfBirth", "N/A")),
        ("Gender", patient_data.get("gender", "N/A")),
        ("Blood Group", patient_data.get("bloodGroup", "N/A")),
        ("Health Number", patient_data.get("hhNumber", "N/A")),
        ("Email", patient_data.get("email", "N/A"))
    ]

    for label, value in info_labels:
        row = ctk.CTkFrame(info_frame)
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=f"{label}:", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=5)

    # Add buttons for actions
    actions_frame = ctk.CTkFrame(info_frame)
    actions_frame.pack(fill="x", pady=10)

    view_records_btn = ctk.CTkButton(
        actions_frame,
        text="View Medical Records",
        command=lambda: view_medical_records(patient_data["hhNumber"])
    )
    view_records_btn.pack(side="left", padx=5)

    add_record_btn = ctk.CTkButton(
        actions_frame,
        text="Add Medical Record",
        command=lambda: add_medical_record(patient_data["hhNumber"])
    )
    add_record_btn.pack(side="left", padx=5)

def search_patient(hh_number, results_frame):
    try:
        response = requests.get(f"http://127.0.0.1:5000/get_patient_details?hh_number={hh_number}")
        if response.status_code == 200:
            patient_data = response.json().get("patient_data", {})
            update_patient_results(results_frame, patient_data)
        else:
            update_patient_results(results_frame, None)
    except requests.exceptions.RequestException as e:
        show_message("Error", f"Failed to search patient: {str(e)}")
        update_patient_results(results_frame, None)

def request_patient_access(patient_hh, doctor_hh):
    try:
        data = {
            "patient_hh": patient_hh,
            "doctor_hh": doctor_hh
        }
        response = requests.post("http://127.0.0.1:5000/request_access", json=data)
        if response.status_code == 200:
            show_message("Success", "Access request sent successfully")
        else:
            show_message("Error", "Failed to send access request")
    except requests.exceptions.RequestException as e:
        show_message("Error", f"Failed to request access: {str(e)}")

def view_medical_records(patient_hh):
    # This function would be implemented to show medical records
    show_message("Info", "Medical records viewing functionality coming soon!")

def add_medical_record(patient_hh):
    # This function would be implemented to add new medical records
    show_message("Info", "Add medical record functionality coming soon!")