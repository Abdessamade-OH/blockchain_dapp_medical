import customtkinter
from PIL import Image, ImageTk

# Set custom tkinter appearance and theme
customtkinter.set_appearance_mode("light")  # Light mode for a pastel theme
customtkinter.set_default_color_theme("green")  # Choose a softer color theme

# Initialize the app
app = customtkinter.CTk()  # Create CTk window
app.geometry("900x600")  # Fixed window size
app.resizable(False, False)  # Disable resizing/zooming

# Set the background color to a pastel shade
app.configure(bg="#EAF6F6")  # A light pastel green-blue color

# Left-side image frame
image_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6")  # Transparent frame
image_frame.grid(row=0, column=0, sticky="nsew")

# Open the image and resize it to exactly fit half the screen
image = Image.open("assets/login_img.jpg")  # Replace with the path to your image
image = image.resize((600, 800), Image.Resampling.LANCZOS)  # Resize to 600x800 to perfectly fit
image_tk = ImageTk.PhotoImage(image)

# Place the image in the frame
image_label = customtkinter.CTkLabel(image_frame, image=image_tk, text="")
image_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the image

# Right-side login form frame
login_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6", corner_radius=0)
login_frame.grid(row=0, column=1, sticky="nsew")

# Login label
login_label = customtkinter.CTkLabel(login_frame, text="Login", font=("Arial", 32), bg_color="#EAF6F6")
login_label.pack(pady=(50, 30))

# Username entry field
username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Username or Email", corner_radius=0, width=300)
username_entry.pack(pady=15)

# Password entry field
password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
password_entry.pack(pady=15)

# Login button
login_button = customtkinter.CTkButton(login_frame, text="Login", corner_radius=0, command=lambda: print("Login clicked"))
login_button.pack(pady=30)

# Register button
register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: register_page())
register_button.pack(pady=10)

# Register Page Function
def register_page():
    # Clear the current frame and display the register page
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Create a canvas widget for scrolling
    canvas = customtkinter.CTkCanvas(login_frame, bg="#EAF6F6")
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    # Add a scrollbar to the canvas
    scrollbar = customtkinter.CTkScrollbar(login_frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to contain all the widgets
    register_frame = customtkinter.CTkFrame(canvas, fg_color="#EAF6F6", corner_radius=0)
    canvas.create_window((0, 0), window=register_frame, anchor="nw")

    # Back button at the top
    back_button = customtkinter.CTkButton(register_frame, text="Back to Login", corner_radius=0, command=lambda: show_login_page())
    back_button.pack(pady=(20, 10))

    # Registration page title
    register_label = customtkinter.CTkLabel(register_frame, text="Register", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    # Name entry field
    name_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    # Date of Birth entry field
    dob_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Date of Birth", corner_radius=0, width=300)
    dob_entry.pack(pady=10)

    # Gender entry field
    gender_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Gender", corner_radius=0, width=300)
    gender_entry.pack(pady=10)

    # Blood group entry field
    blood_group_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Blood Group", corner_radius=0, width=300)
    blood_group_entry.pack(pady=10)

    # Address entry field
    address_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Home Address", corner_radius=0, width=300)
    address_entry.pack(pady=10)

    # Email entry field
    email_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Email", corner_radius=0, width=300)
    email_entry.pack(pady=10)

    # Household number entry field
    hh_number_entry = customtkinter.CTkEntry(register_frame, placeholder_text="Household Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    # Password entry field
    password_entry_reg = customtkinter.CTkEntry(register_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry_reg.pack(pady=10)

    # Register button
    register_button = customtkinter.CTkButton(register_frame, text="Register", corner_radius=0, command=lambda: print("Register clicked"))
    register_button.pack(pady=20)

    # Update the scroll region of the canvas so that it covers all widgets
    register_frame.update_idletasks()  # Make sure all widgets are rendered
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to show the login page
def show_login_page():
    # Clear the current register frame and show the login frame again
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Recreate login elements
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

# Adjust grid weights to split the app into two equal halves
app.grid_columnconfigure(0, weight=1)  # Left (image) column
app.grid_columnconfigure(1, weight=1)  # Right (login) column
app.grid_rowconfigure(0, weight=1)  # Single row spanning the full height

# Start with login page
show_login_page()

# Start the app
app.mainloop()
