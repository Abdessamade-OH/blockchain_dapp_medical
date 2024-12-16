import customtkinter as ctk
import tkinter as tk
from PIL import Image
from web3 import Web3
import json
import os

# Update the Web3 connection to use Ganache's default port
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Ganache default port

# Add a check to verify connection
if not w3.is_connected():
    raise Exception("Failed to connect to Ganache")

class HealthcareApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Healthcare Blockchain System")
        self.root.geometry("1000x600")
        
        # Set the color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Initialize all frames but only show landing page
        self.landing_frame = None
        self.patient_login_frame = None
        self.doctor_login_frame = None
        self.patient_register_frame = None
        self.doctor_register_frame = None
        
        self.create_landing_page()
        
    def create_landing_page(self):
        if self.landing_frame:
            self.landing_frame.destroy()
            
        self.landing_frame = ctk.CTkFrame(self.main_frame)
        self.landing_frame.pack(fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(
            self.landing_frame, 
            text="Healthcare Blockchain System",
            font=("Arial Bold", 32)
        )
        title.pack(pady=40)
        
        # Buttons container
        buttons_frame = ctk.CTkFrame(self.landing_frame)
        buttons_frame.pack(pady=20)
        
        # Patient Section
        patient_label = ctk.CTkLabel(
            buttons_frame,
            text="Patients",
            font=("Arial Bold", 24)
        )
        patient_label.pack(pady=10)
        
        patient_login_btn = ctk.CTkButton(
            buttons_frame,
            text="Patient Login",
            command=self.show_patient_login,
            width=200,
            height=40
        )
        patient_login_btn.pack(pady=10)
        
        patient_register_btn = ctk.CTkButton(
            buttons_frame,
            text="Patient Registration",
            command=self.show_patient_register,
            width=200,
            height=40
        )
        patient_register_btn.pack(pady=10)
        
        # Separator
        separator = ctk.CTkFrame(buttons_frame, width=200, height=2)
        separator.pack(pady=20)
        
        # Doctor Section
        doctor_label = ctk.CTkLabel(
            buttons_frame,
            text="Healthcare Professionals",
            font=("Arial Bold", 24)
        )
        doctor_label.pack(pady=10)
        
        doctor_login_btn = ctk.CTkButton(
            buttons_frame,
            text="Doctor Login",
            command=self.show_doctor_login,
            width=200,
            height=40
        )
        doctor_login_btn.pack(pady=10)
        
        doctor_register_btn = ctk.CTkButton(
            buttons_frame,
            text="Doctor Registration",
            command=self.show_doctor_register,
            width=200,
            height=40
        )
        doctor_register_btn.pack(pady=10)
    
    def create_patient_login(self):
        if self.patient_login_frame:
            self.patient_login_frame.destroy()
            
        self.patient_login_frame = ctk.CTkFrame(self.main_frame)
        self.patient_login_frame.pack(fill="both", expand=True)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.patient_login_frame,
            text="← Back",
            command=self.show_landing_page,
            width=100
        )
        back_btn.pack(anchor="nw", padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.patient_login_frame,
            text="Patient Login",
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        # Login form
        form_frame = ctk.CTkFrame(self.patient_login_frame)
        form_frame.pack(pady=20)
        
        hh_number = ctk.CTkEntry(
            form_frame,
            placeholder_text="Health Number",
            width=300
        )
        hh_number.pack(pady=10)
        
        password = ctk.CTkEntry(
            form_frame,
            placeholder_text="Password",
            show="*",
            width=300
        )
        password.pack(pady=10)
        
        connect_wallet_btn = ctk.CTkButton(
            form_frame,
            text="Connect MetaMask",
            command=self.connect_metamask,
            width=300
        )
        connect_wallet_btn.pack(pady=10)
        
        login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=lambda: self.login_patient(hh_number.get(), password.get()),
            width=300
        )
        login_btn.pack(pady=10)
    
    def create_doctor_login(self):
        if self.doctor_login_frame:
            self.doctor_login_frame.destroy()
            
        self.doctor_login_frame = ctk.CTkFrame(self.main_frame)
        self.doctor_login_frame.pack(fill="both", expand=True)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.doctor_login_frame,
            text="← Back",
            command=self.show_landing_page,
            width=100
        )
        back_btn.pack(anchor="nw", padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.doctor_login_frame,
            text="Healthcare Professional Login",
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        # Login form
        form_frame = ctk.CTkFrame(self.doctor_login_frame)
        form_frame.pack(pady=20)
        
        hh_number = ctk.CTkEntry(
            form_frame,
            placeholder_text="Professional ID",
            width=300
        )
        hh_number.pack(pady=10)
        
        password = ctk.CTkEntry(
            form_frame,
            placeholder_text="Password",
            show="*",
            width=300
        )
        password.pack(pady=10)
        
        connect_wallet_btn = ctk.CTkButton(
            form_frame,
            text="Connect MetaMask",
            command=self.connect_metamask,
            width=300
        )
        connect_wallet_btn.pack(pady=10)
        
        login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=lambda: self.login_doctor(hh_number.get(), password.get()),
            width=300
        )
        login_btn.pack(pady=10)
    
    def create_patient_register(self):
        if self.patient_register_frame:
            self.patient_register_frame.destroy()
            
        self.patient_register_frame = ctk.CTkFrame(self.main_frame)
        self.patient_register_frame.pack(fill="both", expand=True)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.patient_register_frame,
            text="← Back",
            command=self.show_landing_page,
            width=100
        )
        back_btn.pack(anchor="nw", padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.patient_register_frame,
            text="Patient Registration",
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        # Registration form
        form_frame = ctk.CTkFrame(self.patient_register_frame)
        form_frame.pack(pady=20)
        
        # Create a canvas with scrollbar for the form
        canvas = ctk.CTkCanvas(form_frame, width=400, height=400)
        scrollbar = ctk.CTkScrollbar(form_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        fields = [
            ("name", "Full Name"),
            ("dob", "Date of Birth (DD/MM/YYYY)"),
            ("gender", "Gender"),
            ("blood_group", "Blood Group"),
            ("address", "Home Address"),
            ("email", "Email"),
            ("hh_number", "Health Number"),
            ("password", "Password"),
            ("confirm_password", "Confirm Password")
        ]
        
        entries = {}
        for field, placeholder in fields:
            entry = ctk.CTkEntry(
                scrollable_frame,
                placeholder_text=placeholder,
                width=300
            )
            entry.pack(pady=10)
            entries[field] = entry
            
            if field in ["password", "confirm_password"]:
                entry.configure(show="*")
        
        connect_wallet_btn = ctk.CTkButton(
            scrollable_frame,
            text="Connect MetaMask",
            command=self.connect_metamask,
            width=300
        )
        connect_wallet_btn.pack(pady=10)
        
        register_btn = ctk.CTkButton(
            scrollable_frame,
            text="Register",
            command=lambda: self.register_patient(entries),
            width=300
        )
        register_btn.pack(pady=10)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_doctor_register(self):
        if self.doctor_register_frame:
            self.doctor_register_frame.destroy()
            
        self.doctor_register_frame = ctk.CTkFrame(self.main_frame)
        self.doctor_register_frame.pack(fill="both", expand=True)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.doctor_register_frame,
            text="← Back",
            command=self.show_landing_page,
            width=100
        )
        back_btn.pack(anchor="nw", padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.doctor_register_frame,
            text="Healthcare Professional Registration",
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        # Registration form
        form_frame = ctk.CTkFrame(self.doctor_register_frame)
        form_frame.pack(pady=20)
        
        fields = [
            ("name", "Full Name"),
            ("specialization", "Specialization"),
            ("hospital", "Hospital Name"),
            ("hh_number", "Professional ID"),
            ("password", "Password"),
            ("confirm_password", "Confirm Password")
        ]
        
        entries = {}
        for field, placeholder in fields:
            entry = ctk.CTkEntry(
                form_frame,
                placeholder_text=placeholder,
                width=300
            )
            entry.pack(pady=10)
            entries[field] = entry
            
            if field in ["password", "confirm_password"]:
                entry.configure(show="*")
        
        connect_wallet_btn = ctk.CTkButton(
            form_frame,
            text="Connect MetaMask",
            command=self.connect_metamask,
            width=300
        )
        connect_wallet_btn.pack(pady=10)
        
        register_btn = ctk.CTkButton(
            form_frame,
            text="Register",
            command=lambda: self.register_doctor(entries),
            width=300
        )
        register_btn.pack(pady=10)
    
    # Navigation methods
    def show_landing_page(self):
        self.clear_frames()
        self.create_landing_page()
    
    def show_patient_login(self):
        self.clear_frames()
        self.create_patient_login()
    
    def show_doctor_login(self):
        self.clear_frames()
        self.create_doctor_login()
    
    def show_patient_register(self):
        self.clear_frames()
        self.create_patient_register()
    
    def show_doctor_register(self):
        self.clear_frames()
        self.create_doctor_register()
    
    def clear_frames(self):
        frames = [
            self.landing_frame,
            self.patient_login_frame,
            self.doctor_login_frame,
            self.patient_register_frame,
            self.doctor_register_frame
        ]
        
        for frame in frames:
            if frame:
                frame.pack_forget()
    
    # Blockchain interaction methods
    def connect_metamask(self):
        try:
            # First verify Web3 connection
            if not w3.is_connected():
                self.show_message("Error", "Cannot connect to Ganache. Please check if Ganache is running.")
                return

            # Get accounts
            accounts = w3.eth.accounts
            if not accounts:
                self.show_message("Error", "No accounts found. Please ensure MetaMask is connected to Ganache")
                return
                
            self.current_account = accounts[0]
            
            # Verify account has proper checksum
            self.current_account = Web3.to_checksum_address(self.current_account)
            
            # Test connection by getting balance
            balance = w3.eth.get_balance(self.current_account)
            
            self.show_message("Success", f"MetaMask connected successfully!\nAccount: {self.current_account}\nBalance: {w3.from_wei(balance, 'ether')} ETH")
            
        except Exception as e:
            self.show_message("Error", f"Failed to connect to MetaMask: {str(e)}\nPlease ensure Ganache is running and the account is imported to MetaMask")

    def load_contract(self, contract_name, contract_address):
        try:
            # Load ABI from JSON file
            contract_path = os.path.join("contracts", f"{contract_name}.json")
            with open(contract_path, 'r') as file:
                contract_json = json.load(file)
                contract_abi = contract_json['abi']
                
            # Create contract instance
            contract_address = Web3.to_checksum_address(contract_address)
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            return contract
        except Exception as e:
            self.show_message("Error", f"Failed to load contract {contract_name}: {str(e)}")
            return None
    
    def login_patient(self, hh_number, password):
        try:
            # Verify input is not empty
            if not hh_number or not password:
                self.show_message("Error", "Please enter both Health Number and Password")
                return

            # Connect to the ContractPatient 
            contract_address = "0x00ceb1B885668C4471f0DEd975D390BaB74f2861"  # Replace with actual deployed address
            abi = json.loads('[YOUR_CONTRACT_ABI]')  # Replace with actual ABI from Remix

            contract = w3.eth.contract(address=contract_address, abi=abi)

            # Hash the password to compare with stored hash
            password_hash = w3.keccak(text=password)

            try:
                # Check if patient is registered and password matches
                patient = contract.functions.patients(hh_number).call()
                
                if patient[0] != "0x0000000000000000000000000000000000000000":  # Check if patient exists
                    stored_hash = patient[8]  # Assuming passwordHash is at index 8
                    
                    if stored_hash == password_hash:
                        # Verify wallet connection
                        if not hasattr(self, 'current_account') or not self.current_account:
                            self.show_message("Error", "Please connect MetaMask first")
                            return
                        
                        # Verify wallet matches registered address
                        if self.current_account.lower() != patient[0].lower():
                            self.show_message("Error", "Connected wallet does not match registered account")
                            return
                        
                        # Successful login 
                        self.show_message("Success", f"Welcome, {patient[1]}!")
                        # TODO: Navigate to patient dashboard
                    else:
                        self.show_message("Error", "Incorrect password")
                else:
                    self.show_message("Error", "Patient not registered")
            
            except Exception as contract_error:
                self.show_message("Error", f"Login error: {str(contract_error)}")

        except Exception as e:
            self.show_message("Error", f"Unexpected error: {str(e)}")
    
    def login_doctor(self, hh_number, password):
        try:
            # Verify input is not empty
            if not hh_number or not password:
                self.show_message("Error", "Please enter both Professional ID and Password")
                return

            # Connect to the ContractDoctor
            contract_address = "0x372fF41fEbFc04BE4687565268C8aBE9A4886d6e"  # Replace with actual deployed address
            # Replace [YOUR_CONTRACT_ABI] with the actual ABI JSON
            abi = json.loads('[YOUR_CONTRACT_ABI]')  # Replace with actual ABI from Remix

            contract = w3.eth.contract(address=contract_address, abi=abi)

            # Hash the password to compare with stored hash
            password_hash = w3.keccak(text=password)

            try:
                # Check if doctor is registered and password matches
                doctor = contract.functions.doctors(hh_number).call()
                
                if doctor[0] != "0x0000000000000000000000000000000000000000":  # Check if doctor exists
                    stored_hash = doctor[5]  # Assuming passwordHash is at index 5
                    
                    if stored_hash == password_hash:
                        # Verify wallet connection
                        if not hasattr(self, 'current_account') or not self.current_account:
                            self.show_message("Error", "Please connect MetaMask first")
                            return
                        
                        # Verify wallet matches registered address
                        if self.current_account.lower() != doctor[0].lower():
                            self.show_message("Error", "Connected wallet does not match registered account")
                            return
                        
                        # Successful login 
                        self.show_message("Success", f"Welcome, Dr. {doctor[1]}!")
                        # TODO: Navigate to doctor dashboard
                    else:
                        self.show_message("Error", "Incorrect password")
                else:
                    self.show_message("Error", "Doctor not registered")
            
            except Exception as contract_error:
                self.show_message("Error", f"Login error: {str(contract_error)}")

        except Exception as e:
            self.show_message("Error", f"Unexpected error: {str(e)}")
    
    def register_patient(self, entries):
        try:
            # Validate inputs
            for key, entry in entries.items():
                if not entry.get():
                    self.show_message("Error", f"Please fill in {key}")
                    return
            
            # Check password match
            if entries['password'].get() != entries['confirm_password'].get():
                self.show_message("Error", "Passwords do not match")
                return
            
            # Verify MetaMask connection
            if not hasattr(self, 'current_account') or not self.current_account:
                self.show_message("Error", "Please connect MetaMask first")
                return
            
            # Connect to the ContractPatient
            contract_address = "0x00ceb1B885668C4471f0DEd975D390BaB74f2861"  # Replace with actual deployed address
            abi = json.loads('[YOUR_CONTRACT_ABI]')  # Replace with actual ABI from Remix
            contract = w3.eth.contract(address=contract_address, abi=abi)
            
            # Prepare transaction
            transaction = contract.functions.registerPatient(
                entries['name'].get(),
                entries['dob'].get(),
                entries['gender'].get(),
                entries['blood_group'].get(),
                entries['address'].get(),
                entries['email'].get(),
                entries['hh_number'].get(),
                entries['password'].get()
            )
            
            # Estimate gas
            gas_estimate = transaction.estimate_gas()
            
            # Send transaction
            tx_hash = transaction.transact({
                'from': self.current_account,
                'gas': gas_estimate
            })
            
            # Wait for transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt['status'] == 1:
                self.show_message("Success", "Patient registered successfully!")
                # TODO: Navigate to patient dashboard
            else:
                self.show_message("Error", "Registration failed")
        
        except Exception as e:
            self.show_message("Error", f"Registration error: {str(e)}")

    def register_doctor(self, entries):
        try:
            # Validate inputs
            for key, entry in entries.items():
                if not entry.get():
                    self.show_message("Error", f"Please fill in {key}")
                    return
            
            # Check password match
            if entries['password'].get() != entries['confirm_password'].get():
                self.show_message("Error", "Passwords do not match")
                return
            
            # Verify MetaMask connection
            if not hasattr(self, 'current_account') or not self.current_account:
                self.show_message("Error", "Please connect MetaMask first")
                return
            
            # Connect to the ContractDoctor
            contract_address = "0x372fF41fEbFc04BE4687565268C8aBE9A4886d6e"  # Replace with actual deployed address
            abi = json.loads('[YOUR_CONTRACT_ABI]')  # Replace with actual ABI from Remix
            contract = w3.eth.contract(address=contract_address, abi=abi)
            
            # Prepare transaction
            transaction = contract.functions.registerDoctor(
                entries['name'].get(),
                entries['specialization'].get(),
                entries['hospital'].get(),
                entries['hh_number'].get(),
                entries['password'].get()
            )
            
            # Estimate gas
            gas_estimate = transaction.estimate_gas()
            
            # Send transaction
            tx_hash = transaction.transact({
                'from': self.current_account,
                'gas': gas_estimate
            })
            
            # Wait for transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt['status'] == 1:
                self.show_message("Success", "Doctor registered successfully!")
                # TODO: Navigate to doctor dashboard
            else:
                self.show_message("Error", "Registration failed")
        
        except Exception as e:
            self.show_message("Error", f"Registration error: {str(e)}")
    
    def show_message(self, title, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title=title
        )
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HealthcareApp()
    app.run()