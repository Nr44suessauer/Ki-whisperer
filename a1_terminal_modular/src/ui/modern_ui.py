"""Moderne UI Setup für A1 Terminal"""

import customtkinter as ctk

def setup_modern_ui(app):
    """
    Erstellt das moderne, resizable UI-Layout
    
    Layout-Struktur:
    ┌─────────────────────────────────────────────────┐
    │  ┌───────────┬───────────────────────────────┐  │
    │  │  Session  │        Chat Area             │  │
    │  │  Panel    │  ┌────────────────────────┐  │  │
    │  │ (Models  │  │  Chat Messages         │  │  │
    │  │  +       │  │  (Scrollable)          │  │  │
    │  │ Sessions) │  └────────────────────────┘  │  │
    │  │           │  ┌────────────────────────┐  │  │
    │  │           │  │  Input Box             │  │  │
    │  │           │  └────────────────────────┘  │  │
    │  └───────────┴───────────────────────────────┘  │
    └─────────────────────────────────────────────────┘
    """
    
    from src.ui.resizable_pane import ResizablePane
    from src.ui.model_selector import ModelSelector
    
    # Main Container
    main_container = ctk.CTkFrame(app.root, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Horizontales ResizablePane (Session-Panel | Chat)
    horizontal_pane = ResizablePane(main_container, orient="horizontal")
    horizontal_pane.pack(fill="both", expand=True)
    
    # ==================== LEFT PANEL: Session Management ====================
    left_panel = ctk.CTkFrame(horizontal_pane, fg_color="#1a1a1a", corner_radius=10)
    
    # Model Selector (oben)
    app.model_selector = ModelSelector(
        left_panel,
        on_model_select=app.on_model_select,
        on_model_download=app.download_model_by_name,
        on_model_delete=app.delete_selected_model,
        on_refresh=app.refresh_models
    )
    app.model_selector.pack(fill="x", padx=5, pady=5)
    
    # Session List Header
    session_header = ctk.CTkFrame(left_panel, fg_color="transparent")
    session_header.pack(fill="x", padx=10, pady=(10, 5))
    
    session_title = ctk.CTkLabel(
        session_header,
        text="💬 Sessions",
        font=("Arial", 14, "bold"),
        anchor="w"
    )
    session_title.pack(side="left", fill="x", expand=True)
    
    new_session_btn = ctk.CTkButton(
        session_header,
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
    app.session_list_frame = ctk.CTkScrollableFrame(
        left_panel,
        fg_color="#0f0f0f",
        corner_radius=8
    )
    app.session_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Current Session BIAS (unten)
    bias_frame = ctk.CTkFrame(left_panel, fg_color="#2b2b2b", corner_radius=8)
    bias_frame.pack(fill="x", padx=10, pady=(5, 10))
    
    bias_label = ctk.CTkLabel(
        bias_frame,
        text="🎯 Session BIAS",
        font=("Arial", 11, "bold")
    )
    bias_label.pack(anchor="w", padx=10, pady=(10, 5))
    
    app.session_bias_entry = ctk.CTkTextbox(
        bias_frame,
        height=80,
        font=("Arial", 9),
        corner_radius=6
    )
    app.session_bias_entry.pack(fill="x", padx=10, pady=(0, 10))
    app.session_bias_entry.bind("<KeyRelease>", app.on_bias_text_changed)
    
    # ==================== RIGHT PANEL: Chat Area ====================
    right_panel = ctk.CTkFrame(horizontal_pane, fg_color="#1a1a1a", corner_radius=10)
    
    # Chat Header mit Tabs
    chat_header = ctk.CTkFrame(right_panel, fg_color="#2b2b2b", corner_radius=8, height=50)
    chat_header.pack(fill="x", padx=5, pady=5)
    chat_header.pack_propagate(False)
    
    # Tab-Buttons
    tab_frame = ctk.CTkFrame(chat_header, fg_color="transparent")
    tab_frame.pack(fill="both", expand=True, padx=10, pady=8)
    
    app.chat_tab_btn = ctk.CTkButton(
        tab_frame,
        text="💬 Chat",
        command=lambda: app.switch_tab("chat"),
        fg_color="#1f538d",
        hover_color="#2563a8",
        corner_radius=6,
        font=("Arial", 11, "bold"),
        width=100
    )
    app.chat_tab_btn.pack(side="left", padx=2)
    
    app.export_tab_btn = ctk.CTkButton(
        tab_frame,
        text="📤 Export",
        command=lambda: app.switch_tab("export"),
        fg_color="#3a3a3a",
        hover_color="#4a4a4a",
        corner_radius=6,
        font=("Arial", 11, "bold"),
        width=100
    )
    app.export_tab_btn.pack(side="left", padx=2)
    
    app.config_tab_btn = ctk.CTkButton(
        tab_frame,
        text="⚙️ Config",
        command=lambda: app.switch_tab("config"),
        fg_color="#3a3a3a",
        hover_color="#4a4a4a",
        corner_radius=6,
        font=("Arial", 11, "bold"),
        width=100
    )
    app.config_tab_btn.pack(side="left", padx=2)
    
    # Tab Content Container
    app.tab_content = ctk.CTkFrame(right_panel, fg_color="transparent")
    app.tab_content.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    # ==================== CHAT TAB ====================
    app.chat_tab_frame = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    
    # Chat Display (Scrollable) mit farbiger Umrandung für aktive Session
    app.chat_display_frame = ctk.CTkScrollableFrame(
        app.chat_tab_frame,
        fg_color="#0f0f0f",
        corner_radius=8,
        border_width=3,
        border_color="#4A4A4A"  # Standard-Gray, is being bei Session-Wechsel aktualisiert
    )
    app.chat_display_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Input Area
    input_container = ctk.CTkFrame(app.chat_tab_frame, fg_color="#2b2b2b", corner_radius=8, height=80)
    input_container.pack(fill="x", padx=5, pady=5)
    input_container.pack_propagate(False)
    
    input_frame = ctk.CTkFrame(input_container, fg_color="transparent")
    input_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.message_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="💬 Message eingeben...",
        font=("Arial", 12),
        corner_radius=6,
        height=40
    )
    app.message_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
    app.message_entry.bind("<Return>", app.send_message)
    app.message_entry.bind("<Up>", app.navigate_history_up)
    app.message_entry.bind("<Down>", app.navigate_history_down)
    
    # Button Container
    btn_container = ctk.CTkFrame(input_frame, fg_color="transparent")
    btn_container.pack(side="right")
    
    app.send_btn = ctk.CTkButton(
        btn_container,
        text="🚀",
        command=app.send_message,
        width=50,
        height=40,
        fg_color="#2B8A3E",
        hover_color="#37A24B",
        corner_radius=6,
        font=("Arial", 16, "bold")
    )
    app.send_btn.pack(side="left", padx=2)
    
    app.stop_btn = ctk.CTkButton(
        btn_container,
        text="⏹️",
        command=app.stop_generation,
        width=50,
        height=40,
        fg_color="#722F37",
        hover_color="#8B3A47",
        corner_radius=6,
        font=("Arial", 16, "bold"),
        state="disabled"
    )
    app.stop_btn.pack(side="left", padx=2)
    
    # ==================== EXPORT TAB ====================
    app.export_tab_frame = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    _setup_export_tab(app, app.export_tab_frame)
    
    # ==================== CONFIG TAB ====================
    app.config_tab_frame = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    _setup_config_tab(app, app.config_tab_frame)
    
    # Add panels to resizable pane
    horizontal_pane.add(left_panel, weight=1, minsize=300)
    horizontal_pane.add(right_panel, weight=3, minsize=500)
    
    # Show initial tab
    app.current_tab = "chat"
    app.chat_tab_frame.pack(fill="both", expand=True)
    
    # Initialize
    app.chat_bubbles = []
    
    return main_container


def _setup_export_tab(app, parent):
    """Setup Export Tab"""
    
    scroll = ctk.CTkScrollableFrame(parent, fg_color="#0f0f0f", corner_radius=8)
    scroll.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Title
    title = ctk.CTkLabel(
        scroll,
        text="📤 Session Export",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=20)
    
    # Export Options
    options_frame = ctk.CTkFrame(scroll, fg_color="#2b2b2b", corner_radius=10)
    options_frame.pack(fill="x", padx=20, pady=10)
    
    # Markdown Export
    md_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
    md_frame.pack(fill="x", padx=15, pady=15)
    
    md_icon = ctk.CTkLabel(md_frame, text="📝", font=("Arial", 24))
    md_icon.pack(side="left", padx=10)
    
    md_info = ctk.CTkFrame(md_frame, fg_color="transparent")
    md_info.pack(side="left", fill="x", expand=True, padx=10)
    
    ctk.CTkLabel(md_info, text="Markdown Export", font=("Arial", 14, "bold"), anchor="w").pack(anchor="w")
    ctk.CTkLabel(md_info, text="Exportiert Session als formatierte .md File", 
                font=("Arial", 10), text_color="#888888", anchor="w").pack(anchor="w")
    
    md_btn = ctk.CTkButton(
        md_frame,
        text="Exportieren",
        command=app.export_session_markdown,
        width=120,
        fg_color="#2B8A3E",
        hover_color="#37A24B"
    )
    md_btn.pack(side="right", padx=10)
    
    # JSON Export
    json_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
    json_frame.pack(fill="x", padx=15, pady=15)
    
    json_icon = ctk.CTkLabel(json_frame, text="📊", font=("Arial", 24))
    json_icon.pack(side="left", padx=10)
    
    json_info = ctk.CTkFrame(json_frame, fg_color="transparent")
    json_info.pack(side="left", fill="x", expand=True, padx=10)
    
    ctk.CTkLabel(json_info, text="JSON Export", font=("Arial", 14, "bold"), anchor="w").pack(anchor="w")
    ctk.CTkLabel(json_info, text="Complete data export incl. metadata", 
                font=("Arial", 10), text_color="#888888", anchor="w").pack(anchor="w")
    
    json_btn = ctk.CTkButton(
        json_frame,
        text="Exportieren",
        command=app.export_session_json,
        width=120,
        fg_color="#1f538d",
        hover_color="#2563a8"
    )
    json_btn.pack(side="right", padx=10)


def _setup_config_tab(app, parent):
    """Setup Config Tab"""
    
    scroll = ctk.CTkScrollableFrame(parent, fg_color="#0f0f0f", corner_radius=8)
    scroll.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Title
    title = ctk.CTkLabel(
        scroll,
        text="⚙️ Einstellungen",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=20)
    
    # Colors Section
    colors_frame = ctk.CTkFrame(scroll, fg_color="#2b2b2b", corner_radius=10)
    colors_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(colors_frame, text="🎨 Farben", font=("Arial", 14, "bold")).pack(pady=15)
    
    # Simple color inputs for now - can be enhanced later
    info_label = ctk.CTkLabel(
        colors_frame,
        text="Color configuration via Config tab available in old version.\nModern theme is being used.",
        font=("Arial", 10),
        text_color="#888888"
    )
    info_label.pack(pady=20)
    
    # Buttons
    btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    reset_btn = ctk.CTkButton(
        btn_frame,
        text="🔄 Standard wiederherstellen",
        command=app.reset_config,
        width=200,
        fg_color="#722F37",
        hover_color="#8B3A47"
    )
    reset_btn.pack()
