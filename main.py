
import tkinter as tk
from tkinter import filedialog, simpledialog

import os
import time

# For file conversion
from moviepy.editor import VideoFileClip

from PIL import Image, ImageTk  # Import Image and ImageTk from PIL library
from io import BytesIO
import requests

#from tkhtmlview import HTMLLabel
import yt_dlp as youtube_dl

class FileConverter: # Handles file converting

    supported_files = [ # This includes the types of files that the programm can convert          
        ("All Supported Files", "*.png *.jpg *.jpeg *.gif *.bmp *.mp4 *.avi *.mov *.wmv *.mkv"), # All supported image and video formats
        ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"), # Image formats
        ("Video Files", "*.mp4 *.avi *.mov *.wmv *.mkv"), # Video formats
    ]

    def convert_image(self, file_path, new_type, app):
        # Ensure new_type does not include a leading dot and is in uppercase
        desired_type = new_type.split(".")[1].upper()

        # Get the directory of the original file
        directory_os = os.path.dirname(file_path)
        
        # Create a new file path with the desired type
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        new_file_path = os.path.join(directory_os, f"{base_name}.{desired_type.lower()}")

        try:
            # Open the image
            with Image.open(file_path) as img:
                if desired_type == 'JPEG' and img.mode in ('RGBA', 'LA'): # removing alpha transparency for jpegs
                    img = img.convert('RGB')
                
                print(f"Saving image as {desired_type} to {new_file_path}")
                img.save(new_file_path, format=desired_type)
                app.welcome_window()

            print(f"Image converted and saved as {new_file_path}")

        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        
        except IOError as e:
            print(f"IOError: {e}. Cannot convert or save the image.")
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def convert_video(self, file_path, new_type, app):
        try:
            # Extract the file name without extension and the current extension
            file_name, current_extension = os.path.splitext(file_path)
            
            # Ensure the new type starts with a dot (e.g., ".avi")
            new_type = new_type.split("*")[1]

            # Construct the output file path
            output_file = file_name + new_type

            # Load the video file
            video_clip = VideoFileClip(file_path)

            # Write the video to the new file with specified format
            video_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

            print(f"Video successfully converted and saved as {output_file}")
            app.welcome_window() # Returning to homepage
        
        except Exception as e:
            print(f"An error occurred: {e}")

class YoutubeDownloader: #Handles youtube downloading

    def get_vid(self, link):
    
        ydl_opts = {
            'quiet': True,  # Suppress output messages
            'noplaylist': True,  # Don't download playlists
            'skip_download': True,  # Only extract info, don't download
        }
            
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(link, download=False)
                return info_dict['title'], info_dict['thumbnail']
            except Exception as e:
                print(f"Error downloading video: {e}")
    
    def download_thumbnail(self, thumbnail_url): # Downloads the vid thumbnail so that it can be displayed to the user
        response = requests.get(thumbnail_url)
        image_data = BytesIO(response.content)

        return Image.open(image_data)

    def download_vid(self, link):

        download_dir = filedialog.askdirectory(title="Select Download Directory")

        if not download_dir:
            return False
        
        default_filename = 'video'
        filename = simpledialog.askstring("Input", "Enter filename (without extension):", initialvalue=default_filename)

        if filename is None:
            filename = default_filename
        
        filename = filename.replace('/', '_').replace('\\', '_')  # Ensures it doesnt contain invalid characters

        ydl_opts = {
            'format': 'best',  # Download the best quality
            'outtmpl': os.path.join(download_dir, f'{filename}.%(ext)s'),  
            'noplaylist': True,  # Don't download playlists
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([link])

                downloaded_file = os.path.join(download_dir, f'{filename}.{ydl.prepare_filename(ydl.extract_info(link, download=False)).split(".")[-1]}')
                
                current_time = time.time()
                os.utime(downloaded_file, (current_time, current_time)) # Fixes a bug where the file creation time was incorrect

                return True
            except Exception as e:
                print(f"Error downloading video: {e}")

class App:

    def __init__(self):

        self.root = None

        self.welc_window = None
        self.conv_window = None
        self.yt_window = None

        self.welcome_window() # Creates the welcome window when the app is first opened
    
    def welcome_window(self):  

        if self.welc_window is None: # Checking if the window class already exists
            self.welc_window = WelcomeWindow() # Creating the welcome window

        self.welc_window.load_ui(self.root, self)

    def convertion_window(self):

        if self.conv_window is None: # Checking if the window class already exists
            self.conv_window = ConversionWindow() # Creating the welcome window

        self.conv_window.load_ui(self.root, self)

    def youtube_window(self):   

        if self.yt_window is None: # Checking if the window class already exists
            self.yt_window = YoutubeWindow() # Creating the youtube window

        self.yt_window.load_ui(self.root, self)

    def get_img(self, name, sizeDimensions): # Returns the image object at its usable form

        image_path = os.path.join(os.path.join(os.path.dirname(__file__), "assets"), name)  
        img = Image.open(image_path)
        img = img.resize(sizeDimensions, Image.LANCZOS)  # Resize image to fit window
        background_image = ImageTk.PhotoImage(img)

        return background_image
    
    def set_root(self, target_class): # Sets the root to the one of the desired class
        self.root = target_class.root 

class WelcomeWindow:

    def load_ui(self, root, app):

        if root is not None:
            root.destroy() # Destroying the previous window if it existed

        self.root = tk.Tk()
        self.app = app

        self.app.set_root(self) # Sets the root of the app to the one of this window

        # Core window settings
        self.root.geometry("800x600")
        self.root.title("NT file tools")
        self.root.config(bg="black")
        self.root.resizable(False, False) # Makes the window not resizable

        # These 4 lines turn the background into an image
        bg_img = app.get_img("background.jpg", (800,600)) 
        background_label = tk.Label(self.root, image=bg_img)
        background_label.img = bg_img
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        main_frame = tk.Frame(self.root, bg="#0d0d0d") # Everything resides in this frame in order to be centred
        main_frame.pack(expand=True)

        title = tk.Label(main_frame, text="Welcome to NT file tools!", font=('Arial', 25), bg="#0d0d0d", fg="white")
        title.pack()

        options_label = tk.Label(main_frame, text="Please choose one of the following functions.", font=('Arial', 18), bg="#0d0d0d", fg="white")
        options_label.pack(pady=30)

        buttons_frame = tk.Frame(main_frame, bg="#0d0d0d")
        buttons_frame.pack(pady=10)

        converter_button = tk.Button(buttons_frame, text="Converter", font=('Arial', 18), bg="#0b21e3", fg="white", command=app.convertion_window)
        converter_button.pack(side=tk.LEFT, padx=10)

        yt_button = tk.Button(buttons_frame, text="Youtube", font=('Arial', 18), bg="#e30b0b", fg="white", command=app.youtube_window)
        yt_button.pack(side=tk.LEFT, padx=10)

        self.root.mainloop()

class ConversionWindow:

    def __init__(self):
        self.file_converter = FileConverter() # Setting up the file converter class

    def load_ui(self, root, app): # The ui that opens when the window is first loaded

        root.destroy() # Destroying the previous window if it existed

        self.root = tk.Tk()
        self.app = app
        self.app.set_root(self) # Sets the root of the app to the one of this window

        # Core window settings
        self.root.geometry("800x600")
        self.root.title("NT youtube downloader")
        self.root.config(bg="black")
        self.root.resizable(False, False) # Makes the window not resizable

        # These 4 lines turn the background into an image
        bg_img = app.get_img("background.jpg", (800,600)) 
        background_label = tk.Label(self.root, image=bg_img)
        background_label.img = bg_img
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        main_frame = tk.Frame(self.root, bg="#292929")
        main_frame.pack(expand=True)

        self.title_label = tk.Label(main_frame, text="Please select a file to convert", font=('Arial', 22), bg="#292929", fg="white", wraplength=700)
        self.title_label.pack(pady=10)

        buttons_frame = tk.Frame(main_frame, bg="#292929")
        buttons_frame.pack(pady=20)

        self.selection_button = tk.Button(buttons_frame, text="Select", font=('Arial', 22), bg="#0b21e3", fg="white", command=self.select_file)
        self.selection_button.pack(side=tk.LEFT, padx=10)

        self.decline_button = tk.Button(buttons_frame, text="Cancel", font=('Arial', 22), bg="#a3051a", fg="white", command=self.app.welcome_window)
        self.decline_button.pack(side=tk.LEFT ,padx=10)

        self.root.mainloop()

    def select_file(self): # Selects which file the user wants to convert
        
        file_path = filedialog.askopenfilename(
            title="Please select a file to convert",  
            filetypes=self.file_converter.supported_files
        )

        if file_path: # Checking if the user selected a file
            
            file_name_with_extension = os.path.basename(file_path) # Gets the name of the file but with the extension too
            file_name, file_extension = os.path.splitext(file_name_with_extension) # Seperates the extension from the name of the file

            self.title_label.config(text=f"Please select into which file type you want to convert {file_name_with_extension}.")
            self.selection_button.config(text="Confirm", bg="#0a7806", command=lambda: self.select_type(file_path, file_name, file_extension))
            self.decline_button.config(command=lambda: self.load_ui(self.root, self.app))

    def select_type(self, file_path, file_name, file_extension): # Selects in what type the user wants to convert the file
        
        isImage = None # This will help us know what file type we have later on
        title_text = None # This will be set to the text of the grid header later on
        file_types = None # The list of the file types that will later be looped through

        # Get the list of supported file types for images and videos
        image_file_types = self.file_converter.supported_files[1][1].split()
        video_file_types = self.file_converter.supported_files[2][1].split()
        file_ext_trans = "*" + file_extension # Adding a * to the start of the extension so that it is the same type as the ones in the lists

        if (file_ext_trans) in image_file_types: # Checking if the file type is an image

            file_types = image_file_types
            file_types.remove(file_ext_trans)

            if file_ext_trans != "*.jpg": # checking if it hasnt already been removed
                file_types.remove("*.jpg") # Removing jpg as jpeg already exists
            else:
                file_types.remove("*.jpeg") # Removing jpeg since file is a jpg

            isImage = True
            title_text = "Image types"
        elif (file_ext_trans) in video_file_types: # Checking if the file type is a video

            file_types = video_file_types
            file_types.remove(file_ext_trans)
            isImage = False 
            title_text = "Video types"
        else: # The program has failed

            self.app.welcome_window() # Going back to the homepage
            return None

        self.root.destroy() # Destroying the previous window
        self.root = tk.Tk()
        self.app.set_root(self) # Sets the root of the app to the one of this window

        # Core window settings
        self.root.geometry("600x600")
        self.root.title("NT youtube downloader")
        self.root.config(bg="black")
        self.root.resizable(False, False) # Makes the window not resizable

        # These 4 lines turn the background into an image
        bg_img = self.app.get_img("background.jpg", (800,600)) 
        background_label = tk.Label(self.root, image=bg_img)
        background_label.img = bg_img
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        main_frame = tk.Frame(self.root, bg="#292929")
        main_frame.pack(expand=True)

        header_label = tk.Label(main_frame, text=title_text, font=('Arial', 18, 'bold'), bg="#292929", fg="white")
        header_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        for i,file_type in enumerate(file_types):

            file_button = tk.Button(main_frame, text=file_type, font=('Arial', 18, 'bold'), bg="#4c4d4c", fg="white", command=lambda file_type=file_type:self.convert_ui(file_path, file_name, file_extension, file_type, isImage))
            file_button.grid(row=(i + 1), column=1, padx=10, pady=5, sticky="ew")

    def convert_ui(self, file_path, file_name, file_type_old, file_type_new, IsImage): # The ui that has the user confirm what file he wants to convert and in which type

        self.root.destroy() # Destroying the previous window
        self.root = tk.Tk()
        self.app.set_root(self) # Sets the root of the app to the one of this window

        convert_function = None

        # Deciding which convert method to use based on if the file is an image or not
        if IsImage == True:
            convert_function = self.file_converter.convert_image
        else:
            convert_function = self.file_converter.convert_video

        # Core window settings
        self.root.geometry("800x600")
        self.root.title("NT youtube downloader")
        self.root.config(bg="black")
        self.root.resizable(False, False) # Makes the window not resizable

        # These 4 lines turn the background into an image
        bg_img = self.app.get_img("background.jpg", (800,600)) 
        background_label = tk.Label(self.root, image=bg_img)
        background_label.img = bg_img
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        main_frame = tk.Frame(self.root, bg="#292929")
        main_frame.pack(expand=True)

        title_text = f'Are you sure you want to convert the {file_name+file_type_old} into a {file_type_new}?'
        title_label = tk.Label(main_frame, text=title_text, font=('Arial', 22), bg="#4c4d4c", fg="white", wraplength=700)
        title_label.pack(pady=10)

        buttons_frame = tk.Frame(main_frame, bg="#292929") # This frame will contain the Yes and No buttons
        buttons_frame.pack(pady=20)

        accept_button = tk.Button(buttons_frame, text="Yes", font=('Arial', 22), bg="#048526", fg="white", command=lambda: convert_function(file_path, file_type_new, self.app))
        accept_button.pack(side=tk.LEFT, padx=10)

        decline_button = tk.Button(buttons_frame, text="No", font=('Arial', 22), bg="#a3051a", fg="white", command=self.app.welcome_window)
        decline_button.pack(side=tk.LEFT, padx=10)

class YoutubeWindow:

    def __init__(self):
        self.yt_dl = YoutubeDownloader() # Setting up the youtube downloader class

    def load_ui(self, root, app):
                 
        root.destroy() # Destroying the previous window if it existed

        self.root = tk.Tk()
        self.app = app
        self.app.set_root(self) # Sets the root of the app to the one of this window

        # Core window settings
        self.root.geometry("800x600")
        self.root.title("NT youtube downloader")
        self.root.config(bg="black")
        self.root.resizable(False, False) # Makes the window not resizable

        # These 4 lines turn the background into an image
        bg_img = app.get_img("background.jpg", (800,600)) 
        background_label = tk.Label(self.root, image=bg_img)
        background_label.img = bg_img
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.main_frame = tk.Frame(self.root, bg='#0d0d0d') # Everything will be stored in here
        self.main_frame.pack(expand=True, fill='x')

        self.title = tk.Label(self.main_frame, text="Please enter your link below", font=('Arial', 22), bg="#292929", fg="white")
        self.title.pack()

        video_img = app.get_img("vid_placeholder.jpg", (414, 232)) 
        self.video_label = tk.Label(self.main_frame, width=320, height=180, image=video_img) # this will show the youtube video image placeholder
        self.video_label.img = video_img
        self.video_label.pack(pady=10)

        self.video_entry = tk.Entry(self.main_frame, font=('Arial', 22), width=700, justify='center', bg="#171717", fg="white")
        self.video_entry.pack(pady=10)

        self.buttons_frame = tk.Frame(self.main_frame, bg="#0d0d0d") # This frame will contain the confirm/download and cancel button
        self.buttons_frame.pack(pady=10)

        self.confirm_button = tk.Button(self.buttons_frame, text="Confirm", font=('Arial', 22), bg="#026302", fg="white", command=self.onConfirm)
        self.confirm_button.pack(side=tk.LEFT, padx=10)

        self.cancel_button = tk.Button(self.buttons_frame, text="Exit", font=('Arial', 22), bg="#c9040e", fg="white", command=app.welcome_window)
        self.cancel_button.pack(side=tk.LEFT, padx=10) # Making the cancel button visible

        self.root.mainloop()

    def download(self, yt_dl, yt_link): # Runs when the user clicks the download button

        video = None 

        self.root.withdraw() # Hiding the root until the user selects where the vid should be downloaded
        video = yt_dl.download_vid(yt_link)

        if video is True:
            print("Download finished successfully.")
            self.app.youtube_window() #resetting the window
        else:
            print("Download failed.")
            self.load_ui(self.root, self.app)  # Restart the app         

    def onConfirm(self): # Runs when the user enters a link and presses confirm    

        yt_link = self.video_entry.get()
        print(yt_link)
        video_title, thumbnail_url = self.yt_dl.get_vid(yt_link) 

        if video_title is not None and thumbnail_url: #checks if the link is valid
            
            thumbnail = self.yt_dl.download_thumbnail(thumbnail_url)

            thumbnail = thumbnail.resize((320, 180), Image.LANCZOS)
            thumbnail_img = ImageTk.PhotoImage(thumbnail)

            self.video_label.config(image=thumbnail_img) # Assigning the thumbnail image to the placeholder
            self.video_label.img = thumbnail_img

            self.title.config(text=video_title) 
            self.confirm_button.config(text="Download", bg="#0310a1", command=lambda: self.download(self.yt_dl, yt_link))
            self.cancel_button.config(text="Cancel", command=lambda: self.load_ui(self.root, self.app))

def main():
    myApp = App()

if __name__ == "__main__":
    main()