import customtkinter as ctk
from tkinter import filedialog
import os
from cryptography.fernet import Fernet
import datetime
from web3 import Web3
import json

# Assuming the necessary classes and methods from DoctorDashboard are available

def show_doctor_dashboard(app, patient_info, doctor_info):
    # Clear the current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Dashboard Header
    header_frame = ctk.CTkFrame(app, height=80, fg_color="#EAF6F6")
    header_frame.pack(fill="x", pady=10)
    welcome_label = ctk.CTkLabel(
        header_frame, 
        text=f"Welcome, Dr. {doctor_info['name']}", 
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
    create_personal_info_section(personal_info_tab, patient_info)

    # Medical Records Tab
    medical_records_tab = tab_view.add("Medical Records")
    create_medical_records_section(medical_records_tab)

    # Access Management Tab
    access_management_tab = tab_view.add("Access Management")
    create_access_management_section(access_management_tab, doctor_info)

    # New Doctor-Specific Functionalities
    doctor_tab = tab_view.add("Doctor Functions")
    create_doctor_functionality_section(doctor_tab, doctor_info)

def create_personal_info_section(parent, patient_info):
    info_frame = ctk.CTkFrame(parent)
    info_frame.pack(fill="both", expand=True, padx=20, pady=20)

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
        row = ctk.CTkFrame(info_frame)
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=f"{label}:", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=5)

def create_medical_records_section(parent):
    label = ctk.CTkLabel(parent, text="Medical Records - Coming Soon!", font=("Arial", 16))
    label.pack(pady=20)

def create_access_management_section(parent, doctor_info):
    access_frame = ctk.CTkFrame(parent)
    access_frame.pack(fill="both", expand=True, padx=20, pady=20)

    check_access_frame = ctk.CTkFrame(access_frame)
    check_access_frame.pack(fill="x", pady=10)

    patient_hh_entry = ctk.CTkEntry(
        check_access_frame,
        placeholder_text="Patient HH Number",
        width=300
    )
    patient_hh_entry.pack(side="left", padx=10)

    check_access_btn = ctk.CTkButton(
        check_access_frame,
        text="Check Access",
        command=lambda: check_patient_access(patient_hh_entry.get(), doctor_info['hhNumber'])
    )
    check_access_btn.pack(side="left", padx=10)

    access_status_label = ctk.CTkLabel(
        access_frame,
        text="Access status will appear here",
        font=("Arial", 14)
    )
    access_status_label.pack(pady=10)

def create_doctor_functionality_section(parent, doctor_info):
    # Additional Doctor Functionality like creating medical records, viewing audit logs, etc.
    records_frame = ctk.CTkFrame(parent)
    records_frame.pack(fill="both", expand=True, padx=20, pady=20)

    hh_frame = ctk.CTkFrame(records_frame)
    hh_frame.pack(fill="x", pady=10)

    record_patient_hh_entry = ctk.CTkEntry(
        hh_frame,
        placeholder_text="Patient HH Number",
        width=300
    )
    record_patient_hh_entry.pack(side="left", padx=10)

    file_frame = ctk.CTkFrame(records_frame)
    file_frame.pack(fill="x", pady=10)

    selected_file_label = ctk.CTkLabel(
        file_frame, 
        text="No file selected", 
        width=300
    )
    selected_file_label.pack(side="left", padx=10)

    select_file_btn = ctk.CTkButton(
        file_frame,
        text="Select Medical Record File",
        command=lambda: select_medical_record_file()
    )
    select_file_btn.pack(side="left", padx=10)

    create_btn = ctk.CTkButton(
        records_frame,
        text="Create Medical Record",
        command=lambda: create_medical_record(doctor_info)
    )
    create_btn.pack(pady=10)

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
        selected_file_label.configure(text=os.path.basename(filename))
        return filename

def create_medical_record(doctor_info):
    try:
        patient_hh = record_patient_hh_entry.get()
        if not patient_hh:
            show_message("Error", "Please enter patient HH number")
            return

        if not hasattr(selected_file, 'selected_file'):
            show_message("Error", "Please select a file")
            return

        # Encryption and file handling logic here

        # Create medical record on blockchain logic

        # Log Audit
        log_audit(patient_hh, 0, "Created medical record: {os.path.basename(selected_file)}")

        show_message("Success", "Medical record created successfully")

    except Exception as e:
        show_message("Error", str(e))

def check_patient_access(patient_hh, doctor_hh):
    try:
        # Call smart contract to check access for patient
        has_access = check_patient_access_from_contract(patient_hh, doctor_hh)
        status = "Access Granted" if has_access else "No Access"
        access_status_label.configure(
            text=f"Status: {status}",
            text_color="green" if has_access else "red"
        )
    except Exception as e:
        show_message("Error", str(e))

def show_message(title, message):
    messagebox.showinfo(title, message)

def log_audit(patient_hh, action_type, details):
    # Add audit log entry to blockchain
    pass
