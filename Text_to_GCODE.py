#Import tkinter and Scrolledtext
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import textwrap
import os.path
import pickle

gcode_output = ""
#Open Text File
def openFile():
    oF = filedialog.askopenfilename(title="Open Textfile", filetypes=(("Text Files", "*.txt"),))
    with open(oF, "r", encoding="utf-8", errors="ignore") as infile:
        indata = infile.read()
        text_area0.delete("1.0", "end")
        text_area0.insert(1.0, indata)
    

#Main Function
def showPreview():    
    global gcode_output
 
    #Show Wrapped Text and Text Size
    getText = text_area0.get("1.0", "end")
    wrapper = textwrap.TextWrapper(width=int(EntryLabel1.get()), replace_whitespace=False)           
    string = wrapper.fill(text=getText)                     
    textlines = string.splitlines()
    printmatrix = EntryLabel0.get().split(", ")                                                      
    pm_float = [float(item) for item in printmatrix]
    Xmatrix = pm_float[0]
    Ymatrix = pm_float[1]
    most_chars = float(len(max(textlines, key=len)))                                                 
    Textsize = [(Xmatrix * most_chars), (Ymatrix * len(textlines))]
    Label4.config(text = str(Textsize))
    
    #Create i2c Commands
    text_lists_of_chars = [list(c) for c in textlines]
    lists_of_values = [[ord(item) for item in group] for group in text_lists_of_chars]
    lists_of_strings = [[str(x) for x in l] for l in lists_of_values]
    carriage_return = [item + ["13"] for item in lists_of_strings]
    byte_command = [["M260 B" + item + "\n" for item in group] for group in carriage_return]
    adress_command = [["M260 A9\n"] + item for item in byte_command]
    send_command = [item + ["M260 S1\n"] for item in adress_command]
    i2c_commands = ["".join(item) for item in send_command]
    
    #Calculate Print-Start Coordinates
    Y_coordinates = [x * Ymatrix for x in range(0, len(textlines))]
    Y_coordinates_floatlists = [[c] for c in Y_coordinates]
    Y_coordinates_stringlists = [[str(x) for x in l] for l in Y_coordinates_floatlists]
    Ystart_add_text = [["Y" + item + " F" + EntryLabel9.get() + "\nM106 P1 S255\n" for item in group] for group in Y_coordinates_stringlists]
    XYstart_lists = [["G1 X0.0 "] + item for item in Ystart_add_text]
    XYstart_strings = ["".join(item) for item in XYstart_lists]
    
    #Calculate Print-End Coordinates
    Xend_coordinates = [(len(item) * Xmatrix + float(EntryLabel2.get())) for item in textlines]
    Xend_coordinates_floatlists = [[c] for c in Xend_coordinates]
    Xend_coordinates_stringlists = [[str(x) for x in l] for l in Xend_coordinates_floatlists]
    Xend_add_text = [["G1 X" + item +  " " for item in group] for group in Xend_coordinates_stringlists]
    Yend_add_text = [["Y" + item + " F" + EntryLabel9.get() + "\nM106 P1 S0\n" for item in group] for group in Y_coordinates_stringlists]
    Xend_strings = ["".join(item) for item in Xend_add_text]
    Yend_strings = ["".join(item) for item in Yend_add_text]
    XYend_zip = zip(Xend_strings, Yend_strings)
    XYend_list = list(XYend_zip)
    XYend_strings = ["".join(item) for item in XYend_list]
   
    #Create GCODE
    gcode_zip = zip(i2c_commands, XYstart_strings, XYend_strings)
    gcode_list = list(gcode_zip)
    gcode_string_list = ["".join(item) for item in gcode_list]
    gcode_string = "".join(gcode_string_list)
    gcode_output = text_area1.get(1.0, "end") + gcode_string + text_area2.get(1.0, "end")
    
    #Show Preview
    text_area0.delete("1.0", "end")
    text_area0.insert(1.0, str(string))
    
#Change Label back to -  
def restoreLabel():
    Label8.config(text="-")
    
#Save Settings to File
def saveSettings(event):
    SettingValues = {"Print Matrix X, Y": EntryLabel0.get(), "Line Charakter Limit": EntryLabel1.get(),
                     "Runout": EntryLabel2.get(), "Speed F": EntryLabel9.get(), "Startcode": text_area1.get(1.0,
                     "end"), "Endcode": text_area2.get(1.0, "end")}
    pickle.dump( SettingValues, open( "Settings.p", "wb" ) )
    Label8.config(text="Saving")
    win.after(1000, restoreLabel)
    
#Convert Text to GCODE and save it
def saveGCODE():
    showPreview()
    sF = filedialog.asksaveasfilename(defaultextension=".gcode", title="Save GCODE", filetypes=(("GCODE Files", "*.gcode"),))
    with open(sF, "w") as outfile:
        outdata = text_area0.get("1.0", "end")
        outfile.write(gcode_output)
    
#Creating tkinter Main Window
win = tk.Tk()
win.title("Text to GCODE")
win.state("zoomed")

#Frames
Settings = tk.Frame(win)
Settings.grid(column = 0, row = 0, pady = 10, padx = 10, sticky="e")
TextInput = tk.Frame(win)
TextInput.grid(column = 0, row = 1, pady = 10, padx = 10, sticky="w")
Buttons = tk.Frame(win)
Buttons.grid(column = 0, row = 0, pady = 10, padx = 10, sticky="w")
Startcode = tk.Frame(win)
Startcode.grid(column = 0, row = 2, pady = 10, padx = 10, sticky="w")
Endcode = tk.Frame(win)
Endcode.grid(column = 0, row = 2, pady = 10, padx = 10, sticky="e")

#Scrolled Texts
text_area0 = scrolledtext.ScrolledText(TextInput, wrap = tk.WORD, width = 130, height = 18, font = ("Courier", 12))
text_area0.grid(column = 0, row = 0, pady = 10, padx = 10)
text_area1 = scrolledtext.ScrolledText(Startcode, wrap = tk.WORD, width = 60, height = 4, font = ("Courier", 12))
text_area1.grid(column = 0, row = 1, pady = 10, padx = 10)
text_area2 = scrolledtext.ScrolledText(Endcode, wrap = tk.WORD, width = 60, height = 4, font = ("Courier", 12))
text_area2.grid(column = 0, row = 1, pady = 10, padx = 10)

#Buttons
Button0 = tk.Button(Buttons, text="Open Text File", command=openFile, width=20, height=1)
Button0.grid(column = 0, row = 0, pady = 10, padx = 10, sticky="e")
Button1 = tk.Button(Buttons, text="Show Preview", command=showPreview, width=20, height=1)
Button1.grid(column = 0, row = 1, pady = 10, padx = 10, sticky="e")
Button2 = tk.Button(Buttons, text="Save GCODE", command=saveGCODE, width=20, height=1)
Button2.grid(column = 0, row = 2, pady = 10, padx = 10, sticky="e")

#Labels
Label0 = tk.Label(Settings, text="Print Matrix X, Y")
Label0.grid(column = 0, row = 0, pady = 10, padx = 10, sticky="w")
Label1 = tk.Label(Settings, text="Line Charakter Limit")
Label1.grid(column = 0, row = 2, pady = 10, padx = 10, sticky="w")
Label2 = tk.Label(Settings, text="Runout")
Label2.grid(column = 0, row = 1, pady = 10, padx = 10, sticky="w")
Label3 = tk.Label(Settings, text="Text Size X, Y")
Label3.grid(column = 2, row = 1, pady = 10, padx = 10, sticky="w")
Label4 = tk.Label(Settings, text="[0.0, 0.0]")
Label4.grid(column = 3, row = 1, pady = 10, padx = 10, sticky="ew")
Label5 = tk.Label(Startcode, text="Startcode")
Label5.grid(column = 0, row = 0, pady = 10, padx = 10, sticky="w")
Label6 = tk.Label(Endcode, text="Endcode")
Label6.grid(column = 0, row = 0, pady = 10, padx = 10, sticky="w")
Label7 = tk.Label(Settings, text="Save Settings", fg="blue", cursor="hand2")
Label7.grid(column = 2, row = 2, pady = 10, padx = 10, sticky="w")
Label8 = tk.Label(Settings, text="-")
Label8.grid(column = 3, row = 2, pady = 10, padx = 10, sticky="ew")
Label9 = tk.Label(Settings, text="Speed F")
Label9.grid(column = 2, row = 0, pady = 10, padx = 10, sticky="w")

#Make Label7 clickable
Label7.bind("<Button-1>", saveSettings)

#Entrys
EntryLabel0 = tk.Entry(Settings)
EntryLabel0.grid(column = 1, row = 0, pady = 10, padx = 10, sticky="w")
EntryLabel1 = tk.Entry(Settings)
EntryLabel1.grid(column = 1, row = 2, pady = 10, padx = 10, sticky="w")
EntryLabel2 = tk.Entry(Settings)
EntryLabel2.grid(column = 1, row = 1, pady = 10, padx = 10, sticky="w")
EntryLabel9 = tk.Entry(Settings)
EntryLabel9.grid(column = 3, row = 0, pady = 10, padx = 10, sticky="w")

#If no Pickle File exists, create one
defaultSettings = {"Print Matrix X, Y": "Empty", "Line Charakter Limit": "Empty",
                   "Runout": "Empty", "Speed F": "Empty", "Startcode": "Empty", "Endcode": "Empty"}
if os.path.isfile("Settings.p") == False:
    pickle.dump(defaultSettings, open("Settings.p", "wb"))

#Load Settings from File
SettingValues = pickle.load(open("Settings.p", "rb"))
EntryLabel0.insert(0, SettingValues.get("Print Matrix X, Y"))
EntryLabel1.insert(0, SettingValues.get("Line Charakter Limit"))
EntryLabel2.insert(0, SettingValues.get("Runout"))
text_area1.insert(1.0, SettingValues.get("Startcode"))
text_area2.insert(1.0, SettingValues.get("Endcode"))
EntryLabel9.insert(0, SettingValues.get("Speed F"))

#Mainloop
win.mainloop()
