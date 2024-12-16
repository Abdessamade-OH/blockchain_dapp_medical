# login_patient.py
import customtkinter
import requests
from utils import validate_input, show_message

LOGIN_URL = "http://127.0.0.1:5000/login"

def login_patient_to_backend(login_frame):
    data = {
        "hh_number": username_entry.get(),
        "password": password_entry.get()
    }

    # Pass 'patient' as the form_type to validate_input
    errors = validate_input(data, "patient")
    if errors:
        for error in errors:
            error_label = customtkinter.CTkLabel(login_frame, text=error, text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=5)
        return

    try:
        response = requests.post(LOGIN_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                show_message(login_frame, "Correct login", "green")
            else:
                show_message(login_frame, result.get("message", "Invalid credentials"), "red")
        else:
            show_message(login_frame, "Error communicating with backend", "red")
    except requests.exceptions.RequestException as e:
        show_message(login_frame, "Request failed. Please check the backend connection.", "red")

def show_login_patient_page(login_frame, auth_page_callback):
    for widget in login_frame.winfo_children():
        widget.destroy()

    login_label = customtkinter.CTkLabel(login_frame, text="Login Patient", font=("Arial", 32), bg_color="#EAF6F6")
    login_label.pack(pady=(50, 30))

    global username_entry, password_entry
    username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="HH Number", corner_radius=0, width=300)
    username_entry.pack(pady=10)

    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=10)

    button_frame = customtkinter.CTkFrame(login_frame, fg_color="#EAF6F6")
    button_frame.pack(pady=20)

    login_button = customtkinter.CTkButton(button_frame, text="Login", corner_radius=0, command=lambda: login_patient_to_backend(login_frame))
    login_button.pack(side="top", fill="x", pady=5)

    back_button = customtkinter.CTkButton(button_frame, text="Back", corner_radius=0, command=lambda: auth_page_callback(login_frame))
    back_button.pack(side="top", fill="x", pady=5)
