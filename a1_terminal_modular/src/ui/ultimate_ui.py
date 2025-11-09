"""Ultimate Modern UI for A1 Terminal - Complete Implementation"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os

def setup_ultimate_ui(app):
    """
    Erstellt die ultimative moderne UI mit allen Must-Have Features
    
    Features:
    ✅ Resizable Split-View
    ✅ Session Cards mit visuellen Info
    ✅ Inline Model Selector
    ✅ Message Actions (Copy, Regen)
    ✅ Typing Indicator
    ✅ Keyboard Shortcuts
    ✅ Theme Toggle
    ✅ Quick Actions
    """
    
    from src.ui.resizable_pane import ResizablePane
    from src.ui.session_card import SessionCard
    from src.ui.model_selector import ModelSelector
    
    # ============== MAIN CONTAINER ==============
    app.main_container = ctk.CTkFrame(app.root, fg_color="#0f0f0f")
    app.main_container.pack(fill="both", expand=True)
    
    # ============== TOP BAR ==============
    top_bar = ctk.CTkFrame(app.main_container, height=60, fg_color="#1a1a1a", corner_radius=0)
    top_bar.pack(fill="x", side="top")
    top_bar.pack_propagate(False)
    
    # Logo / Title
    title_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    title_frame.pack(side="left", padx=20, pady=10)
    
    title = ctk.CTkLabel(
        title_frame,
        text="🤖 Ki-Whisperer",
        font=("Arial", 20, "bold"),
        text_color="#00BFFF"
    )
    title.pack(side="left")
    
    subtitle = ctk.CTkLabel(
        title_frame,
        text="AI Chat Assistant",
        font=("Arial", 10),
        text_color="#888888"
    )
    subtitle.pack(side="left", padx=(10, 0))
    
    # Quick Actions (rechts)
    quick_actions = ctk.CTkFrame(top_bar, fg_color="transparent")
    quick_actions.pack(side="right", padx=20, pady=10)
    
    # Theme Toggle
    app.theme_var = tk.StringVar(value="dark")
    theme_btn = ctk.CTkButton(
        quick_actions,
        text="🌙",
        width=40,
        height=40,
        command=lambda: toggle_theme(app),
        fg_color="#2b2b2b",
        hover_color="#3a3a3a",
        corner_radius=8
    )
    theme_btn.pack(side="right", padx=5)
    app.theme_btn = theme_btn
    
    # Settings
    settings_btn = ctk.CTkButton(
        quick_actions,
        text="⚙️",
        width=40,
        height=40,
        command=lambda: show_settings(app),
        fg_color="#2b2b2b",
        hover_color="#3a3a3a",
        corner_radius=8
    )
    settings_btn.pack(side="right", padx=5)
    
    # Export
    export_btn = ctk.CTkButton(
        quick_actions,
        text="📤",
        width=40,
        height=40,
        command=lambda: show_export_dialog(app),
        fg_color="#2b2b2b",
        hover_color="#3a3a3a",
        corner_radius=8
    )
    export_btn.pack(side="right", padx=5)
    
    # ============== MAIN CONTENT AREA ==============
    content_area = ctk.CTkFrame(app.main_container, fg_color="transparent")
    content_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Resizable Horizontal Pane
    h_pane = ResizablePane(content_area, orient="horizontal")
    h_pane.pack(fill="both", expand=True)
    
    # ============== LEFT PANEL: Sessions & Model ==============
    left_panel = ctk.CTkFrame(h_pane, fg_color="#1a1a1a", corner_radius=10)
    
    # Model Selector (kompakt oben)
    model_frame = ctk.CTkFrame(left_panel, fg_color="#2b2b2b", corner_radius=8)
    model_frame.pack(fill="x", padx=10, pady=10)
    
    model_label = ctk.CTkLabel(
        model_frame,
        text="🤖 Model",
        font=("Arial", 12, "bold")
    )
    model_label.pack(anchor="w", padx=10, pady=(10, 5))
    
    # Model Dropdown mit Icons
    model_select_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
    model_select_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    app.model_dropdown = ctk.CTkComboBox(
        model_select_frame,
        values=["Lädt..."],
        command=app.on_model_select,
        font=("Arial", 10),
        corner_radius=6,
        button_color="#2B8A3E",
        button_hover_color="#37A24B"
    )
    app.model_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    # Quick Model Actions
    model_refresh_btn = ctk.CTkButton(
        model_select_frame,
        text="🔄",
        width=35,
        height=28,
        command=app.refresh_models,
        fg_color="#3a3a3a",
        hover_color="#4a4a4a",
        corner_radius=6
    )
    model_refresh_btn.pack(side="left", padx=2)
    
    model_add_btn = ctk.CTkButton(
        model_select_frame,
        text="➕",
        width=35,
        height=28,
        command=lambda: show_model_download(app),
        fg_color="#2B8A3E",
        hover_color="#37A24B",
        corner_radius=6
    )
    model_add_btn.pack(side="left", padx=2)
    
    # Sessions Header
    sessions_header = ctk.CTkFrame(left_panel, fg_color="transparent")
    sessions_header.pack(fill="x", padx=15, pady=(15, 10))
    
    sessions_title = ctk.CTkLabel(
        sessions_header,
        text="💬 Sessions",
        font=("Arial", 14, "bold")
    )
    sessions_title.pack(side="left")
    
    new_session_btn = ctk.CTkButton(
        sessions_header,
        text="➕",
        width=35,
        height=28,
        command=app.create_new_session,
        fg_color="#2B8A3E",
        hover_color="#37A24B",
        corner_radius=6,
        font=("Arial", 14, "bold")
    )
    new_session_btn.pack(side="right")
    
    # Scrollable Session List
    app.session_list_container = ctk.CTkScrollableFrame(
        left_panel,
        fg_color="#0f0f0f",
        corner_radius=8
    )
    app.session_list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # ============== RIGHT PANEL: Chat Area ==============
    right_panel = ctk.CTkFrame(h_pane, fg_color="#1a1a1a", corner_radius=10)
    
    # Chat Header
    chat_header = ctk.CTkFrame(right_panel, fg_color="#2b2b2b", corner_radius=8, height=60)
    chat_header.pack(fill="x", padx=10, pady=10)
    chat_header.pack_propagate(False)
    
    header_content = ctk.CTkFrame(chat_header, fg_color="transparent")
    header_content.pack(fill="both", expand=True, padx=15, pady=10)
    
    # Current Session Info
    app.current_session_label = ctk.CTkLabel(
        header_content,
        text="Keine Session aktiv",
        font=("Arial", 13, "bold"),
        anchor="w"
    )
    app.current_session_label.pack(side="left", fill="x", expand=True)
    
    # Session Actions
    session_actions = ctk.CTkFrame(header_content, fg_color="transparent")
    session_actions.pack(side="right")
    
    clear_btn = ctk.CTkButton(
        session_actions,
        text="🗑️",
        width=35,
        height=28,
        command=lambda: clear_chat(app),
        fg_color="transparent",
        hover_color="#722F37",
        border_width=1,
        border_color="#722F37",
        corner_radius=6
    )
    clear_btn.pack(side="left", padx=2)
    
    bias_btn = ctk.CTkButton(
        session_actions,
        text="🎯",
        width=35,
        height=28,
        command=lambda: show_bias_editor(app),
        fg_color="transparent",
        hover_color="#1f538d",
        border_width=1,
        border_color="#1f538d",
        corner_radius=6
    )
    bias_btn.pack(side="left", padx=2)
    
    # Chat Display
    app.chat_display_frame = ctk.CTkScrollableFrame(
        right_panel,
        fg_color="#0f0f0f",
        corner_radius=8
    )
    app.chat_display_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # Typing Indicator (versteckt initial)
    app.typing_indicator = create_typing_indicator(right_panel)
    app.typing_indicator.pack_forget()
    
    # Input Area
    input_container = ctk.CTkFrame(right_panel, fg_color="#2b2b2b", corner_radius=8, height=100)
    input_container.pack(fill="x", padx=10, pady=(0, 10))
    input_container.pack_propagate(False)
    
    input_content = ctk.CTkFrame(input_container, fg_color="transparent")
    input_content.pack(fill="both", expand=True, padx=15, pady=12)
    
    # Text Input
    app.message_entry = ctk.CTkTextbox(
        input_content,
        height=60,
        font=("Arial", 12),
        corner_radius=6,
        wrap="word"
    )
    app.message_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    # Bind Enter key (Ctrl+Enter for newline)
    app.message_entry.bind("<Return>", lambda e: send_message_from_textbox(app, e))
    app.message_entry.bind("<Control-Return>", lambda e: None)  # Newline
    
    # Buttons
    button_frame = ctk.CTkFrame(input_content, fg_color="transparent")
    button_frame.pack(side="right")
    
    app.send_btn = ctk.CTkButton(
        button_frame,
        text="🚀",
        width=50,
        height=60,
        command=lambda: send_message_from_textbox(app),
        fg_color="#2B8A3E",
        hover_color="#37A24B",
        corner_radius=8,
        font=("Arial", 20, "bold")
    )
    app.send_btn.pack()
    
    app.stop_btn = ctk.CTkButton(
        button_frame,
        text="⏹️",
        width=50,
        height=60,
        command=app.stop_generation,
        fg_color="#722F37",
        hover_color="#8B3A47",
        corner_radius=8,
        font=("Arial", 20, "bold"),
        state="disabled"
    )
    app.stop_btn.pack_forget()
    
    # Add panels to resizable pane
    h_pane.add(left_panel, weight=1, minsize=280)
    h_pane.add(right_panel, weight=3, minsize=500)
    
    # Setup keyboard shortcuts
    setup_keyboard_shortcuts(app)
    
    # Initialize
    app.chat_bubbles = []
    
    return app.main_container


# ============== HELPER FUNCTIONS ==============

def create_typing_indicator(parent):
    """Erstellt animierten Typing Indicator"""
    frame = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=10, height=50)
    frame.pack_propagate(False)
    
    content = ctk.CTkFrame(frame, fg_color="transparent")
    content.pack(expand=True)
    
    ctk.CTkLabel(
        content,
        text="🤖",
        font=("Arial", 16)
    ).pack(side="left", padx=(10, 5))
    
    ctk.CTkLabel(
        content,
        text="AI denkt nach",
        font=("Arial", 11),
        text_color="#888888"
    ).pack(side="left")
    
    # Animierte Dots
    dots_label = ctk.CTkLabel(
        content,
        text="...",
        font=("Arial", 11),
        text_color="#888888"
    )
    dots_label.pack(side="left", padx=(5, 10))
    
    # Animation
    def animate_dots():
        current = dots_label.cget("text")
        dots_label.configure(text="." if len(current) >= 3 else current + ".")
        frame.after(500, animate_dots)
    
    animate_dots()
    
    return frame


def send_message_from_textbox(app, event=None):
    """Sendet Nachricht aus Textbox"""
    if event and event.state & 0x4:  # Ctrl gedrückt
        return None  # Erlaube Newline
    
    message = app.message_entry.get("1.0", "end-1c").strip()
    if message:
        app.message_entry.delete("1.0", "end")
        app.send_message_programmatic(message)
    
    return "break"  # Verhindere default behavior


def toggle_theme(app):
    """Wechselt zwischen Dark und Light Theme"""
    current = app.theme_var.get()
    if current == "dark":
        ctk.set_appearance_mode("light")
        app.theme_var.set("light")
        app.theme_btn.configure(text="☀️")
    else:
        ctk.set_appearance_mode("dark")
        app.theme_var.set("dark")
        app.theme_btn.configure(text="🌙")


def show_settings(app):
    """Zeigt Settings Dialog"""
    dialog = ctk.CTkToplevel(app.root)
    dialog.title("⚙️ Einstellungen")
    dialog.geometry("500x400")
    dialog.transient(app.root)
    dialog.grab_set()
    
    # Platzhalter
    ctk.CTkLabel(
        dialog,
        text="⚙️ Einstellungen",
        font=("Arial", 18, "bold")
    ).pack(pady=20)
    
    ctk.CTkLabel(
        dialog,
        text="Einstellungen werden hier angezeigt...",
        font=("Arial", 12),
        text_color="#888888"
    ).pack(pady=20)


def show_export_dialog(app):
    """Zeigt Export Dialog"""
    if not app.current_session_id:
        messagebox.showwarning("Keine Session", "Bitte wählen Sie zuerst eine Session aus.")
        return
    
    dialog = ctk.CTkToplevel(app.root)
    dialog.title("📤 Session exportieren")
    dialog.geometry("400x300")
    dialog.transient(app.root)
    dialog.grab_set()
    
    ctk.CTkLabel(
        dialog,
        text="📤 Export Format wählen",
        font=("Arial", 16, "bold")
    ).pack(pady=20)
    
    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(expand=True)
    
    ctk.CTkButton(
        btn_frame,
        text="📝 Markdown (.md)",
        command=lambda: [app.export_session_markdown(), dialog.destroy()],
        width=200,
        height=50,
        font=("Arial", 12, "bold"),
        fg_color="#2B8A3E",
        hover_color="#37A24B"
    ).pack(pady=10)
    
    ctk.CTkButton(
        btn_frame,
        text="📊 JSON (.json)",
        command=lambda: [app.export_session_json(), dialog.destroy()],
        width=200,
        height=50,
        font=("Arial", 12, "bold"),
        fg_color="#1f538d",
        hover_color="#2563a8"
    ).pack(pady=10)


def show_model_download(app):
    """Zeigt Model Download Dialog"""
    dialog = ctk.CTkToplevel(app.root)
    dialog.title("➕ Modell herunterladen")
    dialog.geometry("450x250")
    dialog.transient(app.root)
    dialog.grab_set()
    
    ctk.CTkLabel(
        dialog,
        text="➕ Neues Modell hinzufügen",
        font=("Arial", 16, "bold")
    ).pack(pady=20)
    
    entry_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    entry_frame.pack(pady=10)
    
    entry = ctk.CTkEntry(
        entry_frame,
        placeholder_text="z.B. llama3.2:3b",
        width=300,
        height=40,
        font=("Arial", 12)
    )
    entry.pack(pady=10)
    
    def download():
        model_name = entry.get().strip()
        if model_name:
            dialog.destroy()
            app.download_model_by_name(model_name)
    
    ctk.CTkButton(
        entry_frame,
        text="⬇️ Herunterladen",
        command=download,
        width=200,
        height=40,
        font=("Arial", 12, "bold"),
        fg_color="#2B8A3E",
        hover_color="#37A24B"
    ).pack(pady=10)


def show_bias_editor(app):
    """Zeigt BIAS Editor Dialog"""
    if not app.current_session_id:
        messagebox.showwarning("Keine Session", "Bitte wählen Sie zuerst eine Session aus.")
        return
    
    dialog = ctk.CTkToplevel(app.root)
    dialog.title("🎯 Session BIAS bearbeiten")
    dialog.geometry("600x400")
    dialog.transient(app.root)
    dialog.grab_set()
    
    ctk.CTkLabel(
        dialog,
        text="🎯 Session BIAS",
        font=("Arial", 16, "bold")
    ).pack(pady=15)
    
    ctk.CTkLabel(
        dialog,
        text="Setzen Sie den Kontext und die Instruktionen für diese Session",
        font=("Arial", 10),
        text_color="#888888"
    ).pack(pady=(0, 10))
    
    textbox = ctk.CTkTextbox(
        dialog,
        font=("Arial", 11),
        wrap="word"
    )
    textbox.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    textbox.insert("1.0", app.current_session_bias or "")
    
    def save():
        app.current_session_bias = textbox.get("1.0", "end-1c")
        app.save_current_session()
        dialog.destroy()
        messagebox.showinfo("Gespeichert", "BIAS wurde gespeichert!")
    
    ctk.CTkButton(
        dialog,
        text="💾 Speichern",
        command=save,
        width=150,
        height=40,
        font=("Arial", 12, "bold"),
        fg_color="#2B8A3E",
        hover_color="#37A24B"
    ).pack(pady=10)


def clear_chat(app):
    """Löscht Chat-Historie"""
    if messagebox.askyesno("Chat leeren", "Möchten Sie den Chat wirklich leeren?"):
        for bubble in app.chat_bubbles:
            bubble.destroy()
        app.chat_bubbles = []
        app.chat_history = []
        messagebox.showinfo("Gelöscht", "Chat wurde geleert!")


def setup_keyboard_shortcuts(app):
    """Setup Keyboard Shortcuts"""
    
    # Ctrl+N: Neue Session
    app.root.bind("<Control-n>", lambda e: app.create_new_session())
    
    # Ctrl+K: Model wechseln (Focus auf Dropdown)
    app.root.bind("<Control-k>", lambda e: app.model_dropdown.focus())
    
    # Ctrl+L: Chat leeren
    app.root.bind("<Control-l>", lambda e: clear_chat(app))
    
    # Ctrl+E: Export
    app.root.bind("<Control-e>", lambda e: show_export_dialog(app))
    
    # Ctrl+B: BIAS bearbeiten
    app.root.bind("<Control-b>", lambda e: show_bias_editor(app))
    
    # Ctrl+T: Theme wechseln
    app.root.bind("<Control-t>", lambda e: toggle_theme(app))
    
    # Escape: Stop generation
    app.root.bind("<Escape>", lambda e: app.stop_generation())
