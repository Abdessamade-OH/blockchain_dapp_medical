import customtkinter
import requests
from PIL import Image, ImageTk

# Set custom tkinter appearance and theme
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("green")

# Initialize the app
app = customtkinter.CTk()
app.geometry("900x600")
app.resizable(False, False)

# Define backend URLs
REGISTER_URL = "http://127.0.0.1:5000/register"  # Update if needed
LOGIN_URL = "http://127.0.0.1:5000/login"  # For login functionality

# Function to validate user input
def validate_input(data):
    errors = []
    for key, value in data.items():
        if not value.strip():
            errors.append(f"{key.capitalize()} is required.")
    return errors

# Function to send registration data to backend
def register_patient_to_backend(register_frame):
    data = {
        "name": name_entry.get(),
        "dob": dob_entry.get(),
        "gender": gender_entry.get(),
        "blood_group": blood_group_entry.get(),
        "address": address_entry.get(),
        "email": email_entry.get(),
        "hh_number": hh_number_entry.get(),
        "password": password_entry_reg.get()
    }

    # Validate input
    errors = validate_input(data)
    if errors:
        for error in errors:
            error_label = customtkinter.CTkLabel(register_frame, text=error, text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=5)
        return

    # Send the data to the backend
    try:
        response = requests.post(REGISTER_URL, json=data)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("Patient registered successfully")
                # Redirect to login page with success message
                show_login_page(success_message="Registration successful. Please log in.")
            else:
                error_message = result.get("message", "Unknown error occurred")
                print(f"Error: {error_message}")
                error_label = customtkinter.CTkLabel(register_frame, text=error_message, text_color="red", bg_color="#EAF6F6")
                error_label.pack(pady=10)
        else:
            error_label = customtkinter.CTkLabel(register_frame, text="Error communicating with backend", text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=10)
            print("Error communicating with backend:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request Exception:", str(e))
        error_label = customtkinter.CTkLabel(register_frame, text="Request failed. Please check the backend connection.", text_color="red", bg_color="#EAF6F6")
        error_label.pack(pady=10)

# Function to send login data to backend
def login_user_to_backend(username, password, login_frame):
    data = {
        "username": username,
        "password": password
    }

    # Validate input
    errors = validate_input(data)
    if errors:
        for error in errors:
            error_label = customtkinter.CTkLabel(login_frame, text=error, text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=5)
        return

    # Send the data to the backend
    try:
        response = requests.post(LOGIN_URL, json=data)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("Login successful")
                # Show dashboard or next page
                # For now, we just print a success message
                success_label = customtkinter.CTkLabel(login_frame, text="Login successful", text_color="green", bg_color="#EAF6F6")
                success_label.pack(pady=10)
            else:
                error_message = result.get("message", "Unknown error occurred")
                print(f"Error: {error_message}")
                error_label = customtkinter.CTkLabel(login_frame, text=error_message, text_color="red", bg_color="#EAF6F6")
                error_label.pack(pady=10)
        else:
            error_label = customtkinter.CTkLabel(login_frame, text="Error communicating with backend", text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=10)
            print("Error communicating with backend:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request Exception:", str(e))
        error_label = customtkinter.CTkLabel(login_frame, text="Request failed. Please check the backend connection.", text_color="red", bg_color="#EAF6F6")
        error_label.pack(pady=10)

# Initialize the UI layout
app.grid_columnconfigure(0, weight=1)  # Left column
app.grid_columnconfigure(1, weight=1)  # Right column
app.grid_rowconfigure(0, weight=1)  # Single row spanning the full height

# Left-side image frame
image_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
image_frame.grid(row=0, column=0, sticky="nsew")

# Open the image and resize it to fit
try:
    image = Image.open("assets/login_img.jpg")  # Replace with your image path
    image = image.resize((600, 800), Image.Resampling.LANCZOS)
    image_tk = ImageTk.PhotoImage(image)
    image_label = customtkinter.CTkLabel(image_frame, image=image_tk, text="")
    image_label.place(relx=0.5, rely=0.5, anchor="center")
except FileNotFoundError:
    print("Image file not found. Check the path.")

# Right-side login form frame
login_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6", corner_radius=0)
login_frame.grid(row=0, column=1, sticky="nsew")

# Register page function
def register_page():
    # Clear current login frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Create canvas for scrollable content
    canvas = customtkinter.CTkCanvas(login_frame, bg="#EAF6F6")
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    # Add a scrollbar to the canvas
    scrollbar = customtkinter.CTkScrollbar(login_frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the widgets
    register_frame = customtkinter.CTkFrame(canvas, fg_color="#EAF6F6", corner_radius=0)
    canvas.create_window((0, 0), window=register_frame, anchor="nw")

    # Back button
    back_button = customtkinter.CTkButton(register_frame, text="Back to Login", corner_radius=0, command=lambda: show_login_page())
    back_button.pack(pady=(20, 10))

    # Registration title
    register_label = customtkinter.CTkLabel(register_frame, text="Register", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    # Create all registration form fields
    global name_entry, dob_entry, gender_entry, blood_group_entry, address_entry, email_entry, hh_number_entry, password_entry_reg
    name_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    dob_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Date of Birth", corner_radius=0, width=300)
    dob_entry.pack(pady=10)

    gender_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Gender", corner_radius=0, width=300)
    gender_entry.pack(pady=10)

    blood_group_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Blood Group", corner_radius=0, width=300)
    blood_group_entry.pack(pady=10)

    address_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Home Address", corner_radius=0, width=300)
    address_entry.pack(pady=10)

    email_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Email", corner_radius=0, width=300)
    email_entry.pack(pady=10)

    hh_number_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Household Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    password_entry_reg = customtkinter.CTkEntry(register_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry_reg.pack(pady=10)

    # Register button
    register_button = customtkinter.CTkButton(register_frame, text="Register", corner_radius=0, command=lambda: register_patient_to_backend(register_frame))
    register_button.pack(pady=20)

# Function to show login page
def show_login_page(success_message=None):
    # Clear current frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Create canvas for scrollable content
    canvas = customtkinter.CTkCanvas(login_frame, bg="#EAF6F6")
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    # Add a scrollbar to the canvas
    scrollbar = customtkinter.CTkScrollbar(login_frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the widgets
    login_frame_inside = customtkinter.CTkFrame(canvas, fg_color="#EAF6F6", corner_radius=0)
    canvas.create_window((0, 0), window=login_frame_inside, anchor="nw")

    # Success message if any
    if success_message:
        success_label = customtkinter.CTkLabel(login_frame_inside, text=success_message, text_color="green", bg_color="#EAF6F6")
        success_label.pack(pady=10)

    # Login title
    login_label = customtkinter.CTkLabel(login_frame_inside, text="Login", font=("Arial", 32), bg_color="#EAF6F6")
    login_label.pack(pady=(50, 30))

    # Create all login form fields
    username_entry = customtkinter.CTkEntry(login_frame_inside, placeholder_text="Username", corner_radius=0, width=300)
    username_entry.pack(pady=10)

    password_entry = customtkinter.CTkEntry(login_frame_inside, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=10)

    # Login button
    login_button = customtkinter.CTkButton(login_frame_inside, text="Login", corner_radius=0, command=lambda: login_user_to_backend(username_entry.get(), password_entry.get(), login_frame_inside))
    login_button.pack(pady=20)

    # Register button
    register_button = customtkinter.CTkButton(login_frame_inside, text="Register", corner_radius=0, command=register_page)
    register_button.pack(pady=20)

# Initial load of the login page
show_login_page()

# Run the app
app.mainloop()
