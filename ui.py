from typing import List
import time

import tkinter as tk
from tkinter import Canvas, simpledialog
from PIL import ImageTk, Image

from utils import grab_screenshot
from ModelClients import COMMANDS, Command

import logger

class ScreenTextTaskApp:
    def __init__(self, supported_commands: List[str] = COMMANDS):
        self.master = tk.Tk()
        self.master.title("Screen Text Task")
        self.supported_commands = supported_commands

        self.screen_padding = 0.1
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        
        self.window_width = int(self.screen_width*(1-self.screen_padding))
        self.padding_width = int(self.screen_width*self.screen_padding/2)
        self.window_height = int(self.screen_height*(1-self.screen_padding))
        self.padding_height = int(self.screen_height*self.screen_padding/2)

        # Make the root window always on top
        self.master.wm_attributes("-topmost", True)
        # Turn off the window shadow
        # self.master.wm_attributes("-transparent", True)
        # Set the root window background color to a transparent color
        # self.master.config(bg='systemTransparent')
        
        self.master.focus_force()
        # Hide the root window drag bar and close button
        # self.master.overrideredirect(True)

        self.image = grab_screenshot()
        
        self.render_canvas_display()
        
    def mainloop(self):
        self.master.mainloop()

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()
    
    def render_canvas_display(self):
        self.clear_widgets()
        
        window_width = self.window_width
        window_height = self.window_height
        self.master.geometry(f"{window_width}x{window_height}+{self.padding_width}+{self.padding_height}")
        
        display_image = self.image.resize((window_width, window_height),resample=Image.Resampling.LANCZOS)
        self.canvas = Canvas(self.master, width=window_width, height=window_height)
        self.photo = ImageTk.PhotoImage(display_image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.canvas.pack()
        
        self.rect = None
        self.start_x = None
        self.start_y = None

        def on_button_press(event):
            self.start_x = event.x
            self.start_y = event.y
            if not self.rect:
                self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

        def on_move_press(event):
            if self.rect:
                self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        def on_button_release(event):
            x1, y1, x2, y2 = self.canvas.coords(self.rect)
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            if x2 - x1 < 10 or y2 - y1 < 10:
                self.render_prompt_window(self.image)
            else:
                x1 = int(x1 / window_width * self.image.width)
                x2 = int(x2 / window_width * self.image.width)
                y1 = int(y1 / window_height * self.image.height)
                y2 = int(y2 / window_height * self.image.height)
                cropped_image = self.image.crop((x1, y1, x2, y2))
                self.render_prompt_window(cropped_image)
        
        self.canvas.bind("<ButtonPress-1>", on_button_press)
        self.canvas.bind("<B1-Motion>", on_move_press)
        self.canvas.bind("<ButtonRelease-1>", on_button_release)
        
    
    def render_prompt_window(self, cropped_image):
        self.clear_widgets()

        display_image_width = int(cropped_image.width * (self.screen_width / self.image.width))
        display_image_height = int(cropped_image.height * (self.screen_height / self.image.height))
        
        window_width = max(min(int(display_image_width + 50), self.window_width), 300)
        window_height = min(int(display_image_height + 50), self.window_height) + len(self.supported_commands) * 50
        padding_width = int(self.screen_width/2 - window_width/2)
        padding_height = int(self.screen_height/2 - window_height/2)
        self.master.geometry(f"{window_width}x{window_height}+{padding_width}+{padding_height}")
        
        button = tk.Button(self.master, text="Retry Selection", command=self.render_canvas_display)
        button.pack(pady=3, padx=3)

        def get_model_command_callback(command: Command):
            def on_command_click():
                logger.log(f"Running ScreenTask: {command}")
                self.clear_widgets()
                self.master.title("Running...")
                self.master.geometry(f"300x0+{int(self.screen_width/2 - 300/2)}+{int(self.screen_height/2 - 0/2)}")
                self.master.update()
                try:
                    # Invoke the model command with the cropped image
                    command.invoke_with_image(cropped_image)
                except Exception as e:
                    logger.log_error(e, f"Error invoking command: {command.display_string}")
                    self.master.title(f"Error")
                    self.master.update()
                    time.sleep(2)
                    self.master.destroy()
                    raise e
                self.master.title("Saved to clipboard! 📋")
                self.master.update()
                time.sleep(1)
                self.master.destroy()
            return on_command_click
        
        for command in self.supported_commands:
            button = tk.Button(self.master, text=command, command=get_model_command_callback(command))
            button.pack(pady=3)

        display_image = cropped_image.resize((display_image_width, display_image_height),resample=Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(display_image)
        panel = tk.Label(self.master, image=photo)
        panel.photo = photo
        panel.pack(side="top", fill="none", expand="yes")

class GenericTaskApp:
    '''
    This class renders a UI with a key-value pair dictionary input.
    The dict has key (Display String) and value (callback).
    '''
    def __init__(self, tasks: dict):
        # Accept tasks as a dictionary: { display_text: callback }
        self.tasks = tasks
        self.master = tk.Tk()
        self.master.title("Generic Task")
        self.render_ui()
    
    def mainloop(self):
        self.master.mainloop()
    
    def render_ui(self):
        label = tk.Label(self.master, text="Select a Task")
        label.pack(pady=10)
        for display_text, callback in self.tasks.items():
            button = tk.Button(self.master, text=display_text, 
                               command=lambda cb=callback: self.on_task_selected(cb))
            button.pack(pady=5)
        cancel_btn = tk.Button(self.master, text="Cancel", command=self.master.destroy)
        cancel_btn.pack(pady=10)
    
    def on_task_selected(self, callback):
        self.master.destroy()
        callback()

    
class ForceStartDialog():

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        

    def confirm(self):
        user_input = simpledialog.askstring("Force Start?", None, parent=self.root)
        self.root.destroy()
        if user_input is None:
            return False
        return True
    
