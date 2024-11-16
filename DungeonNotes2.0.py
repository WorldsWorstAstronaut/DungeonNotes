import tkinter as tk
from tkinter import ttk, Text, StringVar, messagebox
import sqlite3  # SQLite for the database
import pygame   # For playing sound

# Step 1: Setup SQLite connection (creates the database file if it doesn't exist)
def connect_to_db():
    conn = sqlite3.connect('dnd_database.db')  # SQLite uses a file-based database
    return conn

# Step 2: Create a table if it doesn't already exist
def create_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            race TEXT,
            gender TEXT,
            class TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize pygame for sound
pygame.mixer.init()

# List of DnD races and classes
RACE_OPTIONS = [
    "Human", "Elf", "Dwarf", "Halfling", "Half-Elf", "Half-Orc", "Tiefling", "Dragonborn", "Gnome",
    "Aasimar", "Air Genasi", "Earth Genasi", "Fire Genasi", "Water Genasi",
    "Firbolg", "Goliath", "Tabaxi", "Lizardfolk", "Kenku", "Hobgoblin", "Goblin", "Bugbear", "Triton",
    "Yuan-ti Pureblood", "Aarakocra", "Kobold", "Tortle", "Changeling", "Shifter", "Warforged",
    "Leonin", "Satyr", "Loxodon", "Centaur", "Vedalken", "Simic Hybrid", "Verdan", "Grung"
]

CLASS_OPTIONS = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", 
    "Sorcerer", "Warlock", "Wizard", "Artificer"
]

# Step 2: Tkinter Window Setup
class DnDCharacterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DnD Character Manager")

        # Initialize StringVars for dropdowns
        self.race_var = StringVar()
        self.gender_var = StringVar()
        self.class_var = StringVar()

        # Entry fields
        tk.Label(root, text="Name:").grid(row=0, column=0)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1)

        # Dropdown for Race with reordered race list
        tk.Label(root, text="Race:").grid(row=1, column=0)
        self.race_menu = ttk.OptionMenu(root, self.race_var, "Select Race", *RACE_OPTIONS)
        self.race_menu.grid(row=1, column=1)

        # Dropdowns for Gender and Class with updated class list
        tk.Label(root, text="Gender:").grid(row=2, column=0)
        self.gender_menu = ttk.OptionMenu(root, self.gender_var, "Select Gender", "Male", "Female", "Non-binary")
        self.gender_menu.grid(row=2, column=1)

        tk.Label(root, text="Class:").grid(row=3, column=0)
        self.class_menu = ttk.OptionMenu(root, self.class_var, "Select Class", *CLASS_OPTIONS)
        self.class_menu.grid(row=3, column=1)

        # Notes section
        tk.Label(root, text="Notes:").grid(row=4, column=0)
        self.notes_text = Text(root, height=10, width=30)
        self.notes_text.grid(row=4, column=1)

        # Buttons
        self.save_button = tk.Button(root, text="Save Character", command=self.save_character)
        self.save_button.grid(row=5, column=0)

        self.update_button = tk.Button(root, text="Update Character", command=self.update_character)
        self.update_button.grid(row=5, column=1)

        self.delete_button = tk.Button(root, text="Delete Character", command=self.delete_character)
        self.delete_button.grid(row=5, column=2)

        # Treeview for displaying characters
        self.character_tree = ttk.Treeview(root, columns=("Name", "Race", "Class"), show="headings")
        self.character_tree.heading("Name", text="Name")
        self.character_tree.heading("Race", text="Race")
        self.character_tree.heading("Class", text="Class")
        self.character_tree.grid(row=6, column=0, columnspan=3)

        self.character_tree.bind("<<TreeviewSelect>>", self.on_character_select)  # Binding the selection event

        self.refresh_button = tk.Button(root, text="Refresh Character List", command=self.load_characters)
        self.refresh_button.grid(row=7, column=1)

        # Add buttons to play sound effects at the bottom
        self.wilhelm_button = tk.Button(root, text="Play Wilhelm Scream", command=self.play_wilhelm_scream)
        self.wilhelm_button.grid(row=8, column=0)

        self.ffwin_button = tk.Button(root, text="Play Victory Fanfare", command=self.play_victory_fanfare)
        self.ffwin_button.grid(row=8, column=2)

        # Load characters into the treeview on startup
        self.load_characters()

        # Placeholder for selected character ID
        self.selected_character_id = None

    # Step 3: Save character to SQLite
    def save_character(self):
        name = self.name_entry.get()
        race = self.race_var.get()
        gender = self.gender_var.get()
        char_class = self.class_var.get()

        if not name or race == "Select Race" or gender == "Select Gender" or char_class == "Select Class":
            messagebox.showwarning("Input Error", "Please fill out all fields before saving.")
            return

        conn = connect_to_db()
        cursor = conn.cursor()

        notes = self.notes_text.get("1.0", tk.END)

        sql = "INSERT INTO characters (name, race, gender, class, notes) VALUES (?, ?, ?, ?, ?)"
        values = (name, race, gender, char_class, notes)
        cursor.execute(sql, values)

        conn.commit()
        conn.close()

        # Refresh the list after saving
        self.load_characters()
        self.clear_form()  # Clear the form after saving

    # Step 4: Load characters into the Treeview
    def load_characters(self):
        conn = connect_to_db()
        cursor = conn.cursor()

        # Clear the current list
        for row in self.character_tree.get_children():
            self.character_tree.delete(row)

        cursor.execute("SELECT id, name, race, class FROM characters")
        characters = cursor.fetchall()

        for character in characters:
            self.character_tree.insert("", "end", values=(character[1], character[2], character[3]), iid=character[0])

        conn.close()

    # Step 5: Handle character selection in the Treeview
    def on_character_select(self, event):
        selected_item = self.character_tree.selection()  # Get selected item
        if selected_item:
            self.selected_character_id = selected_item[0]  # Store the ID of the selected character

            # Load character details into the form
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name, race, gender, class, notes FROM characters WHERE id = ?", (self.selected_character_id,))
            character = cursor.fetchone()

            if character:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, character[0])

                self.race_var.set(character[1])
                self.gender_var.set(character[2])
                self.class_var.set(character[3])

                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", character[4])

            conn.close()

    # Step 6: Delete character from SQLite
    def delete_character(self):
        if self.selected_character_id:
            conn = connect_to_db()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM characters WHERE id = ?", (self.selected_character_id,))
            conn.commit()
            conn.close()

            # Clear selection
            self.selected_character_id = None

            # Refresh the list after deletion
            self.load_characters()
            self.clear_form()  # Clear the form after deletion

            messagebox.showinfo("Success", "Character deleted successfully!")
        else:
            messagebox.showwarning("Select a Character", "Please select a character to delete.")

    # Step 7: Update character details in SQLite
    def update_character(self):
        if self.selected_character_id:
            name = self.name_entry.get()
            race = self.race_var.get()
            gender = self.gender_var.get()
            char_class = self.class_var.get()

            if not name or race == "Select Race" or gender == "Select Gender" or char_class == "Select Class":
                messagebox.showwarning("Input Error", "Please fill out all fields before updating.")
                return

            conn = connect_to_db()
            cursor = conn.cursor()

            notes = self.notes_text.get("1.0", tk.END)

            # Update the selected character
            cursor.execute('''
                UPDATE characters
                SET name = ?, race = ?, gender = ?, class = ?, notes = ?
                WHERE id = ?
            ''', (name, race, gender, char_class, notes, self.selected_character_id))

            conn.commit()
            conn.close()

            # Refresh the list after updating
            self.load_characters()
            self.clear_form()  # Clear the form after updating

            messagebox.showinfo("Success", "Character updated successfully!")
        else:
            messagebox.showwarning("Select a Character", "Please select a character to update.")

    # Step 8: Play Wilhelm Scream
    def play_wilhelm_scream(self):
        try:
            pygame.mixer.music.load("wilhelm_scream.mp3")  # Ensure the file path is correct
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Could not play Wilhelm Scream: {e}")

    # Step 9: Play Victory Fanfare sound
    def play_victory_fanfare(self):
        try:
            pygame.mixer.music.load("victory_fanfare.mp3")  # Ensure the file path is correct
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Could not play Victory Fanfare: {e}")

    # Step 10: Clear the form fields
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.race_var.set("Select Race")
        self.gender_var.set("Select Gender")
        self.class_var.set("Select Class")
        self.notes_text.delete("1.0", tk.END)
        self.selected_character_id = None  # Clear selected ID

# Step 11: Run the Tkinter App and create the database
if __name__ == "__main__":
    create_table()  # Ensure table is created before running the app
    root = tk.Tk()
    app = DnDCharacterApp(root)
    root.mainloop()
