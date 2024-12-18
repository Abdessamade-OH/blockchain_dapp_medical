import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import datetime
from web3 import Web3
import json
import os

# Additional imports for file handling and encryption
from cryptography.fernet import Fernet
import pinata

class DoctorDashboard:
    def __init__(self, root, doctor_info):
        self.root = root
        self.doctor_info = doctor_info
        
        # IPFS and encryption setup
        self.pinata_api_key = 'YOUR_PINATA_API_KEY'
        self.pinata_secret_api_key = 'YOUR_PINATA_SECRET_API_KEY'
        self.pinata_client = pinata.Pinata(self.pinata_api_key, self.pinata_secret_api_key)
        
        # Create main dashboard frame
        self.dashboard_frame = ctk.CTkFrame(self.root)
        self.dashboard_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(self.dashboard_frame, height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        welcome_label = ctk.CTkLabel(
            header_frame, 
            text=f"Welcome, Dr. {doctor_info['name']}",
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
        
        # Patient Access Tab
        patient_access_tab = tab_view.add("Patient Access")
        self.create_patient_access_section(patient_access_tab)
        
        # Medical Records Tab
        medical_records_tab = tab_view.add("Medical Records")
        self.create_medical_records_section(medical_records_tab)
        
        # Audit Logs Tab
        audit_log_tab = tab_view.add("Audit Logs")
        self.create_audit_log_section(audit_log_tab)

    def create_personal_info_section(self, parent):
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Match exactly with the Doctor struct fields from the smart contract
        info_labels = [
            ("Wallet Address", self.doctor_info.get('walletAddress', 'N/A')),
            ("Name", self.doctor_info.get('name', 'N/A')),
            ("Specialization", self.doctor_info.get('specialization', 'N/A')),
            ("Hospital Name", self.doctor_info.get('hospitalName', 'N/A')),
            ("Health Number", self.doctor_info.get('hhNumber', 'N/A'))
        ]
        
        for label, value in info_labels:
            row_frame = ctk.CTkFrame(info_frame)
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row_frame, text=label + ":", width=150, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=value, width=250, anchor="w").pack(side="left")
    
    def create_patient_access_section(self, parent):
        access_frame = ctk.CTkFrame(parent)
        access_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Check Access Frame
        check_access_frame = ctk.CTkFrame(access_frame)
        check_access_frame.pack(fill="x", pady=10)
        
        patient_hh_entry = ctk.CTkEntry(
            check_access_frame,
            placeholder_text="Patient HH Number",
            width=300
        )
        patient_hh_entry.pack(side="left", padx=10)
        
        check_access_btn = ctk.CTkButton(
            check_access_frame,
            text="Check Access",
            command=lambda: self.check_patient_access(
                patient_hh_entry.get(),
                self.doctor_info['hhNumber']
            )
        )
        check_access_btn.pack(side="left", padx=10)
        
        # Access Status
        self.access_status_label = ctk.CTkLabel(
            access_frame,
            text="Access status will appear here",
            font=("Arial", 14)
        )
        self.access_status_label.pack(pady=10)
    
    def create_medical_records_section(self, parent):
        records_frame = ctk.CTkFrame(parent)
        records_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Patient HH Number Entry
        hh_frame = ctk.CTkFrame(records_frame)
        hh_frame.pack(fill="x", pady=10)
        
        self.record_patient_hh_entry = ctk.CTkEntry(
            hh_frame,
            placeholder_text="Patient HH Number",
            width=300
        )
        self.record_patient_hh_entry.pack(side="left", padx=10)
        
        # File Selection
        file_frame = ctk.CTkFrame(records_frame)
        file_frame.pack(fill="x", pady=10)
        
        self.selected_file_label = ctk.CTkLabel(
            file_frame, 
            text="No file selected", 
            width=300
        )
        self.selected_file_label.pack(side="left", padx=10)
        
        select_file_btn = ctk.CTkButton(
            file_frame,
            text="Select Medical Record File",
            command=self.select_medical_record_file
        )
        select_file_btn.pack(side="left", padx=10)
        
        # Create Button
        create_btn = ctk.CTkButton(
            records_frame,
            text="Create Medical Record",
            command=self.create_medical_record
        )
        create_btn.pack(pady=10)
    
    def select_medical_record_file(self):
        # Support multiple file types
        file_types = [
            ('PDF files', '*.pdf'),
            ('Image files', '*.jpg;*.jpeg;*.png'),
            ('Text files', '*.txt'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Medical Record File",
            filetypes=file_types
        )
        
        if filename:
            self.selected_file = filename
            self.selected_file_label.configure(
                text=os.path.basename(filename)
            )
    
    def create_medical_record(self):
        try:
            # Validate inputs
            patient_hh = self.record_patient_hh_entry.get()
            if not patient_hh:
                self.show_message("Error", "Please enter patient HH number")
                return
            
            if not hasattr(self, 'selected_file'):
                self.show_message("Error", "Please select a file")
                return
            
            # Generate symmetric key
            symmetric_key = Fernet.generate_key()
            fernet = Fernet(symmetric_key)
            
            # Read and encrypt file
            with open(self.selected_file, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = fernet.encrypt(file_data)
            
            # Upload encrypted file to IPFS
            with open('temp_encrypted_file', 'wb') as temp_file:
                temp_file.write(encrypted_data)
            
            ipfs_response = self.pinata_client.pin_file('temp_encrypted_file')
            ipfs_hash = ipfs_response['IpfsHash']
            
            # Cleanup temporary file
            os.remove('temp_encrypted_file')
            
            # Encrypt symmetric key (for future: use doctor's public key)
            encrypted_symmetric_key = symmetric_key.decode('utf-8')
            
            # Create medical record on blockchain
            tx = self.doctor_contract.functions.createMedicalRecord(
                patient_hh,
                ipfs_hash,
                encrypted_symmetric_key,
                self.doctor_info['hhNumber']
            ).build_transaction({
                'from': self.doctor_info['walletAddress'],
                'nonce': self.w3.eth.get_transaction_count(self.doctor_info['walletAddress'])
            })
            
            # You'll need to implement transaction signing and sending here
            
            # Log audit
            self.log_audit(patient_hh, 0, f"Created medical record: {os.path.basename(self.selected_file)}")
            
            # Clear file selection
            self.selected_file_label.configure(text="No file selected")
            del self.selected_file
            
            self.show_message("Success", "Medical record created successfully")
        
        except Exception as e:
            self.show_message("Error", str(e))
    
    def create_audit_log_section(self, parent):
        audit_frame = ctk.CTkFrame(parent)
        audit_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Entity ID Search
        search_frame = ctk.CTkFrame(audit_frame)
        search_frame.pack(fill="x", pady=10)
        
        entity_id_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Entity HH Number",
            width=300
        )
        entity_id_entry.pack(side="left", padx=10)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Get Audit Logs",
            command=lambda: self.get_audit_logs(entity_id_entry.get())
        )
        search_btn.pack(side="left", padx=10)
        
        # Audit Log Display
        self.audit_display = ctk.CTkTextbox(audit_frame, height=400)
        self.audit_display.pack(fill="both", expand=True, pady=10)
    
    def check_patient_access(self, patient_hh, doctor_hh):
        try:
            has_access = self.patient_contract.functions.checkAccess(
                patient_hh,
                doctor_hh
            ).call()
            
            status = "Access Granted" if has_access else "No Access"
            self.access_status_label.configure(
                text=f"Status: {status}",
                text_color="green" if has_access else "red"
            )
        except Exception as e:
            self.show_message("Error", str(e))
    
    def create_medical_record(self):
        try:
            patient_hh = self.record_patient_hh_entry.get()
            ipfs_hash = self.ipfs_hash_entry.get()
            encrypted_key = self.encrypted_key_entry.get()
            
            tx = self.doctor_contract.functions.createMedicalRecord(
                patient_hh,
                ipfs_hash,
                encrypted_key,
                self.doctor_info['hhNumber']
            ).build_transaction({
                'from': self.doctor_info['walletAddress'],
                'nonce': self.w3.eth.get_transaction_count(self.doctor_info['walletAddress'])
            })
            
            # You'll need to implement transaction signing and sending here
            
            # Log audit
            self.log_audit(patient_hh, 0, "Created medical record")  # 0 = CREATE_RECORD
            
            self.show_message("Success", "Medical record created successfully")
        except Exception as e:
            self.show_message("Error", str(e))
    
    def update_medical_record(self):
        try:
            patient_hh = self.record_patient_hh_entry.get()
            ipfs_hash = self.ipfs_hash_entry.get()
            encrypted_key = self.encrypted_key_entry.get()
            record_id = 0  # You'll need to implement record ID selection
            
            tx = self.doctor_contract.functions.updateMedicalRecord(
                patient_hh,
                record_id,
                ipfs_hash,
                encrypted_key,
                self.doctor_info['hhNumber']
            ).build_transaction({
                'from': self.doctor_info['walletAddress'],
                'nonce': self.w3.eth.get_transaction_count(self.doctor_info['walletAddress'])
            })
            
            # You'll need to implement transaction signing and sending here
            
            # Log audit
            self.log_audit(patient_hh, 1, "Updated medical record")  # 1 = UPDATE_RECORD
            
            self.show_message("Success", "Medical record updated successfully")
        except Exception as e:
            self.show_message("Error", str(e))
    
    def get_audit_logs(self, entity_id):
        try:
            logs = self.audit_contract.functions.getAuditLogsForEntity(entity_id).call()
            
            self.audit_display.delete("1.0", tk.END)
            for log in logs:
                action_types = ["CREATE", "UPDATE", "VIEW", "GRANT", "REVOKE"]
                action = action_types[log[1]] if log[1] < len(action_types) else "UNKNOWN"
                
                log_entry = f"Entity: {log[0]}\n"
                log_entry += f"Action: {action}\n"
                log_entry += f"Performer: {log[2]}\n"
                log_entry += f"Timestamp: {datetime.datetime.fromtimestamp(log[3])}\n"
                log_entry += f"Details: {log[4]}\n"
                log_entry += "-" * 50 + "\n"
                
                self.audit_display.insert(tk.END, log_entry)
        except Exception as e:
            self.show_message("Error", str(e))
    
    def log_audit(self, entity_id, action_type, details):
        try:
            tx = self.audit_contract.functions.logAudit(
                entity_id,
                action_type,
                details
            ).build_transaction({
                'from': self.doctor_info['walletAddress'],
                'nonce': self.w3.eth.get_transaction_count(self.doctor_info['walletAddress'])
            })
            
            # You'll need to implement transaction signing and sending here
        except Exception as e:
            self.show_message("Error", str(e))
    
    def logout(self):
        self.dashboard_frame.destroy()
        self.root.show_landing_page()
    
    def show_message(self, title, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title=title
        )

def main():
    root = ctk.CTk()
    root.geometry("900x600")
    root.title("Doctor Dashboard")
    
    # Example doctor info - you'll need to get this from your authentication system
    doctor_info = {
        "name": "John Doe",
        "specialization": "Cardiology",
        "hospitalName": "City Hospital",
        "hhNumber": "DOC123",
        "walletAddress": "0x..."
    }
    
    dashboard = DoctorDashboard(root, doctor_info)
    root.mainloop()

if __name__ == "__main__":
    main()