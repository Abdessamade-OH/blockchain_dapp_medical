import customtkinter
from PIL import Image, ImageTk

# Import the specific functions you're using
from login_patient import show_login_patient_page
from login_doctor import show_login_doctor_page
from register_patient import show_register_patient_page
from register_doctor import show_register_doctor_page

def show_auth_page(app):
    # Clear current screen by destroying all widgets
    for widget in app.winfo_children():
        widget.destroy()

    # Main container frame to pack everything into
    auth_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
    auth_frame.pack(fill="both", expand=True)

    # Left-side image frame
    image_frame = customtkinter.CTkFrame(auth_frame, fg_color="#EAF6F6")
    image_frame.pack(side="left", fill="both", expand=True)

    # Load and display the image each time we enter the auth page
    try:
        # Open and resize the image to fit the left side
        image = Image.open("assets/login_img.jpg")  # Replace with your image path
        image = image.resize((700, 900), Image.Resampling.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)  # Create the PhotoImage object

        # Clear any previous image in the frame and add the new one
        for widget in image_frame.winfo_children():
            widget.destroy()  # Clear previous image if any

        # Place the image in the frame
        image_label = customtkinter.CTkLabel(image_frame, image=image_tk, text="")
        image_label.place(relx=0.5, rely=0.5, anchor="center")
    except FileNotFoundError:
        print("Image file not found. Check the path.")

    # Right-side frame for buttons
    button_frame = customtkinter.CTkFrame(auth_frame, fg_color="#EAF6F6", corner_radius=0)
    button_frame.pack(side="right", fill="both", expand=True)

    # Buttons to navigate to respective pages
    login_patient_button = customtkinter.CTkButton(
        button_frame, 
        text="Login Patient", 
        corner_radius=0, 
        width=300, 
        command=lambda: show_login_patient_page(app, show_auth_page)
    )
    login_patient_button.pack(pady=10)

    login_doctor_button = customtkinter.CTkButton(
        button_frame, 
        text="Login Doctor", 
        corner_radius=0, 
        width=300, 
        command=lambda: show_login_doctor_page(app, show_auth_page)
    )
    login_doctor_button.pack(pady=10)

    register_patient_button = customtkinter.CTkButton(
        button_frame, 
        text="Register Patient", 
        corner_radius=0, 
        width=300, 
        command=lambda: show_register_patient_page(app, show_auth_page)
    )
    register_patient_button.pack(pady=10)

    register_doctor_button = customtkinter.CTkButton(
        button_frame, 
        text="Register Doctor", 
        corner_radius=0, 
        width=300, 
        command=lambda: show_register_doctor_page(app, show_auth_page)
    )
    register_doctor_button.pack(pady=10)


def show_patient_dashboard(app):
    # Clear the current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Create the dashboard frame
    dashboard_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
    dashboard_frame.pack(fill="both", expand=True)

    # Add some content for patients
    label = customtkinter.CTkLabel(dashboard_frame, text="Welcome to the Patient Dashboard!", font=("Arial", 24))
    label.pack(pady=20)

    logout_button = customtkinter.CTkButton(
        dashboard_frame, text="Logout", command=lambda: show_auth_page(app)
    )
    logout_button.pack(pady=10)


def show_doctor_dashboard(app):
    # Clear the current screen
    for widget in app.winfo_children():
        widget.destroy()

    # Create the dashboard frame
    dashboard_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
    dashboard_frame.pack(fill="both", expand=True)

    # Add some content for doctors
    label = customtkinter.CTkLabel(dashboard_frame, text="Welcome to the Doctor Dashboard!", font=("Arial", 24))
    label.pack(pady=20)

    logout_button = customtkinter.CTkButton(
        dashboard_frame, text="Logout", command=lambda: show_auth_page(app)
    )
    logout_button.pack(pady=10)
