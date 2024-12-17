# doctor_dashboard.py
import customtkinter as ctk
import requests
from utils import show_message

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
    create_personal_info_section(personal_info_tab, doctor_info)

    # Patient Records Tab
    patient_records_tab = tab_view.add("Patient Records")
    create_patient_records_section(patient_records_tab)

    # Access Management Tab
    access_management_tab = tab_view.add("Access Management")
    create_access_management_section(access_management_tab, doctor_info)

def create_personal_info_section(parent, doctor_info):
    info_frame = ctk.CTkFrame(parent)
    info_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Display doctor info
    info_labels = [
        ("Wallet Address", doctor_info.get("walletAddress", "N/A")),
        ("Name", doctor_info.get("name", "N/A")),
        ("Specialization", doctor_info.get("specialization", "N/A")),
        ("Hospital", doctor_info.get("hospitalName", "N/A")),
        ("Health Number", doctor_info.get("hhNumber", "N/A"))
    ]

    for label, value in info_labels:
        row = ctk.CTkFrame(info_frame)
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=f"{label}:", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=5)

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