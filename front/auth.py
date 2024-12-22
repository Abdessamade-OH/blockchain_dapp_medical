import customtkinter
from PIL import Image, ImageTk

# Import the specific functions you're using
from login_patient import show_login_patient_page
from login_doctor import show_login_doctor_page
from register_patient import show_register_patient_page
from register_doctor import show_register_doctor_page

import customtkinter
from PIL import Image, ImageTk

def show_auth_page(app):
    # Clear current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Configure grid layout
    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(0, weight=1)

    # Main container with gradient background
    auth_frame = customtkinter.CTkFrame(app, fg_color=("#E3F2FD", "#1A237E"))
    auth_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    auth_frame.grid_columnconfigure(0, weight=1)
    auth_frame.grid_columnconfigure(1, weight=1)
    auth_frame.grid_rowconfigure(0, weight=1)

    # Left side frame for image and welcome text
    left_frame = customtkinter.CTkFrame(auth_frame, fg_color="transparent")
    left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Welcome text above image
    welcome_label = customtkinter.CTkLabel(
        left_frame,
        text="Welcome to HealthCare\nManagement System",
        font=customtkinter.CTkFont(family="Helvetica", size=32, weight="bold"),
        text_color=("#1A237E", "white")
    )
    welcome_label.pack(pady=(20, 10))

    # Subtitle
    subtitle_label = customtkinter.CTkLabel(
        left_frame,
        text="Your trusted healthcare companion",
        font=customtkinter.CTkFont(family="Helvetica", size=16),
        text_color=("#1A237E", "white")
    )
    subtitle_label.pack(pady=(0, 20))

    # Image display
    try:
        image = Image.open("assets/login_img.jpg")
        image = image.resize((600, 600), Image.Resampling.LANCZOS)
        app.auth_image = ImageTk.PhotoImage(image)
        
        image_label = customtkinter.CTkLabel(
            left_frame,
            image=app.auth_image,
            text=""
        )
        image_label.pack(expand=True, fill="both", padx=20)
    except FileNotFoundError:
        print("Image file not found. Check the path.")

    # Right side frame for authentication options
    right_frame = customtkinter.CTkFrame(
        auth_frame,
        fg_color=("white", "#0A1929"),
        corner_radius=15
    )
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Title for auth options
    auth_title = customtkinter.CTkLabel(
        right_frame,
        text="Choose Your Role",
        font=customtkinter.CTkFont(family="Helvetica", size=24, weight="bold"),
        text_color=("#1A237E", "white")
    )
    auth_title.pack(pady=(40, 30))

    # Patient Section
    patient_frame = customtkinter.CTkFrame(right_frame, fg_color="transparent")
    patient_frame.pack(pady=10, padx=30)

    patient_label = customtkinter.CTkLabel(
        patient_frame,
        text="Patient Access",
        font=customtkinter.CTkFont(size=18, weight="bold"),
        text_color=("#1A237E", "white")
    )
    patient_label.pack(pady=(0, 10))

    login_patient_button = customtkinter.CTkButton(
        patient_frame,
        text="Login as Patient",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=40,
        fg_color=("#1565C0", "#42A5F5"),
        hover_color=("#0D47A1", "#1976D2"),
        command=lambda: show_login_patient_page(app, show_auth_page)
    )
    login_patient_button.pack(pady=5)

    register_patient_button = customtkinter.CTkButton(
        patient_frame,
        text="Register as Patient",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=40,
        fg_color="transparent",
        border_width=2,
        border_color=("#1565C0", "#42A5F5"),
        hover_color=("#E3F2FD", "#1A237E"),
        text_color=("#1565C0", "#42A5F5"),
        command=lambda: show_register_patient_page(app, show_auth_page)
    )
    register_patient_button.pack(pady=5)

    # Separator
    separator = customtkinter.CTkFrame(
        right_frame,
        height=2,
        fg_color=("#BDBDBD", "#424242")
    )
    separator.pack(fill="x", padx=30, pady=20)

    # Doctor Section
    doctor_frame = customtkinter.CTkFrame(right_frame, fg_color="transparent")
    doctor_frame.pack(pady=10, padx=30)

    doctor_label = customtkinter.CTkLabel(
        doctor_frame,
        text="Doctor Access",
        font=customtkinter.CTkFont(size=18, weight="bold"),
        text_color=("#1A237E", "white")
    )
    doctor_label.pack(pady=(0, 10))

    login_doctor_button = customtkinter.CTkButton(
        doctor_frame,
        text="Login as Doctor",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=40,
        fg_color=("#1565C0", "#42A5F5"),
        hover_color=("#0D47A1", "#1976D2"),
        command=lambda: show_login_doctor_page(app, show_auth_page)
    )
    login_doctor_button.pack(pady=5)

    register_doctor_button = customtkinter.CTkButton(
        doctor_frame,
        text="Register as Doctor",
        font=customtkinter.CTkFont(size=14),
        corner_radius=8,
        height=40,
        fg_color="transparent",
        border_width=2,
        border_color=("#1565C0", "#42A5F5"),
        hover_color=("#E3F2FD", "#1A237E"),
        text_color=("#1565C0", "#42A5F5"),
        command=lambda: show_register_doctor_page(app, show_auth_page)
    )
    register_doctor_button.pack(pady=5)


# def show_patient_dashboard(app):
#     # Clear the current screen
#     for widget in app.winfo_children():
#         widget.destroy()

#     # Create the dashboard frame
#     dashboard_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
#     dashboard_frame.pack(fill="both", expand=True)

#     # Add some content for patients
#     label = customtkinter.CTkLabel(dashboard_frame, text="Welcome to the Patient Dashboard!", font=("Arial", 24))
#     label.pack(pady=20)

#     logout_button = customtkinter.CTkButton(
#         dashboard_frame, text="Logout", command=lambda: show_auth_page(app)
#     )
#     logout_button.pack(pady=10)


# def show_doctor_dashboard(app):
#     # Clear the current screen
#     for widget in app.winfo_children():
#         widget.destroy()

#     # Create the dashboard frame
#     dashboard_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
#     dashboard_frame.pack(fill="both", expand=True)

#     # Add some content for doctors
#     label = customtkinter.CTkLabel(dashboard_frame, text="Welcome to the Doctor Dashboard!", font=("Arial", 24))
#     label.pack(pady=20)

#     logout_button = customtkinter.CTkButton(
#         dashboard_frame, text="Logout", command=lambda: show_auth_page(app)
#     )
#     logout_button.pack(pady=10)
