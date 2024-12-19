# login_patient.py
import customtkinter
import requests
from utils import validate_input, show_message
from patient_dashboard import show_patient_dashboard  # Import the patient dashboard function

LOGIN_URL = "http://127.0.0.1:5000/login"


def login_patient_to_backend(login_frame, app):
    data = {
        "hh_number": username_entry.get(),
        "password": password_entry.get()
    }

    # Pass 'patient' as the form_type to validate_input
    errors = validate_input(data, form_type="patient")
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
                # Show a success message
                show_message(login_frame, "Login successful!", "green")

                # Fetch patient details using the hh_number
                hh_number = data.get("hh_number")
                patient_details_url = f"http://127.0.0.1:5000/get_patient_details?hh_number={hh_number}"
                patient_details_response = requests.get(patient_details_url)

                if patient_details_response.status_code == 200:
                    patient_data = patient_details_response.json().get("patient_data", {})
                    if not patient_data.get("hhNumber"):
                        print("Error: Patient data does not contain hhNumber.")
                    else:
                        print(f"Patient data retrieved successfully: {patient_data}")
                    # Pass patient info to the dashboard
                    show_patient_dashboard(app, patient_data)
                else:
                    show_message(login_frame, "Error fetching patient details", "red")

            else:
                # Show error message on failure
                show_message(login_frame, result.get("message", "Invalid credentials"), "red")
        else:
            show_message(login_frame, "Error communicating with backend", "red")
    except requests.exceptions.RequestException as e:
        show_message(login_frame, "Request failed. Please check the backend connection.", "red")


def show_login_patient_page(app, auth_page_callback):
    # Clear the frame and set up the login page
    for widget in app.winfo_children():
        widget.destroy()

    login_label = customtkinter.CTkLabel(app, text="Login Patient", font=("Arial", 32), bg_color="#EAF6F6")
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
        command=lambda: login_patient_to_backend(app, app)  # Pass 'app' here
    )
    login_button.pack(side="top", fill="x", pady=5)

    back_button = customtkinter.CTkButton(
        button_frame, 
        text="Back", 
        corner_radius=0, 
        command=lambda: auth_page_callback(app)
    )
    back_button.pack(side="top", fill="x", pady=5)
