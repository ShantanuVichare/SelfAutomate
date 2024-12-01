import time

import mss
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk, Image

class ScreenTextTaskApp:
    def __init__(self, supported_commands, command_callback):
        self.master = tk.Tk()
        self.master.title("Screen Text Task")
        self.supported_commands = supported_commands
        self.command_callback = command_callback

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

        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
            self.image = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
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

        def get_command_callback(cmd_idx):
            def on_command_click():
                self.clear_widgets()
                self.master.title("Running...")
                self.master.geometry(f"300x0+{int(self.screen_width/2 - 300/2)}+{int(self.screen_height/2 - 0/2)}")
                self.master.update()
                self.command_callback(cmd_idx, cropped_image)
                # time.sleep(1)
                self.master.title("Saved to clipboard! 📋")
                self.master.update()
                time.sleep(1)
                self.master.destroy()
            return on_command_click
        
        for cmd_idx, command_text in enumerate(self.supported_commands):
            button = tk.Button(self.master, text=command_text, command=get_command_callback(cmd_idx))
            button.pack(pady=3)

        display_image = cropped_image.resize((display_image_width, display_image_height),resample=Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(display_image)
        panel = tk.Label(self.master, image=photo)
        panel.photo = photo
        panel.pack(side="top", fill="none", expand="yes")

