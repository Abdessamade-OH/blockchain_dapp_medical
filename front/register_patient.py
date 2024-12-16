import customtkinter
import requests
from utils import validate_input, show_message  # Helper functions (if needed)

REGISTER_URL = "http://127.0.0.1:5000/register"

def show_login_from_register(register_frame, login_page_callback):
    login_page_callback()

def register_patient_to_backend(register_frame):
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

    errors = validate_input(data)
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

def show_register_patient_page(register_frame, login_page_callback):
    for widget in register_frame.winfo_children():
        widget.destroy()

    register_label = customtkinter.CTkLabel(register_frame, text="Register Patient", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    # Create a scrollable frame for the register form
    scrollable_frame = customtkinter.CTkScrollableFrame(register_frame)
    scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)

    global name_entry, dob_entry, gender_entry, blood_group_entry, address_entry, email_entry, hh_number_entry, password_entry_reg
    name_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    dob_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Date of Birth", corner_radius=0, width=300)
    dob_entry.pack(pady=10)

    gender_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Gender", corner_radius=0, width=300)
    gender_entry.pack(pady=10)

    blood_group_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Blood Group", corner_radius=0, width=300)
    blood_group_entry.pack(pady=10)

    address_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Home Address", corner_radius=0, width=300)
    address_entry.pack(pady=10)

    email_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Email", corner_radius=0, width=300)
    email_entry.pack(pady=10)

    hh_number_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Health ID Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    password_entry_reg = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry_reg.pack(pady=10)

    # Register button
    register_button = customtkinter.CTkButton(scrollable_frame, text="Register", corner_radius=0, command=lambda: register_patient_to_backend(register_frame))
    register_button.pack(pady=20)

    # Back to login button
    back_button = customtkinter.CTkButton(scrollable_frame, text="Back to Login", corner_radius=0, command=lambda: show_login_from_register(register_frame, login_page_callback))
    back_button.pack(pady=5)

