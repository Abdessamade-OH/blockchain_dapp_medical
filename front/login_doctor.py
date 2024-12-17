import json
import customtkinter
import requests
from utils import validate_input, show_message
from doctor_dashboard import show_doctor_dashboard  # Import the dashboard function

LOGIN_URL = "http://127.0.0.1:5000/login_doctor"

def login_doctor_to_backend(login_frame, app):
    data = {
        "hh_number": username_entry.get(),
        "password": password_entry.get()
    }

    print("Sending data to backend:", json.dumps(data, indent=4))

    # Define the form type, this will be passed to validate_input
    form_type = "doctor_login"

    # Pass form_type to validate_input
    errors = validate_input(data, form_type)
    if errors:
        # Display validation errors if any
        for error in errors:
            error_label = customtkinter.CTkLabel(login_frame, text=error, text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=5)
        return

    try:
        # Make POST request to backend
        response = requests.post(LOGIN_URL, json=data)
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                show_message(login_frame, "Login successful", "green")

                # Pass doctor info to the dashboard
                doctor_info = result.get("data", {})
                show_doctor_dashboard(app, doctor_info)  # Same dashboard as for patient
            else:
                show_message(login_frame, result.get("message", "Invalid credentials"), "red")
        else:
            # Show error on UI and print to terminal
            error_message = f"Error: {response.status_code} - {response.text}"
            show_message(login_frame, error_message, "red")
            print(f"Backend error: {error_message}")
    
    except requests.exceptions.RequestException as e:
        # Log request exceptions (network issues, server down, etc.) to both terminal and UI
        error_message = f"Request failed: {str(e)}"
        show_message(login_frame, error_message, "red")
        print(f"Request failed: {str(e)}")  # Print error to terminal

def show_login_doctor_page(app, auth_page_callback):
    # Clear the frame and set up the login page
    for widget in app.winfo_children():
        widget.destroy()

    login_label = customtkinter.CTkLabel(app, text="Login Doctor", font=("Arial", 32), bg_color="#EAF6F6")
    login_label.pack(pady=(50, 30))

    global username_entry, password_entry
    username_entry = customtkinter.CTkEntry(app, placeholder_text="HH Number", corner_radius=0, width=300)
    username_entry.pack(pady=10)

    password_entry = customtkinter.CTkEntry(app, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=10)

    button_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
    button_frame.pack(pady=20)

    login_button = customtkinter.CTkButton(
        button_frame, 
        text="Login", 
        corner_radius=0, 
        command=lambda: login_doctor_to_backend(app, app)  # Pass 'app' here (same as in patient login)
    )
    login_button.pack(side="top", fill="x", pady=5)

    back_button = customtkinter.CTkButton(
        button_frame, 
        text="Back", 
        corner_radius=0, 
        command=lambda: auth_page_callback(app)
    )
    back_button.pack(side="top", fill="x", pady=5)
