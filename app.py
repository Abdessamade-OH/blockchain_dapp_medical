import customtkinter
import requests

# Set custom tkinter appearance and theme
customtkinter.set_appearance_mode("light")  
customtkinter.set_default_color_theme("green")  

# Initialize the app
app = customtkinter.CTk()  
app.geometry("900x600")  
app.resizable(False, False)  

# Define backend URL
BACKEND_URL = "http://127.0.0.1:5000/register"

# Function to send registration data to backend
def register_patient_to_backend():
    data = {
        "name": name_entry.get(),
        "dob": dob_entry.get(),
        "gender": gender_entry.get(),
        "blood_group": blood_group_entry.get(),
        "address": address_entry.get(),
        "email": email_entry.get(),
        "hh_number": hh_number_entry.get(),
        "password": password_entry_reg.get(),
        "private_key": "your_private_key_here"  # Get private key securely
    }

    # Send the data to the backend
    response = requests.post(BACKEND_URL, json=data)

    # Handle the response
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success":
            print("Patient registered successfully")
            # Optionally show a success message in the UI
            success_label = customtkinter.CTkLabel(register_frame, text="Registration Successful!", text_color="green", bg_color="#EAF6F6")
            success_label.pack(pady=10)
        else:
            print(f"Error: {result['message']}")
            # Optionally show an error message in the UI
            error_label = customtkinter.CTkLabel(register_frame, text=f"Error: {result['message']}", text_color="red", bg_color="#EAF6F6")
            error_label.pack(pady=10)
    else:
        print("Error communicating with backend")
        # Show error in the UI
        error_label = customtkinter.CTkLabel(register_frame, text="Error communicating with backend", text_color="red", bg_color="#EAF6F6")
        error_label.pack(pady=10)

# Initialize the UI layout
app.grid_columnconfigure(0, weight=1)  # Left column
app.grid_columnconfigure(1, weight=1)  # Right column
app.grid_rowconfigure(0, weight=1)  # Single row spanning the full height

# Left-side image frame
image_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")
image_frame.grid(row=0, column=0, sticky="nsew")

# Open the image and resize it to fit
image = Image.open("assets/login_img.jpg")  # Replace with your image path
image = image.resize((600, 800), Image.Resampling.LANCZOS)
image_tk = ImageTk.PhotoImage(image)

# Place the image in the frame
image_label = customtkinter.CTkLabel(image_frame, image=image_tk, text="")
image_label.place(relx=0.5, rely=0.5, anchor="center")

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
    register_button = customtkinter.CTkButton(register_frame, text="Register", corner_radius=0, command=register_patient_to_backend)
    register_button.pack(pady=20)

    # Update canvas scroll region
    register_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Show the login page
def show_login_page():
    # Clear current register frame and show login page
    for widget in login_frame.winfo_children():
        widget.destroy()

    login_label = customtkinter.CTkLabel(login_frame, text="Login", font=("Arial", 32), bg_color="#EAF6F6")
    login_label.pack(pady=(50, 30))

    username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Username or Email", corner_radius=0, width=300)
    username_entry.pack(pady=15)

    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=15)

    login_button = customtkinter.CTkButton(login_frame, text="Login", corner_radius=0, command=lambda: print("Login clicked"))
    login_button.pack(pady=30)

    register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: register_page())
    register_button.pack(pady=10)

# Start with the login page
show_login_page()

# Start the app
app.mainloop()
