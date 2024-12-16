# login.py
import customtkinter
import requests
from utils import validate_input, show_message  # Helper functions (if needed)

LOGIN_URL = "http://127.0.0.1:5000/login"

def show_register_from_login(login_frame, register_page_callback):
    # Call the function to show the register page using the callback
    register_page_callback()

def login_user_to_backend(login_frame):
    global username_entry, password_entry

    username = username_entry.get()
    password = password_entry.get()

    data = {
        "hh_number": username,
        "password": password
    }

    errors = validate_input(data)
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

def show_login_page(login_frame, register_page_callback):
    for widget in login_frame.winfo_children():
        widget.destroy()

    login_label = customtkinter.CTkLabel(login_frame, text="Login", font=("Arial", 32), bg_color="#EAF6F6")
    login_label.pack(pady=(50, 30))

    global username_entry, password_entry
    username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="HH Number", corner_radius=0, width=300)
    username_entry.pack(pady=10)

    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=10)

    login_button = customtkinter.CTkButton(login_frame, text="Login", corner_radius=0, command=lambda: login_user_to_backend(login_frame))
    login_button.pack(pady=20)

    register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: show_register_from_login(login_frame, register_page_callback))
    register_button.pack(pady=20)
