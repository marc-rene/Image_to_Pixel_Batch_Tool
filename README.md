# Projekt 43 Image to Pixel Batch Tool

A Windows-based GUI utility written in Python that batch-processes `.png` texture files. 
It does 2 things:
- Converts a folder of image backgrounds to be transparent based on a selected RGB colour & tolerance.
- Applies a pixel art palette to a folder of images using [SLK img2pixel by Lukas Holzbeierlein](https://captain4lk.itch.io/slk-img2pixel)

This is all done via multiprocessing so that a large number of folders can be processed with adequete speed

---

## Features

- Batch processing of multiple folders of textures.
- GUI built with `Tkinter` and `ttkthemes` *(proper ttkthemes implementation coming soon)*.
- Background transparency removal based on selected colour and tolerance.
- Integration with **SLK_img2pix** by using`.json` palette presets for any number of textures.
- Session settings are saved across launches.
- Fully multi-threaded batch operations via `multiprocessing`.



## Requirements

 - Ensure Python 3.8+ is installed.

- Pip packages: **ttkthemes**, **tkinter**, **Pillow**

- You **must** download  [SLK img2pixel](https://captain4lk.itch.io/slk-img2pixel) and make a .JSON preset with it:
Once you have it downloaded the batch tool can easily find it.

## How to Use

1.  **Get the required pip packages**  
````bash
pip install ttkthemes
pip install tkinter
pip install Pillow
````
    
2.  **Run the script and find the Img 2 Pixel tool**  
    - When running the script, a **tkinter** window should pop up. 
    - Select ***Find Img 2 Pix Tool*** and locate SLK_img2pix_cmd.exe
    
3.  **Add Folders**
    - Select ***Add Folder folder to convert***
    
    -   Add the folders with the `.png` files you want to process.
        
    -   You'll be immediately asked where you want to store the outputted images. You cannot overwrite the original folder. If you somehow did... please let me know because I put in a guard to stop specifically that
    - **NOTE**: All batch operations will allocate ONE Daemon per selected folder. 
    If you are selecting one HUGE folder, it might be an idea to add the subfolders instead as more Daemons will be allocated and time could be saved.
        
4.  **Add Palette Presets**
    -	Using the [SLK img2pixel](https://captain4lk.itch.io/slk-img2pixel) tool, you can create your own `.JSON` preset for how to convert an image. Make note of where you have saved it.
    -	Select ***Add new Img 2 Pix .JSON Preset*** and choose a name and the file path of the preset you've just saved. Extra optional information will be asked but you can safely ignore this.
    -   You will be asked if you want to make this new preset the **active** preset. This means that when you convert any images, they will use this new preset. You can choose which presets to make active later.
        
    -   Make sure one Preset is set as "active".
        
5.  **Converting Textures**
    - **Make Textures Background transparent** will open up a seperate dialog and will ask what colour you want to mark as the transparent colour going forward. 
    This will affect all chosen folders and sub-folders.
        
    -   **Start Batch Converting Folders** converts all images in the chosen folder(s) using the selected `.json` palette.


## Things to be aware about

-    **Overwriting files**: The tool prevents input/output folders from overlapping, but always back up your textures just in case.
    
-    **Folder structure** is preserved, but make sure you’ve chosen your paths carefully.
    
-   Multi-processing is used — don’t close the app while it's running.
    
-  Currently only `.png` files are processed. All others are ignored.


## Possible Improvements

-   Add drag-and-drop support for file/folder input.
-   Implement multi-folder select, only single folder select is working
    
-   Implement progress bars for batch jobs.
    
-   Support more formats (e.g., `.jpg`, `.bmp`).
    
-   Add CLI fallback for headless usage.
    
-   More robust error handling around subprocess failures.
- WAY more comments and testing... This was made during a coffee-induced binge

## Developer Notes

-   Main GUI logic is in `Menu()`
    
-   Session settings are saved in `last runtime settings.json`
    
-   Uses Pillow for image processing and multiprocessing for parallel execution.

## License

Feel free to use and modify this project. Just give credit if you publish or distribute it.
