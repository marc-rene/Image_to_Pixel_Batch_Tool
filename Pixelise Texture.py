import json
import os
import webbrowser
import subprocess
from ttkthemes import ThemedTk
import multiprocessing
import tkinter.messagebox
import tkinter.colorchooser
from PIL import Image
import logging
from pathlib import Path
logging.basicConfig(level=logging.INFO)

import tkinter
from tkinter import ttk
from tkinter import filedialog
from ttkthemes import ThemedTk


Img_to_Pix_label : tkinter.Label
All_Folders_Label_I : tkinter.Label
All_Folders_Label_O : tkinter.Label
All_Presets_Label : tkinter.Label

ALL_MY_DAEMONS_PALETTE = []
ALL_MY_DAEMONS_BG = []
SESSION_SETTINGS = ""
FOLDER_LIST = {}
PRESET_LIST = {}
FIRST_TIME_RUNNING = True
IMAGE_TO_PIXEL_TOOL_PATH = Path("NO PATH HAS BEEN DEFINED FOR THE IMAGE TO PIXEL TOOL")
#CURRENT_ACTIVE_PRESET = "NO ACTIVE PRESET"

def Update_Labels():
    global FOLDER_LIST
    global PRESET_LIST
    global IMAGE_TO_PIXEL_TOOL_PATH
    logging.info("Updating labels")
    Img_to_Pix_label.config(text=f"Img_2_Pix tool : {IMAGE_TO_PIXEL_TOOL_PATH}" if (IMAGE_TO_PIXEL_TOOL_PATH.exists() and IMAGE_TO_PIXEL_TOOL_PATH.is_file() and IMAGE_TO_PIXEL_TOOL_PATH != ".") else "Img_2_Pix tool has NOT been found, please set", 
                            foreground="green" if (IMAGE_TO_PIXEL_TOOL_PATH.exists() and IMAGE_TO_PIXEL_TOOL_PATH.is_file() and IMAGE_TO_PIXEL_TOOL_PATH != ".") else "red",)

    folder_list_str_I = "Input Folders:"
    folder_list_str_O = "Output Folders:"
    for path in FOLDER_LIST:
        folder_list_str_I += f"\n{path}"
        folder_list_str_O += f"\n{FOLDER_LIST[path]}"
    All_Folders_Label_I.config(text=folder_list_str_I)
    All_Folders_Label_O.config(text=folder_list_str_O)
    
    presets_str = "All Presets:" if len(PRESET_LIST.keys()) > 0 else "No Saved Presets"
    itr = 1
    for preset in PRESET_LIST:
        presets_str += f"\nPreset {itr}: {preset}"
        if PRESET_LIST[preset]["Active"]:
            presets_str += ": ACTIVE"
        itr+=1
    All_Presets_Label.config(text=presets_str, foreground="black" if len(PRESET_LIST.keys()) > 0 else "red")

def GetActivePreset() -> str:
    global PRESET_LIST
    for preset in PRESET_LIST:
        if PRESET_LIST[preset]["Active"]:
            return preset
    logging.error("THERE IS NO ACTIVE PRESET")
    return ""


def TryGetLastSessionSettings() -> bool:
    global FOLDER_LIST
    global PRESET_LIST
    global IMAGE_TO_PIXEL_TOOL_PATH
    
    try:
        lastRuntimeSettings = json.loads(open("last runtime settings.json", "r").read())
        logging.debug(f"Saved settings read as {lastRuntimeSettings}")
        if lastRuntimeSettings is None:
            raise Exception("\"last runtime settings.json\" is empty")
        else:
            logging.info("Previous runtime settings found, great success")
            SESSION_SETTINGS = lastRuntimeSettings
            logging.info(f"SESSION SETTINGS are now: {SESSION_SETTINGS}")
            
            FOLDER_LIST = SESSION_SETTINGS["FOLDER LIST"]
            logging.info(f"FOLDER LIST is now: {FOLDER_LIST}")
            
            IMAGE_TO_PIXEL_TOOL_PATH = Path(SESSION_SETTINGS["IMAGE TO PIXEL TOOL LOCATION"])
            logging.info(f"IMAGE_TO_PIXEL_TOOL_PATH is now: {IMAGE_TO_PIXEL_TOOL_PATH}")
            
            PRESET_LIST = SESSION_SETTINGS["PRESET LIST"]
            logging.info(f"PRESET list is now: {PRESET_LIST}")
            Update_Labels()
            return True
    except Exception as E:
        logging.info(f"Previous runtime settings not found because: {repr(E)}")
        return False


def add_folder() -> bool:
    global FOLDER_LIST
    logging.info("Starting File dialog")
    return_result = False
    while True:

        input_folder = tkinter.filedialog.askdirectory(title="Select Input Folder")
        if not input_folder:
            logging.debug("Cancelled Input folder selection")
            break

        if input_folder in FOLDER_LIST:
            logging.warning(f"{input_folder} already exists in our folder list")
            return_result = False
            break
        else:
            output_folder = tkinter.filedialog.askdirectory(title="Select Output Folder")
            if not output_folder:
                logging.debug("Cancelled Output folder selection")
                break

            if (output_folder in FOLDER_LIST) or (output_folder.lower() == input_folder.lower()) or (Path(output_folder) in Path(input_folder).parents):
                logging.warning("You cant overwrite your input folder with your own output")
                res = tkinter.messagebox.askokcancel(title="Folder already selected", message="You've already selected this folder, or one of it's sub-folders as your INPUT folder, you can't overwrite a folder in-place.\nPlease choose another location")
                if res != True:
                    logging.debug("Cancelling folder selection")
                    return_result = False
                    break
                else:
                    logging.debug("NOT Cancelling folder selection")
                    continue
            return_result = True
        
        if tkinter.messagebox.askquestion(title="Add another folder?", message="Would you like to add another Input/Output Folder pairing?") != 'yes': 
            break
        else:
            FOLDER_LIST[input_folder] = output_folder
            logging.info(f"{input_folder} has been added via message box, it's output folder is {output_folder}")
    
    if return_result == True:
        FOLDER_LIST[input_folder] = output_folder
        logging.info(f"{input_folder} has been added, it's output folder is {output_folder}")
        Update_Labels()
    return return_result

    
def save_session_settings():
    global FOLDER_LIST
    with open("last runtime settings.json", "w") as LRS:
        LRS.write(json.dumps({"FOLDER LIST" : FOLDER_LIST, "IMAGE TO PIXEL TOOL LOCATION" : str(IMAGE_TO_PIXEL_TOOL_PATH), "PRESET LIST" : PRESET_LIST}))
    logging.info("Settings from this runtime have been saved")
    
    
def add_new_preset() -> bool:
    global PRESET_LIST

    preset_name = ""
    while True:
        preset_name = tkinter.simpledialog.askstring("New Preset Name", prompt="What would you like to name this Preset?")
        if not preset_name:
            logging.info("No name entered, aborting")
            return False
        elif preset_name in PRESET_LIST:
            res = tkinter.messagebox.askokcancel(title="Name already exists", message=f"Preset must have a unique name, {preset_name} already exists.\nWould you like to enter a new name?")
            if res == False:
                logging.info("Chose to abort instead of enter new name")
                return False
        else:
            break

    preset_path = tkinter.filedialog.askopenfilename(title="Which preset is ours?", filetypes=[("JSON preset files", ".json")])
    
    if not preset_path:
        logging.warning(f"Preset file location for {preset_name} never specified")
        return False

    palette_URL = ""
    palette_URL = tkinter.simpledialog.askstring("Palette URL", prompt="If you got this palette online, What is the URL for it?")
    
    make_active = tkinter.messagebox.askyesno(title="Make active preset", message="Would you like to make this preset the active preset?") if len(PRESET_LIST.keys()) > 0 else True
    if make_active:
        for preset in PRESET_LIST:
            PRESET_LIST[preset]["Active"] = False
            
    PRESET_LIST[preset_name] = {"Path" : preset_path, "URL" : palette_URL, "Active" : make_active}
    
    logging.info(f"Successfully added {preset_name}\nDetails are: {PRESET_LIST[preset_name]}")
    logging.info(f"Presets are now {PRESET_LIST}")
    Update_Labels()
    return True


def convert_image_bg_to_transparent(file_path, output_path, tolerance, target_colour):
    logging.info(f"Converting {file_path} background to become transparent, \nReplacement file will be at {output_path}")
    img = Image.open(file_path).convert("RGBA")
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if all(abs(x - y) <= tolerance for x, y in zip((r, g, b), target_colour)):
                pixels[x, y] = (0, 0, 0, 0)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)


def convert_folder_bg_to_transparent(input_folder, output_folder, tolerance = 10, convert_based_on_colour_RGB = (0, 128, 128)):
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith(".png"):
                in_path = os.path.join(root, filename)
                relative_path = os.path.relpath(in_path, input_folder)
                out_path = os.path.join(output_folder, relative_path)
                convert_image_bg_to_transparent(in_path, out_path, tolerance, convert_based_on_colour_RGB)


def get_img_to_pxl_tool_path(force_dialog = False) -> bool:
    global IMAGE_TO_PIXEL_TOOL_PATH
    global FIRST_TIME_RUNNING
    logging.debug(f"Running find Img2Pix, path is currently {IMAGE_TO_PIXEL_TOOL_PATH}")
    
    if IMAGE_TO_PIXEL_TOOL_PATH.exists() and IMAGE_TO_PIXEL_TOOL_PATH.is_file() and IMAGE_TO_PIXEL_TOOL_PATH.suffix == (".exe" or ".sh") and force_dialog != True:
        logging.info(f"Tool is already found, it's at {IMAGE_TO_PIXEL_TOOL_PATH}")
        res = True
    
    elif Path("SLK_img2pix_cmd.exe").exists() and force_dialog != True: 
        IMAGE_TO_PIXEL_TOOL_PATH = Path("SLK_img2pix_cmd.exe")
        logging.info(f"WE FOUND THE TOOL, it's now {IMAGE_TO_PIXEL_TOOL_PATH}")
        res = True
    
    else: 
        selection = filedialog.askopenfilename(title="Please select the location of the image to pixel tool", filetypes=[("Executable file", "exe")])
        if selection:
            IMAGE_TO_PIXEL_TOOL_PATH = Path(selection)
        logging.info(f"Tool path has been set to {IMAGE_TO_PIXEL_TOOL_PATH}")
        res = IMAGE_TO_PIXEL_TOOL_PATH.exists() and IMAGE_TO_PIXEL_TOOL_PATH.is_file() and IMAGE_TO_PIXEL_TOOL_PATH != "."
    logging.info(f"res is {res} because PATH.exists = {IMAGE_TO_PIXEL_TOOL_PATH.exists()} and PATH.is_file = {IMAGE_TO_PIXEL_TOOL_PATH.is_file()} and not \".\" = {IMAGE_TO_PIXEL_TOOL_PATH != "."}")

    FIRST_TIME_RUNNING = False
    Update_Labels()
    return res


def download_pixel_tool():
    webbrowser.open_new_tab("https://captain4lk.itch.io/slk-img2pixel")
    

def convert_image_to_palette(input_file : Path, output_path : Path, Presets_dict, Tool_Path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    active_preset = "FAILURE"
    
    logging.debug(f"Presets are {Presets_dict}\tAND Tool path is {Tool_Path}")
    for preset in Presets_dict:
        if Presets_dict[preset]["Active"]:
            active_preset = preset
    logging.debug(f"PRESET_LIST[{Presets_dict}][\"Path\"] is {Presets_dict[active_preset]["Path"]}")
    preset_file_path = Path(Presets_dict[active_preset]["Path"])
    
    logging.info(f"Converting {input_file} to {output_path} using {active_preset} ({preset_file_path})")
    subprocess.call([Tool_Path, "--in", input_file, "--out", output_path, "--preset", preset_file_path])


def convert_folder_to_palette(input_folder, output_folder, Preset_Dict, Tool_Path):
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith(".png"):
                in_path = os.path.join(root, filename)
                relative_path = os.path.relpath(in_path, input_folder)
                out_path = os.path.join(output_folder, relative_path)
                convert_image_to_palette(in_path, out_path, Preset_Dict, Tool_Path)


def remove_folder():
    new_root = tkinter.Toplevel()
    new_root.grab_set()
    tkinter.Label(master=new_root, text="Please select which Input/Output folder pair you'd like to delete").pack()
    for pair in FOLDER_LIST:
        tkinter.Button(master=new_root, text=pair, command=lambda p=pair: [FOLDER_LIST.pop(p), Update_Labels(), new_root.destroy()]).pack()


def preset_selection_window():
    new_root = tkinter.Toplevel()
    new_root.grab_set()
    tkinter.Label(master=new_root, text="Please select which preset you'd like to make the active one").pack()
    for preset in PRESET_LIST:
        tkinter.Button(master=new_root, text=preset, command=lambda: [clear_all_except(preset), Update_Labels(), new_root.destroy()]).pack()


def clear_all_except(exception : str):
    for preset in PRESET_LIST:
        if preset != exception:
            logging.info(f"{preset} is no longer active")
            PRESET_LIST[preset]["Active"] = False
        else:
            PRESET_LIST[preset]["Active"] = True
            logging.info(f"{preset} is now active")



def Menu():
    global Img_to_Pix_label
    global All_Folders_Label_I
    global All_Folders_Label_O
    global All_Presets_Label
    
    root = ThemedTk(theme="clam")
    style =  ttk.Style(root)
    style.theme_use('clam')  
    root.set_theme("clam", toplevel=True, themebg=False)
    try: 
        root.iconbitmap("BatchConverter.ico")
        root.wm_iconbitmap("BatchConverter.ico")
    except Exception as E:
        logging.error(f"Setting the App Icon failed because {repr(E)}")
    
    root.title("Projekt 43 Texture Palette Converter")
    Img_to_Pix_label = tkinter.Label(master=root, 
                                     text=f"Image to Pixel path: {IMAGE_TO_PIXEL_TOOL_PATH}",
                                     height=5)
    All_Folders_Label_I = tkinter.Label(master=root, text=f"Input folders:", foreground="dark green")
    All_Folders_Label_O = tkinter.Label(master=root, text=f"Output folders:", foreground="red3")
    All_Presets_Label = tkinter.Label(master=root, text=f"No Presets have been selected", foreground="red" )
    
    
    Find_Pixel_Tool_btn = tkinter.Button(master=root, text="Find Img 2 Pix Tool", command=lambda : get_img_to_pxl_tool_path(force_dialog=(not FIRST_TIME_RUNNING)))
    Download_Pixel_Tool_btn = tkinter.Button(master=root, text="Download Img 2 Pix Tool", command=lambda : download_pixel_tool())
    Add_folder_to_convert_btn = tkinter.Button(master=root, text="Add Folder folder to convert", foreground="dark green", command=lambda : add_folder())
    DEL_folder_to_convert_btn = tkinter.Button(master=root, text="Remove Folder folder from list", foreground="red3", command=lambda : remove_folder())
    Add_new_preset_btn = tkinter.Button(master=root, text="Add new Img 2 Pix .JSON Preset", command=lambda: add_new_preset())    
    Choose_active_preset_btn = tkinter.Button(master=root, text="Select Active Preset", command=lambda: preset_selection_window())
    start_convert_background_btn = tkinter.Button(master=root, text="Make Textures Background transparent",background="salmon", command=lambda: bg_conversion_dialog())
    start_batch_convert_btn = tkinter.Button(master=root, text="Start Batch Converting Folders", background="yellow3", command=lambda: start_batch_convert_to_palette())    
    
    
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1, pad=5)
    root.rowconfigure(4, weight=1, pad=5)
    root.rowconfigure(5, weight=1, pad=5)
    root.rowconfigure(6, weight=1, pad=5)
    root.columnconfigure(0, weight=1 , minsize=300)
    root.columnconfigure(1, weight=1 , minsize=300)
    
    
    Img_to_Pix_label.grid(row=0, columnspan=2, sticky="EW")
    All_Folders_Label_I.grid(row=1, column=0 , sticky="EW")
    All_Folders_Label_O.grid(row=1, column=1, sticky="EW")
    All_Presets_Label.grid(row=2, columnspan=2, sticky="EW")
    
    Find_Pixel_Tool_btn.grid(row=3, column=0, padx=8)
    Download_Pixel_Tool_btn.grid(row=3, column=1, padx=8)
    
    Add_folder_to_convert_btn.grid(row=4, column=0, padx=8)
    DEL_folder_to_convert_btn.grid(row=4, column=1, padx=8)
    
    Add_new_preset_btn.grid(row=5, column=0, padx=8)
    Choose_active_preset_btn.grid(row=5, column=1, padx=8)
    
    start_convert_background_btn.grid(row=6, column=0, padx=8)
    start_batch_convert_btn.grid(row=6, column=1, padx=8)
    
    Update_Labels()
    root.mainloop()



if __name__ == '__main__':
    TryGetLastSessionSettings()

    
    def start_batch_convert_to_palette() -> bool:
        if (IMAGE_TO_PIXEL_TOOL_PATH.exists() and IMAGE_TO_PIXEL_TOOL_PATH.is_file() and IMAGE_TO_PIXEL_TOOL_PATH != ".") == False:
            cancel = tkinter.messagebox.showwarning(title="No Tool selected", message="You Need to select the location of your Image to Pixel tool")
            if cancel:
                return False
            
        if len(FOLDER_LIST.keys()) <= 0:
            cancel = tkinter.messagebox.showwarning("No Folders selected", message="You Need to select Which folders you want to convert")
            if cancel:
                return False
        
        chosen_preset = GetActivePreset()
        
        if not chosen_preset:
            cancel = tkinter.messagebox.showwarning("No Preset selected", message="You Need to select Which preset you want to use")
            if cancel:
                return False
        
        cancel = tkinter.messagebox.askokcancel("Proceed", message="Are you sure you want to proceed?\nThis could take 1-20 minutes")
        if cancel == False:
            return False

        logging.warning(f"STARTING THE PALETTE CONVERSION WITH: {FOLDER_LIST}")
        for pair in FOLDER_LIST:
            logging.info(f"Starting Multiprocess with {pair} to {FOLDER_LIST[pair]}")
            ALL_MY_DAEMONS_PALETTE.append(multiprocessing.Process(target=convert_folder_to_palette, args=(pair, FOLDER_LIST[pair], PRESET_LIST, IMAGE_TO_PIXEL_TOOL_PATH)))
        for DEMON in ALL_MY_DAEMONS_PALETTE:
            DEMON.start()
        for DEMON in ALL_MY_DAEMONS_PALETTE:
            DEMON.join()
        tkinter.messagebox.showinfo("All done!", "Check terminal for any error messages")
        ALL_MY_DAEMONS_PALETTE.clear()
   
      
    def start_convert_folder_bg_to_transparent(chosen_colour, tolerance):
        global FOLDER_LIST
        proceed = tkinter.messagebox.askokcancel("Proceed?", "This operation will likely take a long time.\nAre you sure you'd like to proceed?")
        if proceed == False:
            return
        logging.info(f"Start Background conversion with {tolerance}, with RGB ({chosen_colour})")
        
        for pair in FOLDER_LIST:
            logging.info(f"Starting Multiprocess TextureBG Conversion with {pair} to {FOLDER_LIST[pair]}")
            ALL_MY_DAEMONS_BG.append(multiprocessing.Process(target=convert_folder_bg_to_transparent, args=(pair, FOLDER_LIST[pair], tolerance, chosen_colour )))
        for DEMON in ALL_MY_DAEMONS_BG:
            DEMON.start()
        for DEMON in ALL_MY_DAEMONS_BG:
            DEMON.join()
        logging.info(f"All folders had their Textures BG converted")
        ALL_MY_DAEMONS_BG.clear()
        tkinter.messagebox.showinfo("All done", "Task didn't fail unsuccessfully")
     
        
    def bg_conversion_dialog():
        global FOLDER_LIST
        new_root = tkinter.Toplevel()
        new_root.grab_set()
        
        tkinter.Label(master=new_root, text=f"All {len(FOLDER_LIST)} targeted folders will have their backgrounds changed to 0% Alpha").grid(row=0)
        
        chosen_colour_hex = "#4287f5"
        chosen_colour_rgb = (0,0,0)
        
        tkinter.Label(master=new_root, text ="Target Colour").grid(row=1, column=0)
        colour_btn = tkinter.Button(master=new_root, text="Pick Colour", background=chosen_colour_hex, command=lambda: set_colour())
        colour_btn.grid(row=1, column=1)
        
        def set_colour():
            nonlocal chosen_colour_hex, chosen_colour_rgb, colour_btn
            
            chosen_colour = tkinter.colorchooser.askcolor(initialcolor=chosen_colour_hex)
            chosen_colour_hex = chosen_colour[1]
            chosen_colour_rgb = chosen_colour[0]
            logging.info(f"New chosen colour is {chosen_colour}\n[0] is {chosen_colour[0]}, [1] is {chosen_colour[1]}")
            colour_btn.config(background=chosen_colour[1])

        
        tolerance = tkinter.IntVar()
        tkinter.Label(master=new_root, text="Tolerance").grid(row=2, column=0)
        tkinter.Entry(master=new_root, textvariable=tolerance).grid(row=2, column=1)
        
        tkinter.Button(master=new_root, text="Start converting Textures", command=lambda: [start_convert_folder_bg_to_transparent(chosen_colour_rgb, tolerance.get()), new_root.destroy()]).grid(row=3)
        
          
    Menu()
    logging.info("Exiting")

save_session_settings()