# patient_dashboard.py
import customtkinter

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
    create_access_management_section(access_management_tab)

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

def create_access_management_section(parent):
    label = customtkinter.CTkLabel(parent, text="Access Management - Coming Soon!", font=("Arial", 16))
    label.pack(pady=20)
