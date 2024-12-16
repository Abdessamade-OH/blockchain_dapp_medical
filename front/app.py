import customtkinter
from PIL import Image, ImageTk
from login import show_login_page  # Import login page function from login.py
from register_patient import show_register_patient_page  # Import patient registration page
from register_doctor import show_register_doctor_page  # Import doctor registration page

# Set custom tkinter appearance and theme
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("green")

# Initialize the app
app = customtkinter.CTk()
app.geometry("900x600")
app.resizable(False, False)

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
def register_patient_page():
    # Clear current login frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Call show_register_patient_page from register_patient.py
    show_register_patient_page(login_frame, show_login_page_success)

def register_doctor_page():
    # Clear current login frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Call show_register_doctor_page from register_doctor.py
    show_register_doctor_page(login_frame, show_login_page_success)

# Function to show login page
def show_login_page_success():
    # Clear current frame
    for widget in login_frame.winfo_children():
        widget.destroy()

    # Call show_login_page from login.py to show the login form
    show_login_page(login_frame, register_patient_page)

# Initial load of the login page
show_login_page_success()

# Run the app
app.mainloop()
