"""ColorWheel Widget für Farbauswahl"""

import tkinter as tk
from tkinter import Canvas
import math

class ColorWheel(tk.Frame):
    """Ein interaktiver Farbkreis für die Farbauswahl"""
    
    def __init__(self, master, size=200, initial_color="#1f538d", **kwargs):
        super().__init__(master, bg='#212121', **kwargs)
        
        self.size = size
        self.radius = size // 2 - 10
        self.center = size // 2
        self.selected_color = initial_color
        self.callback = None
        
        # Canvas für Farbkreis
        self.canvas = Canvas(self, width=size, height=size, bg='#212121', highlightthickness=0)
        self.canvas.pack()
        
        self.marker = None
        
        # Zeichne Farbkreis
        for angle in range(0, 360, 5):
            start_angle = angle
            end_angle = angle + 5
            for r in range(20, self.radius, 2):
                # HSV zu RGB für jeden Punkt
                saturation = (r - 20) / (self.radius - 20)
                rgb = self.hsv_to_rgb(angle, saturation, 1.0)
                color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                
                # Berechne Koordinaten
                x1 = self.center + (r-1) * math.cos(math.radians(start_angle))
                y1 = self.center + (r-1) * math.sin(math.radians(start_angle))
                x2 = self.center + r * math.cos(math.radians(end_angle))
                y2 = self.center + r * math.sin(math.radians(end_angle))
                
                self.canvas.create_line(
                    self.center, self.center, x2, y2,
                    fill=color, width=2

        )
        
        # Text in der Mitte
        self.canvas.create_text(
            self.center, self.center,
            text="White", fill="gray", font=("Arial", 9)
        )
    
    def hsv_to_rgb(self, h, s, v):
        """Konvertiert HSV zu RGB"""
        h = h / 360.0
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c
        
        if 0 <= h < 1/6:
            r, g, b = c, x, 0
        elif 1/6 <= h < 2/6:
            r, g, b = x, c, 0
        elif 2/6 <= h < 3/6:
            r, g, b = 0, c, x
        elif 3/6 <= h < 4/6:
            r, g, b = 0, x, c
        elif 4/6 <= h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
            
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    def rgb_to_hsv(self, r, g, b):
        """Konvertiert RGB zu HSV"""
        r, g, b = r/255.0, g/255.0, b/255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx-mn
        
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/df) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/df) + 120) % 360
        else:  # mx == b
            h = (60 * ((r-g)/df) + 240) % 360
            
        s = 0 if mx == 0 else df/mx
        v = mx
        
        return h, s, v
    
    def on_click(self, event):
        """Behandelt Mausklick auf Farbkreis"""
        self.update_color_from_position(event.x, event.y)
    
    def on_drag(self, event):
        """Behandelt Maus-Ziehen auf Farbkreis"""
        self.update_color_from_position(event.x, event.y)
    
    def update_color_from_position(self, x, y):
        """Aktualisiert Farbe basierend auf Position"""
        # Abstand vom Zentrum berechnen
        dx = x - self.center
        dy = y - self.center
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check ob im Farbkreis oder im weißen Zentrum
        if distance > self.radius:
            return
        
        # Whiteer Area in der Mitte
        if distance < 20:
            self.selected_color = "#FFFFFF"
            self.update_marker(self.center, self.center)
            if self.callback:
                self.callback("#FFFFFF")
            return
            
        # Winkel berechnen
        angle = math.degrees(math.atan2(dy, dx)) % 360
        
        # Saturation basierend auf Abstand
        if distance > self.radius - 20:
            saturation = 1.0
        else:
            saturation = max(0, (distance - 20) / (self.radius - 40))
        
        # RGB berechnen
        value = 1.0
        rgb = self.hsv_to_rgb(angle, saturation, value)
        color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        # Farbe refresh
        self.selected_color = color
        self.update_marker(x, y)
        
        # Callback aufrufen falls vorhanden
        if self.callback:
            self.callback(color)
    
    def update_marker(self, x, y):
        """Aktualisiert den Auswahl-Marker"""
        if self.marker:
            self.canvas.delete(self.marker)
            
        # Neuer Marker (Kreis mit Rand)
        self.marker = self.canvas.create_oval(
            x-6, y-6, x+6, y+6,
            fill=self.selected_color, 
            outline="white",
            width=2
        )
    
    def set_initial_position(self):
        """Setzt die initiale Position basierend auf der Startfarbe"""
        try:
            # Hex zu RGB
            hex_color = self.selected_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # RGB zu HSV
            h, s, v = self.rgb_to_hsv(r, g, b)
            
            # Position berechnen
            if s == 0:  # Graystufe - Zentrum
                x, y = self.center, self.center
            else:
                distance = 20 + s * (self.radius - 40)
                if s > 0.8:  # Äußerer Ring
                    distance = self.radius - 10
                    
                angle_rad = math.radians(h)
                x = self.center + distance * math.cos(angle_rad)
                y = self.center + distance * math.sin(angle_rad)
            
            self.update_marker(x, y)
            
        except:
            # Fallback: Zentrum
            self.update_marker(self.center, self.center)
    
    def set_color_callback(self, callback):
        """Setzt eine Callback-Funktion für Farbänderungen"""
        self.callback = callback
    
    def get_color(self):
        """Gibt die aktuell ausgewählte Farbe back"""
        return self.selected_color