#Import libraries
import os
import tkinter
import json
from tkinter import *
from tkinter import filedialog, colorchooser, font
from tkinter.messagebox import *
from tkinter.filedialog import *

about_txt = "About.txt"
help_txt = "Help.txt"

active_tags = set()

#Changing color
def change_color():
    color = colorchooser.askcolor(title="Pick a color")
    main.text_area.config(fg=color[1])

#Resizing font
def resize_font(event=None):
    #Try to get the int from the 'size_box' and apply it
    try:
        new_size = int(main.size_box.get())
        main.text_area.config(font=(main.font_name.get(), new_size))
    except ValueError:
        #If the box contains some kind of string, trigger the error
        print("[!] Invalid font size input. Please enter a number [!]")

#Change the font (call to finalize)
def change_font(*args):
    resize_font()

#Makes bold
def make_bold(event=None):
    toggle_format("bold", (main.font_name, main.size_box.get(), "bold"))

#Makes italic
def make_italic(event=None):
    toggle_format("italic", (main.font_name, main.size_box.get(), "italic"))

#Makes underline
def make_underline(event=None):
    toggle_format("underline", (main.font_name, main.size_box.get(), "underline"))

#Called in whichever function
def toggle_format(tag_name, font_style):
    if tag_name in active_tags:
        active_tags.remove(tag_name)
    else:
        active_tags.add(tag_name)
    main.text_area.tag_configure(tag_name, font=font_style)

def apply_active_tags(event=None):
    index = main.text_area.index("insert-1c")
    for tag in active_tags:
        main.text_area.tag_add(tag, index, f"{index} +1c")


#Creates a new file in a new window (calls 'main' function)
def new_file(event=None):
    main()

def save_file(event=None):
    file = filedialog.asksaveasfilename(initialfile='untitled.txt',
                                        defaultextension='.json',
                                        filetypes=[("Formatted Text", "*.json"), ("All Files", "*.*")])
    if file is None:
        return
    try:
        text = main.text_area.get(1.0, "end-1c")
        tags_data = []
        for tag in main.text_area.tag_names():
            for start, end in zip(main.text_area.tag_ranges(tag)[::2], main.text_area.tag_ranges(tag)[1::2]):
                tag_config = {}
                try:
                    tag_font = main.text_area.tag_cget(tag, "font")
                    tag_fg = main.text_area.tag_cget(tag, "foreground")
                    if tag_font:
                        tag_config["font"] = tag_font
                    if tag_fg:
                        tag_config["foreground"] = tag_fg
                except:
                    pass  # ignore errors for tags that don't have specific properties
                tags_data.append({
                    "tag": tag,
                    "start": str(start),
                    "end": str(end),
                    "config": tag_config
                })
        data = {
            "text": text,
            "tags": tags_data,
            "font": main.font_name.get(),
            "size": main.size_box.get()
        }
        with open(file, "w") as f:
            json.dump(data, f)
        main.window.title(os.path.basename(file))
    except Exception as e:
        print(f"[!] Couldn't save file: {e}")

def open_file(event=None):
    file = filedialog.askopenfilename(filetypes=[
        ("Formatted Text", "*.json"),
        ("Plain Text", "*.txt"),
        ("All Files", "*.*")
    ])
    if file is None:
        return
    try:
        if file.endswith(".json"):
            with open(file, "r") as f:
                data = json.load(f)
            main.text_area.delete(1.0, END)
            main.text_area.insert(1.0, data["text"])
            main.font_name.set(data.get("font", "Arial"))
            main.size_box.set(data.get("size", "20"))
            main.text_area.config(font=(main.font_name.get(), int(main.size_box.get())))
            for tag_info in data["tags"]:
                tag = tag_info["tag"]
                start = tag_info["start"]
                end = tag_info["end"]
                style = tag_info.get("config", {})
                if style:
                    main.text_area.tag_configure(tag, **style)
                main.text_area.tag_add(tag, start, end)
        else:
            with open(file, "r") as f:
                content = f.read()
            main.text_area.delete(1.0, END)
            main.text_area.insert(1.0, content)
        main.window.title(os.path.basename(file))
    except Exception as e:
        print(f"[!] Couldn't read file: {e}")

#Delete and copy (i.e cut)
def cut():
    main.text_area.event_generate("<<Cut>>")

#Copy
def copy():
    main.text_area.event_generate("<<Copy>>")

#Paste
def paste():
    main.text_area.event_generate("<<Paste>>")

#A simple about pop-up
def about():
    with open(about_txt, 'r') as file:
        content = file.read()     

    showinfo("About this program", content)

def help_file():
    #Open the file explorer.
    file = help_txt

    #Try to open file
    try:
        #Sets the window title to file title
        main.window.title(os.path.basename(file))
        main.text_area.delete(1.0, END)

        #Open in read
        file = open(file, "r")

        main.text_area.insert(1.0, file.read())
    except Exception:
        #If file is not found, trigger error
        showinfo("[!]Couldn't open file. File may be missing or moved[!]")
    
#Quit the program
def quit():
    main.window.destroy()

#Hide scrollbar when no text overrides the limit
def toggle_scrollbar(event=None):
    if main.text_area.yview()[1] - main.text_area.yview()[0] < 1:
        main.scroll_bar.pack(side=RIGHT, fill=Y)
    else:
        main.scroll_bar.pack_forget()

#Main function
def main():
    #Create window, apply title and make file blank
    window = Tk()
    window.title("Txt Editor")
    file = None

    #Window variables
    window_width = 500
    window_height = 500
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int(screen_width / 2 - (window_width / 2))
    y = int(screen_height / 2 - (window_height / 2))

    #Set window dimensions
    window.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))

    #Set default font
    font_name = StringVar(window)
    font_name.set("Arial")

    #Set default font size
    font_size = StringVar(window)
    font_size.set("20")

    #Make text wrap when overriding edge of text area
    text_area = Text(window, font=(font_name.get(), int(font_size.get())), wrap="word")
    scroll_bar = Scrollbar(text_area)
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    text_area.grid(sticky=N + E + S + W)
    scroll_bar.config(command=text_area.yview)
    text_area.config(yscrollcommand=scroll_bar.set)

    #Apply formatting on key insert
    text_area.bind("<Key>", apply_active_tags)
    
    #Add frame
    frame = Frame(window)
    frame.grid(row=1, column=0, sticky='ew')
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)

    #Left frame (font controls)
    l_frame = Frame(frame)
    l_frame.grid(row=0, column=0, sticky='w')
    font_box = OptionMenu(l_frame, font_name, *font.families(), command=change_font)
    font_box.pack(side=LEFT)
    size_box = Spinbox(l_frame, from_=1, to=100, width=4, textvariable=font_size, command=change_font)
    size_box.pack(side=LEFT)
    size_box.bind("<Return>", resize_font) #Bind 'Enter' to apply new font size

    #Center frame (formatting buttons)
    c_frame = Frame(frame)
    c_frame.grid(row=0, column=1)
    bold_button = Button(c_frame, text="B", font=("Helvetica", 10, "bold"), command=make_bold)
    bold_button.pack(side=LEFT, padx=2)
    italic_button = Button(c_frame, text="I", font=("Helvetica", 10, "italic"), command=make_italic)
    italic_button.pack(side=LEFT, padx=2)
    underline_button = Button(c_frame, text="U", font=("Helvetica", 10, "underline"),command=make_underline)
    underline_button.pack(side=LEFT, padx=2)

    #Right frame (color button)
    r_frame = Frame(frame)
    r_frame.grid(row=0, column=2, sticky='e')
    color_button = Button(r_frame, text="Color", command=change_color)
    color_button.pack(side=RIGHT)
    
    #Create menu bar at the top of the window
    menu_bar = Menu(window)
    window.config(menu=menu_bar)

    #Instance the 'File' menu popup
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New File            Ctrl+N", command=new_file)
    file_menu.add_command(label="Open File           Ctrl+O", command=open_file)
    file_menu.add_command(label="Save File           Ctrl+S", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=quit)

    #Instance the 'Edit' menu popup
    edit_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Cut            Ctrl+X", command=cut)
    edit_menu.add_command(label="Copy            Ctrl+C", command=copy)
    edit_menu.add_command(label="Paste            Ctrl+V", command=paste)

    #Instance the 'Help' menu popup
    help_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=about)
    help_menu.add_command(label="Txt Help", command=help_file)

    #Keybinds for different options
    window.bind("<Control-n>", new_file)
    window.bind("<Control-o>", open_file)
    window.bind("<Control-s>", save_file)
    window.bind("<Control-b>", make_bold)
    window.bind("<Control-i>", make_italic)
    window.bind("<Control-u>", make_underline)

    #Show the scrollbar if either is triggered
    text_area.bind("<KeyRelease>", toggle_scrollbar)
    text_area.bind("<MouseWheel>", toggle_scrollbar)

    main.text_area = text_area
    main.scroll_bar = scroll_bar
    main.font_name = font_name
    main.size_box = font_size
    main.window = window

    toggle_scrollbar()
    window.mainloop()

main()
