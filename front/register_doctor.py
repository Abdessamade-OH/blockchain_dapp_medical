# register_doctor.py
import customtkinter
import requests
from utils import validate_input, show_message  # Helper functions (if needed)

REGISTER_URL = "http://127.0.0.1:5000/register"

def show_login_from_register(register_frame, login_page_callback):
    login_page_callback()

def register_doctor_to_backend(register_frame):
    data = {
        "wallet_address": wallet_address_entry.get(),
        "name": name_entry.get(),
        "specialization": specialization_entry.get(),
        "hospital_name": hospital_name_entry.get(),
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

def show_register_doctor_page(register_frame, login_page_callback):
    for widget in register_frame.winfo_children():
        widget.destroy()

    register_label = customtkinter.CTkLabel(register_frame, text="Register Doctor", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    # Create a scrollable frame for the register form
    scrollable_frame = customtkinter.CTkScrollableFrame(register_frame)
    scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)

    global name_entry, specialization_entry, hospital_name_entry, hh_number_entry, password_entry_reg, wallet_address_entry
    wallet_address_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Wallet Address", corner_radius=0, width=300)
    wallet_address_entry.pack(pady=10)

    name_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    specialization_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Specialization", corner_radius=0, width=300)
    specialization_entry.pack(pady=10)

    hospital_name_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Hospital Name", corner_radius=0, width=300)
    hospital_name_entry.pack(pady=10)

    hh_number_entry = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Household Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    password_entry_reg = customtkinter.CTkEntry(scrollable_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry_reg.pack(pady=10)

    back_button = customtkinter.CTkButton(scrollable_frame, text="Back to Login", corner_radius=0, command=lambda: show_login_from_register(register_frame, login_page_callback))
    back_button.pack(pady=10)

    register_button = customtkinter.CTkButton(scrollable_frame, text="Register Doctor", corner_radius=0, command=lambda: register_doctor_to_backend(register_frame))
    register_button.pack(pady=20)
