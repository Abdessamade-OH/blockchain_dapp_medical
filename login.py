import customtkinter

def login_page(login_frame):
    # Clear the current frame and display the login page
    for widget in login_frame.winfo_children():
        widget.destroy()

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
    register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: print("Register clicked"))
    register_button.pack(pady=10)
