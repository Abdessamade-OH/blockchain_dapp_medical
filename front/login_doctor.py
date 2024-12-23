import customtkinter
import requests
from PIL import Image, ImageTk
from utils import validate_input, show_message
from doctor_dashboard import show_doctor_dashboard

LOGIN_URL = "http://127.0.0.1:5000/login_doctor"

def login_doctor_to_backend(login_frame, app):
    data = {
        "hh_number": username_entry.get(),
        "password": password_entry.get()
    }

    errors = validate_input(data, "doctor_login")
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
                show_message(login_frame, "Login successful!", "#22c55e")

                hh_number = data.get("hh_number")
                doctor_details_url = f"http://127.0.0.1:5000/get_doctor_details?hh_number={hh_number}"
                doctor_details_response = requests.get(doctor_details_url)

                if doctor_details_response.status_code == 200:
                    doctor_data = doctor_details_response.json().get("doctor_data", {})
                    show_doctor_dashboard(app, doctor_data)
                else:
                    show_message(login_frame, "Error fetching doctor details", "#FF1744")
            else:
                show_message(login_frame, result.get("message", "Invalid credentials"), "#FF1744")
        else:
            show_message(login_frame, "Error communicating with backend", "#FF1744")
    except requests.exceptions.RequestException as e:
        show_message(login_frame, "Request failed. Please check the backend connection.", "#FF1744")

def show_login_doctor_page(app, auth_page_callback):
    for widget in app.winfo_children():
        widget.destroy()

    # Configure grid layout
    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(0, weight=1)

    # Set color scheme to match the patient page
    COLORS = {
        'primary': "#2563eb",      # Blue
        'secondary': "#f8fafc",    # Light gray
        'accent': "#3b82f6",       # Lighter blue
        'text': "#1e293b",         # Dark gray
        'success': "#22c55e",      # Green
        'warning': "#f59e0b"       # Orange
    }

    # Main container with gradient background
    login_frame = customtkinter.CTkFrame(app, fg_color=("white", COLORS['secondary']))
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
        text="Welcome Doctor!\nPlease Login to Continue",
        font=customtkinter.CTkFont(family="Helvetica", size=32, weight="bold"),
        text_color=COLORS['primary']
    )
    welcome_label.pack(pady=(20, 10))

    # Subtitle
    subtitle_label = customtkinter.CTkLabel(
        left_frame,
        text="Access your medical practice portal securely",
        font=customtkinter.CTkFont(family="Helvetica", size=16),
        text_color=COLORS['text']
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
        fg_color=("white", COLORS['primary']),
        corner_radius=15
    )
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Login form title
    login_title = customtkinter.CTkLabel(
        right_frame,
        text="Doctor Login",
        font=customtkinter.CTkFont(family="Helvetica", size=24, weight="bold"),
        text_color=COLORS['text']
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

    # Login button with updated color scheme
    login_button = customtkinter.CTkButton(
        form_frame,
        text="Login",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=45,
        fg_color=COLORS['primary'],
        hover_color=COLORS['accent'],
        command=lambda: login_doctor_to_backend(form_frame, app)
    )
    login_button.pack(pady=(20, 10))

    # Back button with updated color scheme
    back_button = customtkinter.CTkButton(
        form_frame,
        text="Back to Main Menu",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=45,
        fg_color="transparent",
        border_width=2,
        border_color=COLORS['primary'],
        hover_color=COLORS['secondary'],
        text_color=COLORS['primary'],
        command=lambda: auth_page_callback(app)
    )
    back_button.pack(pady=10)
