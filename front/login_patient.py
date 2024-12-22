import customtkinter
import requests
from PIL import Image, ImageTk
from utils import validate_input, show_message
from patient_dashboard import show_patient_dashboard

LOGIN_URL = "http://127.0.0.1:5000/login"

def login_patient_to_backend(login_frame, app):
    data = {
        "hh_number": username_entry.get(),
        "password": password_entry.get()
    }

    errors = validate_input(data, form_type="patient")
    if errors:
        for error in errors:
            error_label = customtkinter.CTkLabel(
                login_frame,
                text=error,
                text_color=("#FF1744", "#FF5252"),
                font=customtkinter.CTkFont(size=14)
            )
            error_label.pack(pady=5)
        return

    try:
        response = requests.post(LOGIN_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                show_message(login_frame, "Login successful!", "#00C853")

                hh_number = data.get("hh_number")
                patient_details_url = f"http://127.0.0.1:5000/get_patient_details?hh_number={hh_number}"
                patient_details_response = requests.get(patient_details_url)

                if patient_details_response.status_code == 200:
                    patient_data = patient_details_response.json().get("patient_data", {})
                    if not patient_data.get("hhNumber"):
                        print("Error: Patient data does not contain hhNumber.")
                    else:
                        print(f"Patient data retrieved successfully: {patient_data}")
                    show_patient_dashboard(app, patient_data)
                else:
                    show_message(login_frame, "Error fetching patient details", "#FF1744")
            else:
                show_message(login_frame, result.get("message", "Invalid credentials"), "#FF1744")
        else:
            show_message(login_frame, "Error communicating with backend", "#FF1744")
    except requests.exceptions.RequestException as e:
        show_message(login_frame, "Request failed. Please check the backend connection.", "#FF1744")

def show_login_patient_page(app, auth_page_callback):
    for widget in app.winfo_children():
        widget.destroy()

    # Configure grid layout
    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(0, weight=1)

    # Main container with gradient background
    login_frame = customtkinter.CTkFrame(app, fg_color=("#E3F2FD", "#1A237E"))
    login_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    login_frame.grid_columnconfigure(0, weight=1)
    login_frame.grid_columnconfigure(1, weight=1)
    login_frame.grid_rowconfigure(0, weight=1)

    # Left side frame for image
    left_frame = customtkinter.CTkFrame(login_frame, fg_color="transparent")
    left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Welcome text
    welcome_label = customtkinter.CTkLabel(
        left_frame,
        text="Welcome Back!\nPlease Login to Continue",
        font=customtkinter.CTkFont(family="Helvetica", size=32, weight="bold"),
        text_color=("#1A237E", "white")
    )
    welcome_label.pack(pady=(20, 10))

    # Subtitle
    subtitle_label = customtkinter.CTkLabel(
        left_frame,
        text="Access your healthcare records securely",
        font=customtkinter.CTkFont(family="Helvetica", size=16),
        text_color=("#1A237E", "white")
    )
    subtitle_label.pack(pady=(0, 20))

    # Image display
    try:
        image = Image.open("assets/login_img.jpg")
        image = image.resize((600, 600), Image.Resampling.LANCZOS)
        app.login_image = ImageTk.PhotoImage(image)
        
        image_label = customtkinter.CTkLabel(
            left_frame,
            image=app.login_image,
            text=""
        )
        image_label.pack(expand=True, fill="both", padx=20)
    except FileNotFoundError:
        print("Image file not found. Check the path.")

    # Right side frame for login form
    right_frame = customtkinter.CTkFrame(
        login_frame,
        fg_color=("white", "#0A1929"),
        corner_radius=15
    )
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Login form title
    login_title = customtkinter.CTkLabel(
        right_frame,
        text="Patient Login",
        font=customtkinter.CTkFont(family="Helvetica", size=24, weight="bold"),
        text_color=("#1A237E", "white")
    )
    login_title.pack(pady=(40, 30))

    # Login form
    form_frame = customtkinter.CTkFrame(right_frame, fg_color="transparent")
    form_frame.pack(pady=10, padx=30)

    global username_entry, password_entry
    
    # HH Number entry
    username_entry = customtkinter.CTkEntry(
        form_frame,
        placeholder_text="HH Number",
        font=customtkinter.CTkFont(size=14),
        height=45,
        width=300,
        corner_radius=8
    )
    username_entry.pack(pady=10)

    # Password entry
    password_entry = customtkinter.CTkEntry(
        form_frame,
        placeholder_text="Password",
        show="•",
        font=customtkinter.CTkFont(size=14),
        height=45,
        width=300,
        corner_radius=8
    )
    password_entry.pack(pady=10)

    # Login button
    login_button = customtkinter.CTkButton(
        form_frame,
        text="Login",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=45,
        fg_color=("#1565C0", "#42A5F5"),
        hover_color=("#0D47A1", "#1976D2"),
        command=lambda: login_patient_to_backend(form_frame, app)
    )
    login_button.pack(pady=(20, 10))

    # Back button
    back_button = customtkinter.CTkButton(
        form_frame,
        text="Back to Main Menu",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=45,
        fg_color="transparent",
        border_width=2,
        border_color=("#1565C0", "#42A5F5"),
        hover_color=("#E3F2FD", "#1A237E"),
        text_color=("#1565C0", "#42A5F5"),
        command=lambda: auth_page_callback(app)
    )
    back_button.pack(pady=10)