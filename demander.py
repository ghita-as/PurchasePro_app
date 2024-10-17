# Importing necessary libraries
import sys
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
import os
import mysql.connector
from datetime import date

# Retrieve the passed user information (name and role)
name = sys.argv[1]
role = sys.argv[2]

# Global variable to hold the request number
request_number = None

# Function to handle logout
def logout():
    messagebox.showinfo("Logout", "You have been logged out.")
    root.destroy()  
    os.system('python login.py')

# Fonction pour lire le dernier numéro de demande à partir de la base de données
def read_last_request_number():
    global request_number
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="app"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT demande_numero FROM app.demands ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            request_number = result[0]
            label_request_number.config(text=f"Demande N°: {request_number}")  # Update the label
        else:
            request_number = "DA-1"  # Default request number if none exists
            label_request_number.config(text=f"Demande N°: {request_number}")  # Set default number
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de base de données", f"Erreur: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# Fonction pour mettre à jour le numéro de demande dans la base de données
def update_request_number():
    global request_number
    if request_number:
        current_number = int(request_number.split('-')[1])
        new_number = current_number + 1
        new_request_number = f"DA-{new_number}"

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="admin",
                database="app"
            )
            cursor = conn.cursor()

            # Optionally, insert the new request number in the database for tracking
            cursor.execute("INSERT INTO demands (demande_numero) VALUES (%s)", (new_request_number,))
            conn.commit()

            request_number = new_request_number  # Update the global variable
        except mysql.connector.Error as err:
            messagebox.showerror("Erreur de base de données", f"Erreur: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

# Fonction pour nettoyer la table demands
def clean_up_demands():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="app"
        )
        cursor = conn.cursor()

        # Get the ID of the last entry to keep it
        cursor.execute("SELECT id FROM app.demands ORDER BY id DESC LIMIT 1")
        last_entry = cursor.fetchone()

        if last_entry:
            last_entry_id = last_entry[0]
            # Delete entries where article or quantity is NULL or empty, but keep the last one
            cursor.execute("""
                DELETE FROM app.demands 
                WHERE (quoi IS NULL OR quoi = '' OR quantite IS NULL OR quantite = '')
                AND id <> %s
            """, (last_entry_id,))
            conn.commit()  # Commit the transaction

    except mysql.connector.Error as err:
        conn.rollback()  # Rollback if there is an error
        messagebox.showerror("Erreur de base de données", f"Erreur: {err}")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Fonction pour ajouter un article à la liste
def add_item():
    quoi = entry_item.get()
    quantite = entry_quantity.get()

    if not quoi or not quantite:
        messagebox.showwarning("Erreur de saisie", "Veuillez remplir tous les champs.")
        return

    try:
        # Ajouter l'article au treeview
        tree.insert("", "end", values=(quoi, quantite))
        entry_item.delete(0, tk.END)  # Effacer les champs de saisie
        entry_quantity.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Fonction pour soumettre la demande
def submit_demand():
    items = tree.get_children()
    if not items:
        messagebox.showwarning("Erreur de saisie", "Aucun article à soumettre.")
        return

    try:
        # Connecter à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="app"
        )
        cursor = conn.cursor()

        for item in items:
            quoi, quantite = tree.item(item, "values")
            # Check if the item and quantity are not empty
            if quoi and quantite:
                query = """
                    INSERT INTO demands (demande_numero, qui, quoi, quantite, date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (request_number, name, quoi, quantite, date.today()))

        conn.commit()
        clean_up_demands()
        messagebox.showinfo("Succès", "Demande soumise avec succès!")
        tree.delete(*items)  # Effacer le treeview après soumission
        update_request_number()  # Mettre à jour le numéro de demande pour la prochaine demande
        label_request_number.config(text=f"Demande N°: {request_number}")  # Met à jour le label après la soumission

    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de base de données", f"Erreur: {err}")
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# Create the main window
root = tk.Tk()
root.title("PurchasePro App")
root.geometry("800x600")
root.configure(bg='#E9EAEC')

# Load the logo image
logo_image = Image.open("logo2.png")  # Replace with your image path
logo_image = logo_image.resize((250, 100), Image.LANCZOS)  # Resize the logo to appropriate size
logo_photo = ImageTk.PhotoImage(logo_image)

# Top-left: Logo
logo_label = tk.Label(root, image=logo_photo, bg='#E9EAEC')
logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Center: Welcome message
welcome_label = tk.Label(root, text=f"Bienvenue {name}", font=("Times New Roman", 20), bg='#E9EAEC')
welcome_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Top-right: Logout button
logout_button = tk.Button(root, text="Déconnecter", font=("Times New Roman", 14, "bold"), bg='blue', fg='white', command=logout)
logout_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

# Demand form
demand_frame = tk.Frame(root, bg='#E9EAEC')
demand_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=20)

# Display the request number
label_request_number = tk.Label(demand_frame, text="Request Number: Not Generated", bg='#E9EAEC', font=("Arial", 14))
label_request_number.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

label_item = tk.Label(demand_frame, text="Article:", bg='#E9EAEC')
label_item.grid(row=1, column=0, padx=10, pady=5)

# Increased width of the entry widget
entry_item = tk.Entry(demand_frame, font=("Arial", 14), bd=2, relief=tk.SOLID, width=30)  # Set the width
entry_item.grid(row=1, column=1, padx=10, pady=5)

label_quantity = tk.Label(demand_frame, text="Quantité:", bg='#E9EAEC')
label_quantity.grid(row=2, column=0, padx=10, pady=5)

# Increased width of the entry widget
entry_quantity = tk.Entry(demand_frame, font=("Arial", 14), bd=2, relief=tk.SOLID, width=30)  # Set the width
entry_quantity.grid(row=2, column=1, padx=10, pady=5)

btn_add_item = tk.Button(demand_frame, text="Add Item", font=("Arial", 14, "bold"), bg='#4CAF50', fg='white', command=add_item)
btn_add_item.grid(row=3, column=0, columnspan=2, pady=10)

# Treeview to display added items
columns = ("Item", "Quantity")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
tree.heading("Item", text="Article")
tree.heading("Quantity", text="Quantité")
# Set width for each column
tree.column("Item", width=300)  # Adjust width as needed
tree.column("Quantity", width=100)  # Adjust width as needed

# Create a vertical scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Place the treeview and scrollbar in the layout
tree.grid(row=4, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")
scrollbar.grid(row=4, column=3, sticky="ns")

# Submit demand button
btn_submit_demand = tk.Button(root, text="Submit Demand", font=("Arial", 14, "bold"), bg='#4CAF50', fg='white', command=submit_demand)
btn_submit_demand.grid(row=5, column=0, columnspan=3, pady=20)

# Configure grid to ensure proper layout:
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(2, weight=0)
root.grid_rowconfigure(4, weight=1)

# Initializing the request number from the database
read_last_request_number()

# Run the application
root.mainloop()
