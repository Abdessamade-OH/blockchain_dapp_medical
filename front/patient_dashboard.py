from tkinter import messagebox
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

    # Create labels for static info
    for label, value in info_labels:
        row = customtkinter.CTkFrame(info_frame)
        row.pack(fill="x", pady=5)
        customtkinter.CTkLabel(row, text=f"{label}:", anchor="w").pack(side="left", padx=5)
        customtkinter.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=5)

    # Fields for editable information (home address and email)
    row_home_address = customtkinter.CTkFrame(info_frame)
    row_home_address.pack(fill="x", pady=5)
    customtkinter.CTkLabel(row_home_address, text="Home Address:", anchor="w").pack(side="left", padx=5)
    home_address_entry = customtkinter.CTkEntry(row_home_address)
    home_address_entry.insert(0, patient_info.get("homeAddress", ""))
    home_address_entry.pack(side="left", padx=5)

    row_email = customtkinter.CTkFrame(info_frame)
    row_email.pack(fill="x", pady=5)
    customtkinter.CTkLabel(row_email, text="Email:", anchor="w").pack(side="left", padx=5)
    email_entry = customtkinter.CTkEntry(row_email)
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
    update_button.pack(pady=20)

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
        command=lambda: grant_access(patient_info, doctor_hh_entry.get(), table_frame)
    )
    grant_button.pack(side="left", padx=5)

    # Table for displaying doctors with granted access
    table_frame = customtkinter.CTkFrame(parent)
    table_frame.pack(fill="x", padx=20, pady=20)

    # Fetch and display doctors with access
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
    header_row = customtkinter.CTkFrame(table_frame)
    header_row.pack(fill="x", pady=5)
    headers = ["Name", "HH Number", "Actions"]
    for header in headers:
        customtkinter.CTkLabel(header_row, text=header, width=200, anchor="w", font=("Arial", 14, "bold")).pack(side="left", padx=5)

    # Table rows
    for doctor in doctors:
        row_frame = customtkinter.CTkFrame(table_frame)
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
