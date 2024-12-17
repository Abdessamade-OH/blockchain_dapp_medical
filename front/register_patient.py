# register_patient.py
import customtkinter
import requests
from utils import validate_input, show_message

REGISTER_URL = "http://127.0.0.1:5000/register"

def register_patient_to_backend(register_frame):
    form_type = "patient" 
    data = {
        "name": name_entry.get(),
        "dob": dob_entry.get(),
        "gender": gender_entry.get(),
        "blood_group": blood_group_entry.get(),
        "address": address_entry.get(),
        "email": email_entry.get(),
        "hh_number": hh_number_entry.get(),
        "password": password_entry_reg.get()
    }

    errors = validate_input(data, form_type)
    if errors:
        for error in errors:
            error_label = customtkinter.CTkLabel(register_frame, text=error, text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=5)
        return

    try:
        response = requests.post(REGISTER_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                show_message(register_frame, "Registration successful. Please log in.", "green")
            else:
                show_message(register_frame, result.get("message", "Unknown error occurred"), "red")
        else:
            show_message(register_frame, "Error communicating with backend", "red")
    except requests.exceptions.RequestException as e:
        show_message(register_frame, "Request failed. Please check the backend connection.", "red")

def show_register_patient_page(register_frame, auth_page_callback):
    for widget in register_frame.winfo_children():
        widget.destroy()

    register_label = customtkinter.CTkLabel(register_frame, text="Register Patient", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    global name_entry, dob_entry, gender_entry, blood_group_entry, address_entry, email_entry, hh_number_entry, password_entry_reg
    name_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    dob_entry = customtkinter.CTkEntry(register_frame, placeholder_text="DOB", corner_radius=0, width=300)
    dob_entry.pack(pady=10)

    gender_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Gender", corner_radius=0, width=300)
    gender_entry.pack(pady=10)

    blood_group_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Blood Group", corner_radius=0, width=300)
    blood_group_entry.pack(pady=10)

    address_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Address", corner_radius=0, width=300)
    address_entry.pack(pady=10)

    email_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Email", corner_radius=0, width=300)
    email_entry.pack(pady=10)

    hh_number_entry = customtkinter.CTkEntry(register_frame, placeholder_text="HH Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    password_entry_reg = customtkinter.CTkEntry(register_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry_reg.pack(pady=10)

    button_frame = customtkinter.CTkFrame(register_frame, fg_color="#EAF6F6")
    button_frame.pack(pady=20)

    register_button = customtkinter.CTkButton(button_frame, text="Register", corner_radius=0, command=lambda: register_patient_to_backend(register_frame))
    register_button.pack(side="top", fill="x", pady=5)

    back_button = customtkinter.CTkButton(button_frame, text="Back", corner_radius=0, command=lambda: auth_page_callback(register_frame))
    back_button.pack(side="top", fill="x", pady=5)
