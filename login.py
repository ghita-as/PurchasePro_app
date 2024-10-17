import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import os
import subprocess

# Function to verify login details
def verify_login():
    email = entry_username.get()
    password = entry_password.get()
    
    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="app"
        )
        cursor = conn.cursor()
        
        # Query to check if the user exists and fetch their role
        query = "SELECT role, nom FROM users WHERE mail = %s AND mdp = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()

        if result:
            role, name = result
            messagebox.showinfo("Login Successful", f"Welcome {role.capitalize()}, {name}!")
            root.destroy()  # Close the login window

            # Launch corresponding script based on role
            if role == "admin":
                subprocess.call(['python', 'admin.py', name, role])
            elif role == "purchaser":
                subprocess.call(['python', 'purchaser.py', name, role])
            elif role == "demander":
                subprocess.call(['python', 'demander.py', name, role])

        else:
            messagebox.showwarning("Login Failed", "Invalid username or password!")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
            
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Create the main window
root = tk.Tk()
root.title("Elegant Login Page")
root.geometry("800x400")
root.configure(bg='#E9EAEC')  # White background

# Configure grid to make content resize properly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Frame for centering the content
content_frame = tk.Frame(root, bg='#E9EAEC')
content_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
content_frame.grid_rowconfigure(0, weight=1)
content_frame.grid_columnconfigure(0, weight=1)
content_frame.grid_columnconfigure(1, weight=1)

# Load and resize logo
try:
    logo_image = Image.open("logo1.png")  # Replace with your image path
    logo_image = logo_image.resize((250, 250), Image.LANCZOS)  # Resize the logo
    logo_photo = ImageTk.PhotoImage(logo_image)
except Exception as e:
    messagebox.showerror("Image Error", f"Failed to load logo: {e}")
    logo_photo = None

# Display the logo if it's successfully loaded
if logo_photo:
    logo_label = tk.Label(content_frame, image=logo_photo, bg='#E9EAEC')  # White background to blend with window
    logo_label.grid(row=0, column=0, padx=20, pady=20, sticky="e")

# Frame for the login form on the right
login_frame = tk.Frame(content_frame, bg='#E9EAEC')  # Transparent-like background by matching root's bg
login_frame.grid(row=0, column=1, padx=20, pady=20, sticky="w")

# Labels and Entry widgets
label_username = tk.Label(login_frame, text="Username", font=("Arial", 14), bg='#E9EAEC')
label_username.grid(row=0, column=0, padx=10, pady=10, sticky='e')

entry_username = tk.Entry(login_frame, font=("Arial", 14), bd=2, relief=tk.SOLID)
entry_username.grid(row=0, column=1, padx=10, pady=10)

label_password = tk.Label(login_frame, text="Password", font=("Arial", 14), bg='#E9EAEC')
label_password.grid(row=1, column=0, padx=10, pady=10, sticky='e')

entry_password = tk.Entry(login_frame, show='*', font=("Arial", 14), bd=2, relief=tk.SOLID)
entry_password.grid(row=1, column=1, padx=10, pady=10)

# Login Button
btn_login = tk.Button(login_frame, text="Login", font=("Arial", 14, "bold"), bg='#4CAF50', fg='white', bd=0, command=verify_login)
btn_login.grid(row=2, column=0, columnspan=2, pady=20)

# Make sure the root frame expands when resized
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the application
root.mainloop()
