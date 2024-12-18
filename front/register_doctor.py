# register_doctor.py
import customtkinter
import requests
from utils import validate_input, show_message

REGISTER_URL = "http://127.0.0.1:5000/register_doctor"  # Adjusted URL for doctor registration

def register_doctor_to_backend(register_frame):
    # Prepare the data without the wallet address and remove validation checks for legacy fields
    data = {
        "name": name_entry.get(),
        "specialization": specialization_entry.get(),
        "hospital_name": hospital_name_entry.get(),
        "hh_number": hh_number_entry.get(),
        "password": password_entry_reg.get()
    }

    # Remove input validation for the wallet address and ensure only required fields are validated
    errors = validate_input(data, form_type="doctor")  # Assuming validation only checks the required fields now
    if errors:
        for error in errors:
            error_label = customtkinter.CTkLabel(register_frame, text=error, text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=5)
        return

    try:
        # Send POST request to backend for doctor registration
        response = requests.post(REGISTER_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                show_message(register_frame, "Registration successful. Please log in.", "green")
            else:
                show_message(register_frame, result.get("error", "Unknown error occurred"), "red")
        else:
            show_message(register_frame, "Error communicating with backend", "red")
    except requests.exceptions.RequestException as e:
        show_message(register_frame, "Request failed. Please check the backend connection.", "red")

def show_register_doctor_page(register_frame, auth_page_callback):
    # Clear existing widgets
    for widget in register_frame.winfo_children():
        widget.destroy()

    register_label = customtkinter.CTkLabel(register_frame, text="Register Doctor", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    # Global entries for the fields
    global name_entry, specialization_entry, hospital_name_entry, hh_number_entry, password_entry_reg
    name_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    specialization_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Specialization", corner_radius=0, width=300)
    specialization_entry.pack(pady=10)

    hospital_name_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Hospital Name", corner_radius=0, width=300)
    hospital_name_entry.pack(pady=10)

    hh_number_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Household Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    password_entry_reg = customtkinter.CTkEntry(register_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry_reg.pack(pady=10)

    # Button frame for register and back buttons
    button_frame = customtkinter.CTkFrame(register_frame, fg_color="#EAF6F6")
    button_frame.pack(pady=20)

    register_button = customtkinter.CTkButton(button_frame, text="Register", corner_radius=0, command=lambda: register_doctor_to_backend(register_frame))
    register_button.pack(side="top", fill="x", pady=5)

    back_button = customtkinter.CTkButton(button_frame, text="Back", corner_radius=0, command=lambda: auth_page_callback(register_frame))
    back_button.pack(side="top", fill="x", pady=5)
