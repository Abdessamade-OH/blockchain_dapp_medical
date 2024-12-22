# app.py
import customtkinter
from auth import show_auth_page

def main():
    app = customtkinter.CTk()

    # Set fixed window size
    app.geometry("900x680")
    app.resizable(True, False)

    # Initialize the application with the auth screen
    show_auth_page(app)

    app.mainloop()

if __name__ == "__main__":
    main()
