import json
import customtkinter
import requests
from utils import validate_input, show_message

LOGIN_URL = "http://127.0.0.1:5000/login_doctor"

def login_doctor_to_backend(login_frame):
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

def show_login_doctor_page(login_frame, auth_page_callback):
    # Clear the frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Create and pack the login label
    login_label = customtkinter.CTkLabel(login_frame, text="Login Doctor", font=("Arial", 32), bg_color="#EAF6F6")
    login_label.pack(pady=(50, 30))

    # Define global entries for username and password
    global username_entry, password_entry
    username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="HH Number", corner_radius=0, width=300)
    username_entry.pack(pady=10)

    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=10)

    # Create a frame for the buttons
    button_frame = customtkinter.CTkFrame(login_frame, fg_color="#EAF6F6")
    button_frame.pack(pady=20)

    # Login button triggers the backend login function
    login_button = customtkinter.CTkButton(button_frame, text="Login", corner_radius=0, command=lambda: login_doctor_to_backend(login_frame))
    login_button.pack(side="top", fill="x", pady=5)

    # Back button calls the auth_page_callback to return to the previous page
    back_button = customtkinter.CTkButton(button_frame, text="Back", corner_radius=0, command=lambda: auth_page_callback(login_frame))
    back_button.pack(side="top", fill="x", pady=5)
