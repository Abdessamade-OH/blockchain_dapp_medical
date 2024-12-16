import customtkinter

def register_page(login_frame):
    # Clear the current frame and display the register page
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Registration page title
    register_label = customtkinter.CTkLabel(login_frame, text="Register", font=("Arial", 32), bg_color="#EAF6F6")
    register_label.pack(pady=(50, 30))

    # Name entry field
    name_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Name", corner_radius=0, width=300)
    name_entry.pack(pady=10)

    # Date of Birth entry field
    dob_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Date of Birth", corner_radius=0, width=300)
    dob_entry.pack(pady=10)

    # Gender entry field
    gender_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Gender", corner_radius=0, width=300)
    gender_entry.pack(pady=10)

    # Blood group entry field
    blood_group_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Blood Group", corner_radius=0, width=300)
    blood_group_entry.pack(pady=10)

    # Address entry field
    address_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Home Address", corner_radius=0, width=300)
    address_entry.pack(pady=10)

    # Email entry field
    email_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Email", corner_radius=0, width=300)
    email_entry.pack(pady=10)

    # Household number entry field
    hh_number_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Household Number", corner_radius=0, width=300)
    hh_number_entry.pack(pady=10)

    # Password entry field
    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
    password_entry.pack(pady=10)

    # Register button
    register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: print("Register clicked"))
    register_button.pack(pady=20)
