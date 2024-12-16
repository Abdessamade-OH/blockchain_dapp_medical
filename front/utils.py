import customtkinter

# Function to validate user input
def validate_input(data):
    errors = []
    for key, value in data.items():
        if not value.strip():
            errors.append(f"{key.capitalize()} is required.")
    return errors

# Function to show messages (success or error)
def show_message(frame, message, color):
    message_label = customtkinter.CTkLabel(frame, text=message, text_color=color, bg_color="#EAF6F6")
    message_label.pack(pady=5)
