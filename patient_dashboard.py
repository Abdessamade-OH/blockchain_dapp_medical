import customtkinter as ctk
import tkinter as tk
from PIL import Image
import datetime

class PatientDashboard:
    def __init__(self, root, patient_info):
        self.root = root
        self.patient_info = patient_info
        
        # Create main dashboard frame
        self.dashboard_frame = ctk.CTkFrame(self.root)
        self.dashboard_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(self.dashboard_frame, height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        welcome_label = ctk.CTkLabel(
            header_frame, 
            text=f"Welcome, {patient_info['name']}",
            font=("Arial Bold", 24)
        )
        welcome_label.pack(side="left", padx=20, pady=10)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            header_frame, 
            text="Logout", 
            command=self.logout,
            width=100
        )
        logout_btn.pack(side="right", padx=20, pady=10)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.dashboard_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tabs
        tab_view = ctk.CTkTabview(content_frame)
        tab_view.pack(fill="both", expand=True)
        
        # Personal Info Tab
        personal_info_tab = tab_view.add("Personal Info")
        self.create_personal_info_section(personal_info_tab)
        
        # Medical Records Tab
        medical_records_tab = tab_view.add("Medical Records")
        self.create_medical_records_section(medical_records_tab)
        
        # Access Management Tab
        access_tab = tab_view.add("Access Management")
        self.create_access_management_section(access_tab)
    
    def create_personal_info_section(self, parent):
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Updated to match contract's Patient struct fields exactly
        info_labels = [
            ("Wallet Address", self.patient_info.get('walletAddress', 'N/A')),
            ("Name", self.patient_info.get('name', 'N/A')),
            ("Date of Birth", self.patient_info.get('dateOfBirth', 'N/A')),
            ("Gender", self.patient_info.get('gender', 'N/A')),
            ("Blood Group", self.patient_info.get('bloodGroup', 'N/A')),
            ("Home Address", self.patient_info.get('homeAddress', 'N/A')),
            ("Email", self.patient_info.get('email', 'N/A')),
            ("Health Number", self.patient_info.get('hhNumber', 'N/A'))
        ]
        
        for label, value in info_labels:
            row_frame = ctk.CTkFrame(info_frame)
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row_frame, text=label + ":", width=150, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=value, width=250, anchor="w").pack(side="left")
    
    def create_medical_records_section(self, parent):
        records_frame = ctk.CTkFrame(parent)
        records_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Table headers
        headers_frame = ctk.CTkFrame(records_frame)
        headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Record ID", "IPFS Hash", "Timestamp", "Doctor"]
        for header in headers:
            ctk.CTkLabel(headers_frame, text=header, width=150).pack(side="left", padx=5)
        
        # Records list (scrollable)
        records_list = ctk.CTkScrollableFrame(records_frame)
        records_list.pack(fill="both", expand=True)
        
        # Placeholder text when no records
        if not hasattr(self, 'medical_records') or not self.medical_records:
            no_records_label = ctk.CTkLabel(
                records_list, 
                text="No medical records available",
                font=("Arial", 16)
            )
            no_records_label.pack(expand=True)
    
    def create_access_management_section(self, parent):
        access_frame = ctk.CTkFrame(parent)
        access_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Doctor Access Management
        access_control_frame = ctk.CTkFrame(access_frame)
        access_control_frame.pack(fill="x", pady=10)
        
        doctor_hh_entry = ctk.CTkEntry(
            access_control_frame, 
            placeholder_text="Doctor Health Number",
            width=250
        )
        doctor_hh_entry.pack(side="left", padx=10)
        
        grant_access_btn = ctk.CTkButton(
            access_control_frame, 
            text="Grant Access",
            command=lambda: self.grant_doctor_access(doctor_hh_entry.get())
        )
        grant_access_btn.pack(side="left", padx=5)
        
        revoke_access_btn = ctk.CTkButton(
            access_control_frame, 
            text="Revoke Access",
            command=lambda: self.revoke_doctor_access(doctor_hh_entry.get())
        )
        revoke_access_btn.pack(side="left")
        
        # Access List
        access_list_frame = ctk.CTkScrollableFrame(access_frame)
        access_list_frame.pack(fill="both", expand=True, pady=10)
        
        # Placeholder for access list
        ctk.CTkLabel(
            access_list_frame, 
            text="Authorized Doctors:\nNo doctors currently have access",
            font=("Arial", 14)
        ).pack(pady=10)
    
    def grant_doctor_access(self, doctor_hh):
        if doctor_hh:
            # This would interact with the smart contract's grantAccess function
            self.show_message("Access Granted", f"Access granted to doctor with Health Number: {doctor_hh}")
        else:
            self.show_message("Error", "Please enter a Doctor Health Number")
    
    def revoke_doctor_access(self, doctor_hh):
        if doctor_hh:
            # This would interact with the smart contract's revokeAccess function
            self.show_message("Access Revoked", f"Access revoked for doctor with Health Number: {doctor_hh}")
        else:
            self.show_message("Error", "Please enter a Doctor Health Number")
    
    def logout(self):
        self.dashboard_frame.destroy()
        self.root.show_landing_page()
    
    def show_message(self, title, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title=title
        )

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("900x600")
        # Updated patient info structure to match contract exactly
        self.patient_info = {
            "walletAddress": "0x123...",
            "name": "John Doe",
            "dateOfBirth": "1980-01-01",
            "gender": "Male",
            "bloodGroup": "O+",
            "homeAddress": "123 Main St, City",
            "email": "johndoe@example.com",
            "hhNumber": "HH123456"
        }
        self.dashboard = PatientDashboard(self.root, self.patient_info)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()