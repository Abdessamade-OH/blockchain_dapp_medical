import customtkinter
import requests

def show_patient_dashboard(app, patient_info):
    # Clear the current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Dashboard Header
    header_frame = customtkinter.CTkFrame(app, height=80, fg_color="#EAF6F6")
    header_frame.pack(fill="x", pady=10)
    welcome_label = customtkinter.CTkLabel(
        header_frame, 
        text=f"Welcome, {patient_info.get('name', 'Patient')}", 
        font=("Arial", 24)
    )
    welcome_label.pack(side="left", padx=20)
    logout_button = customtkinter.CTkButton(
        header_frame, 
        text="Logout", 
        command=lambda: app.destroy()
    )
    logout_button.pack(side="right", padx=20)

    # Main Content Area
    content_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tabs for different sections
    tab_view = customtkinter.CTkTabview(content_frame, width=700)
    tab_view.pack(fill="both", expand=True)

    # Personal Info Tab
    personal_info_tab = tab_view.add("Personal Info")
    create_personal_info_section(personal_info_tab, patient_info)

    # Medical Records Tab
    medical_records_tab = tab_view.add("Medical Records")
    create_medical_records_section(medical_records_tab)

    # Access Management Tab
    access_management_tab = tab_view.add("Access Management")
    create_access_management_section(access_management_tab, patient_info)

def create_personal_info_section(parent, patient_info):
    info_frame = customtkinter.CTkFrame(parent)
    info_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Display personal info
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
        row = customtkinter.CTkFrame(info_frame)
        row.pack(fill="x", pady=5)
        customtkinter.CTkLabel(row, text=f"{label}:", anchor="w").pack(side="left", padx=5)
        customtkinter.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=5)

def create_medical_records_section(parent):
    label = customtkinter.CTkLabel(parent, text="Medical Records - Coming Soon!", font=("Arial", 16))
    label.pack(pady=20)

def create_access_management_section(parent, patient_info):
    access_frame = customtkinter.CTkFrame(parent)
    access_frame.pack(fill="x", padx=20, pady=20)

    # Input field for Doctor HH number
    input_label = customtkinter.CTkLabel(access_frame, text="Doctor HH Number:")
    input_label.pack(side="left", padx=5)
    
    doctor_hh_entry = customtkinter.CTkEntry(access_frame, width=200)
    doctor_hh_entry.pack(side="left", padx=5)

    # Grant Access Button
    grant_button = customtkinter.CTkButton(
        access_frame, 
        text="Grant Access", 
        command=lambda: grant_access(patient_info, doctor_hh_entry.get())
    )
    grant_button.pack(side="left", padx=5)

def grant_access(patient_info, doctor_hh_number):
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
        else:
            print(f"Failed to grant access: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error granting access: {e}")
