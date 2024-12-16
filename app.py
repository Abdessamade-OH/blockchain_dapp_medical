import customtkinter
from PIL import Image, ImageTk

# Set custom tkinter appearance and theme
customtkinter.set_appearance_mode("light")  # Light mode for a pastel theme
customtkinter.set_default_color_theme("green")  # Choose a softer color theme

# Initialize the app
app = customtkinter.CTk()  # Create CTk window
app.geometry("800x600")  # Fixed window size
app.resizable(False, False)  # Disable resizing/zooming

# Set the background color to a pastel shade
app.configure(bg="#EAF6F6")  # A light pastel green-blue color

# Left-side image frame
image_frame = customtkinter.CTkFrame(app, width=400, height=600, fg_color="#EAF6F6")
image_frame.grid(row=0, column=0, sticky="nsew")

# Open and scale the image proportionally to fit
image = Image.open("assets/login_img.jpg")  # Replace with the path to your image
image_ratio = image.width / image.height
frame_width, frame_height = 400, 600

if frame_width / frame_height > image_ratio:
    # Fit by height
    new_width = int(frame_height * image_ratio)
    new_height = frame_height
else:
    # Fit by width
    new_width = frame_width
    new_height = int(frame_width / image_ratio)

image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
image_tk = ImageTk.PhotoImage(image)

# Place the image in the frame
image_label = customtkinter.CTkLabel(image_frame, image=image_tk, text="")
image_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the image

# Right-side login form frame
login_frame = customtkinter.CTkFrame(app, fg_color="#EAF6F6", corner_radius=0, width=400, height=600)
login_frame.grid(row=0, column=1, sticky="nsew")

# Login label
login_label = customtkinter.CTkLabel(login_frame, text="Login", font=("Arial", 24), bg_color="#EAF6F6")
login_label.pack(pady=(40, 20))

# Username entry field
username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Username or Email", corner_radius=0, width=250)
username_entry.pack(pady=10)

# Password entry field
password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", corner_radius=0, width=250)
password_entry.pack(pady=10)

# Login button
login_button = customtkinter.CTkButton(login_frame, text="Login", corner_radius=0, command=lambda: print("Login clicked"))
login_button.pack(pady=20)

# Register button
register_button = customtkinter.CTkButton(login_frame, text="Register", corner_radius=0, command=lambda: print("Register clicked"))
register_button.pack(pady=10)

# Adjust grid weights (to split the screen into two equal halves)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

app.mainloop()
