import tkinter as tk
from tkinter import messagebox, StringVar, Frame
import requests
from PIL import Image, ImageTk
from io import BytesIO
import html  # Import the html library

# Constants
API_URL = 'https://graphql.anilist.co'


# Function to query the AniList API
def query_anilist(query, search_type):
    if search_type == "Character":
        query_string = '''
        query ($search: String) {
          Character(search: $search) {
            name {
              full
            }
            image {
              large
            }
            description
          }
        }
        '''
    else:  # Default to searching for Series
        query_string = '''
        query ($search: String) {
          Media(search: $search) {
            title {
              romaji
              english
            }
            coverImage {
              large
            }
            description
          }
        }
        '''

    variables = {'search': query}
    response = requests.post(API_URL, json={'query': query_string, 'variables': variables})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed with a {}: {}".format(response.status_code, response.text))


# Function to handle search
def search(event=None):
    search_term = search_entry.get()
    search_type = search_var.get()
    if not search_term:
        messagebox.showwarning("Input Error", "Please enter a search term.")
        return

    try:
        result = query_anilist(search_term, search_type)
        if search_type == "Character":
            media = result['data']['Character']
        else:
            media = result['data']['Media']

        if media:
            display_result(media, search_type)
        else:
            messagebox.showinfo("No Results", "No results found for '{}'.".format(search_term))
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Function to display the result
def display_result(media, search_type):
    if search_type == "Character":
        title = media['name']['full']
        description = media['description']
        image_url = media['image']['large']
    else:  # Default to Series
        title = media['title']['romaji'] or media['title']['english']
        description = media['description']
        image_url = media['coverImage']['large']

    description = html.unescape(description)  # Decode HTML entities
    description = description.replace('<br>', '\n')  # Replace <br> with newline

    title_label.config(text=title)
    description_label.config(text=description)

    # Load image
    response = requests.get(image_url)
    img_data = Image.open(BytesIO(response.content))
    img = ImageTk.PhotoImage(img_data)

    # Update image
    image_label.config(image=img)
    image_label.image = img  # Keep a reference


# Setting up the main application window
app = tk.Tk()
app.title("AniList Search")
app.configure(bg="#1e1e1e")
app.geometry("800x600")  # Increased window size

# Header
header_label = tk.Label(app, text="Search information about any series or character!", font=('Coolvetica', 24),
                        bg="#1e1e1e", fg="white")
header_label.pack(pady=20)

# Frame for Dropdown
dropdown_frame = Frame(app, bg="#1e1e1e")
dropdown_frame.pack(pady=10)

# Search Type Menu
search_var = StringVar(app)
search_var.set("Series")  # Default value

# Create a stylized dropdown
search_menu = tk.OptionMenu(dropdown_frame, search_var, "Series", "Character")
search_menu.config(bg="#444444", fg="white", font=('Coolvetica', 14), activebackground="#555555",
                   activeforeground="white")
search_menu["menu"].config(bg="#444444", fg="white")
search_menu.pack()

# Search Entry (Round and Transparent)
search_entry = tk.Entry(app, font=('Coolvetica', 16), justify='center', bd=0, bg="#444444", fg="white")
search_entry.pack(pady=10, padx=20, fill='x')
search_entry.bind("<Return>", search)  # Bind Enter key to search function

# Result Title
title_label = tk.Label(app, text="", font=('Coolvetica', 20), bg="#1e1e1e", fg="white")
title_label.pack(pady=10)

# Result Image
image_label = tk.Label(app, bg="#1e1e1e")
image_label.pack(pady=10)

# Result Description
description_label = tk.Label(app, text="", wraplength=700, justify="left", bg="#1e1e1e", fg="white",
                             font=('Coolvetica', 12))
description_label.pack(pady=10)

# Run the application
app.mainloop()
