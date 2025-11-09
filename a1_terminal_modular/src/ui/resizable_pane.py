"""Resizable Pane Widget für flexible Layouts"""

import customtkinter as ctk
import tkinter as tk

class ResizablePane(ctk.CTkFrame):
    """Ein Panel das mit einem Draggable-Divider die Größe ändern kann"""
    
    def __init__(self, master, orient="horizontal", sash_width=4, **kwargs):
        super().__init__(master, **kwargs)
        
        self.orient = orient  # "horizontal" oder "vertical"
        self.sash_width = sash_width
        self.panes = []
        self.sashes = []
        self.dragging_sash = None
        self.drag_start_pos = None
        self.last_sizes = {}  # Speichert letzte bekannte Größen
        
        # Grid-Konfiguration
        if orient == "horizontal":
            self.grid_rowconfigure(0, weight=1)
        else:
            self.grid_columnconfigure(0, weight=1)
        
        # Bind window resize events
        self.bind("<Configure>", self._on_configure)
    
    def _on_configure(self, event):
        """Handle window resize/maximize events"""
        # Update after layout is stable
        self.after(10, self._update_pane_sizes)
    
    def _update_pane_sizes(self):
        """Update stored pane sizes"""
        try:
            for i, pane_info in enumerate(self.panes):
                widget = pane_info['widget']
                if self.orient == "horizontal":
                    size = widget.winfo_width()
                else:
                    size = widget.winfo_height()
                
                if size > 1:  # Valid size
                    pane_info['current_size'] = size
        except:
            pass
    
    def add(self, widget, weight=1, minsize=100):
        """Fügt ein Widget zum Pane hinzu"""
        pane_info = {
            'widget': widget,
            'weight': weight,
            'minsize': minsize,
            'current_size': None
        }
        
        pane_index = len(self.panes)
        self.panes.append(pane_info)
        
        # Widget platzieren
        if self.orient == "horizontal":
            widget.grid(row=0, column=pane_index * 2, sticky="nsew")
            self.grid_columnconfigure(pane_index * 2, weight=weight, minsize=minsize)
        else:
            widget.grid(row=pane_index * 2, column=0, sticky="nsew")
            self.grid_rowconfigure(pane_index * 2, weight=weight, minsize=minsize)
        
        # Sash (Divider) hinzufügen, wenn nicht das erste Pane
        if pane_index > 0:
            sash = self._create_sash(pane_index)
            self.sashes.append(sash)
    
    def _create_sash(self, pane_index):
        """Erstellt einen Divider (Sash) zwischen zwei Panes"""
        sash = ctk.CTkFrame(self, width=self.sash_width, height=self.sash_width, 
                           fg_color="#3a3a3a", corner_radius=0)
        
        if self.orient == "horizontal":
            sash.grid(row=0, column=(pane_index * 2) - 1, sticky="ns")
            self.grid_columnconfigure((pane_index * 2) - 1, weight=0, minsize=self.sash_width)
            cursor = "sb_h_double_arrow"
        else:
            sash.grid(row=(pane_index * 2) - 1, column=0, sticky="ew")
            self.grid_rowconfigure((pane_index * 2) - 1, weight=0, minsize=self.sash_width)
            cursor = "sb_v_double_arrow"
        
        # Cursor und Hover-Effekt
        sash.configure(cursor=cursor)
        
        # Bind Events
        sash.bind("<Enter>", lambda e: sash.configure(fg_color="#4a4a4a"))
        sash.bind("<Leave>", lambda e: sash.configure(fg_color="#3a3a3a"))
        sash.bind("<Button-1>", lambda e: self._start_drag(e, pane_index, sash))
        sash.bind("<B1-Motion>", lambda e: self._on_drag(e, pane_index))
        sash.bind("<ButtonRelease-1>", lambda e: self._end_drag())
        
        return sash
    
    def _start_drag(self, event, pane_index, sash):
        """Start des Drag-Vorgangs"""
        self.dragging_sash = pane_index
        if self.orient == "horizontal":
            self.drag_start_pos = event.x_root
        else:
            self.drag_start_pos = event.y_root
        sash.configure(fg_color="#5a5a5a")
        
        # Force layout update and get current sizes
        self.update_idletasks()
        self._update_pane_sizes()
    
    def _on_drag(self, event, pane_index):
        """Während des Draggings"""
        if self.dragging_sash is None:
            return
        
        if self.orient == "horizontal":
            delta = event.x_root - self.drag_start_pos
            self._resize_panes_horizontal(pane_index, delta)
        else:
            delta = event.y_root - self.drag_start_pos
            self._resize_panes_vertical(pane_index, delta)
    
    def _end_drag(self):
        """Ende des Drag-Vorgangs"""
        if self.dragging_sash is not None and self.dragging_sash <= len(self.sashes):
            sash = self.sashes[self.dragging_sash - 1]
            sash.configure(fg_color="#3a3a3a")
        self.dragging_sash = None
        
        # Update sizes after drag
        self.after(100, self._update_pane_sizes)
    
    def _resize_panes_horizontal(self, pane_index, delta):
        """Ändert die Größe der Panes horizontal"""
        if abs(delta) < 3:  # Ignore very small movements
            return
            
        left_pane_idx = (pane_index - 1) * 2
        right_pane_idx = pane_index * 2
        
        left_pane = self.panes[pane_index - 1]
        right_pane = self.panes[pane_index]
        
        # Get current actual widths with update
        self.update_idletasks()
        left_width = left_pane['widget'].winfo_width()
        right_width = right_pane['widget'].winfo_width()
        
        # Fallback to stored sizes if winfo returns invalid
        if left_width < 10:
            left_width = left_pane.get('current_size', 280)
        if right_width < 10:
            right_width = right_pane.get('current_size', 500)
        
        # Calculate proposed new widths
        proposed_left = left_width + delta
        proposed_right = right_width - delta
        
        # Check constraints
        if proposed_left < left_pane['minsize']:
            proposed_left = left_pane['minsize']
            proposed_right = left_width + right_width - proposed_left
        
        if proposed_right < right_pane['minsize']:
            proposed_right = right_pane['minsize']
            proposed_left = left_width + right_width - proposed_right
        
        # Calculate weights as percentage
        total = proposed_left + proposed_right
        if total > 0:
            left_weight = max(1, int((proposed_left / total) * 1000))
            right_weight = max(1, int((proposed_right / total) * 1000))
            
            # Apply new weights
            self.grid_columnconfigure(left_pane_idx, weight=left_weight)
            self.grid_columnconfigure(right_pane_idx, weight=right_weight)
            
            # Store new sizes
            left_pane['current_size'] = proposed_left
            right_pane['current_size'] = proposed_right
    
    def _resize_panes_vertical(self, pane_index, delta):
        """Ändert die Größe der Panes vertikal"""
        if abs(delta) < 3:  # Ignore very small movements
            return
            
        top_pane_idx = (pane_index - 1) * 2
        bottom_pane_idx = pane_index * 2
        
        top_pane = self.panes[pane_index - 1]
        bottom_pane = self.panes[pane_index]
        
        # Get current actual heights with update
        self.update_idletasks()
        top_height = top_pane['widget'].winfo_height()
        bottom_height = bottom_pane['widget'].winfo_height()
        
        # Fallback to stored sizes if winfo returns invalid
        if top_height < 10:
            top_height = top_pane.get('current_size', 280)
        if bottom_height < 10:
            bottom_height = bottom_pane.get('current_size', 500)
        
        # Calculate proposed new heights
        proposed_top = top_height + delta
        proposed_bottom = bottom_height - delta
        
        # Check constraints
        if proposed_top < top_pane['minsize']:
            proposed_top = top_pane['minsize']
            proposed_bottom = top_height + bottom_height - proposed_top
        
        if proposed_bottom < bottom_pane['minsize']:
            proposed_bottom = bottom_pane['minsize']
            proposed_top = top_height + bottom_height - proposed_bottom
        
        # Calculate weights as percentage
        total = proposed_top + proposed_bottom
        if total > 0:
            top_weight = max(1, int((proposed_top / total) * 1000))
            bottom_weight = max(1, int((proposed_bottom / total) * 1000))
            
            # Apply new weights
            self.grid_rowconfigure(top_pane_idx, weight=top_weight)
            self.grid_rowconfigure(bottom_pane_idx, weight=bottom_weight)
            
            # Store new sizes
            top_pane['current_size'] = proposed_top
            bottom_pane['current_size'] = proposed_bottom
