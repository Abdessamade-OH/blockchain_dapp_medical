import customtkinter

# Create a function to show the register page
def show_register_page(app):
    # Importing the register view when this function is called
    import register

    # Hide current (login) page
    login_frame.grid_forget()

    # Call the function to display the register page
    register.show_register_page(app)

# Login page layout
login_frame = customtkinter.CTkFrame()

# Title
login_label = customtkinter.CTkLabel(login_frame, text="Login", font=("Arial", 32))
login_label.pack(pady=(50, 30))

# Username field
username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Username or Email", corner_radius=0, width=300)
username_entry.pack(pady=15)

# Password field
password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=300)
password_entry.pack(pady=15)

# Login button
login_button = customtkinter.CTkButton(login_frame, text="Login", corner_radius=0, command=lambda: print("Login clicked"))
login_button.pack(pady=30)

# Register button
register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: show_register_page(app))
register_button.pack(pady=10)

# Function to show login page
def show_login_page(app):
    login_frame.grid(row=0, column=1, sticky="nsew")
