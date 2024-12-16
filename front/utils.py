import customtkinter

def validate_input(data, form_type):
    errors = []
    
    if form_type == 'patient':
        if not data.get("name"):
            errors.append("Name is required.")
        if not data.get("hh_number"):
            errors.append("HH Number is required.")
        if not data.get("password"):
            errors.append("Password is required.")
    
    elif form_type == 'doctor':
        if not data.get("wallet_address"):
            errors.append("Wallet Address is required.")
        if not data.get("name"):
            errors.append("Name is required.")
        if not data.get("specialization"):
            errors.append("Specialization is required.")
        if not data.get("hospital_name"):
            errors.append("Hospital Name is required.")
        if not data.get("hh_number"):
            errors.append("HH Number is required.")
        if not data.get("password"):
            errors.append("Password is required.")
    
    return errors

def show_message(frame, message, color):
    msg_label = customtkinter.CTkLabel(frame, text=message, text_color=color, bg_color="#EAF6F6")
    msg_label.pack(pady=5)
