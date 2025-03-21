import wx
import webbrowser
import os
import logging
from .modern_widgets import ModernPanel, ModernButton, ModernHyperlinkCtrl, AppTheme
from .modern_widgets import IconTextButton

class AboutView(ModernPanel):
    """Panel for the About tab."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Application info
        self.app_version = "3.5"
        self.dev_name = "3λΞĐ"
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI elements."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # App info panel with title and version
        app_info_panel = self._create_app_info_panel()
        
        # Developer info panel
        dev_info_panel = self._create_developer_panel()
        
        # Features panel
        features_panel = self._create_features_panel()
        
        # License panel
        license_panel = self._create_license_panel()
        
        # Connect panel
        connect_panel = self._create_connect_panel()
        
        # Layout all components with some spacing
        main_sizer.Add(app_info_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(dev_info_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(features_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(license_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(connect_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Add some stretch space at the bottom
        main_sizer.AddStretchSpacer()
        
        self.SetSizer(main_sizer)
        
    def _create_app_info_panel(self):
        """Create the application info panel."""
        panel = ModernPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # App icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "icon.png")
            if os.path.exists(icon_path):
                app_icon = wx.Bitmap(icon_path)
                icon_scaled = app_icon.ConvertToImage().Scale(64, 64, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
                icon_ctrl = wx.StaticBitmap(panel, bitmap=icon_scaled)
                sizer.Add(icon_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        except Exception as e:
            # If icon loading fails, show nothing
            logging.warning(f"Could not load app icon: {e}")
        
        # App info text
        info_sizer = wx.BoxSizer(wx.VERTICAL)
        
        app_title = wx.StaticText(panel, label="Network Diagnostic Tool")
        app_title.SetFont(AppTheme.get_bold_font(18))
        app_title.SetForegroundColour(AppTheme.PRIMARY)
        
        version_text = wx.StaticText(panel, label=f"Version {self.app_version}")
        version_text.SetFont(AppTheme.get_font(10))
        version_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        description = wx.StaticText(
            panel, 
            label="A comprehensive network diagnostics and analysis tool"
        )
        description.SetFont(AppTheme.get_font())
        
        info_sizer.Add(app_title, 0, wx.BOTTOM, 5)
        info_sizer.Add(version_text, 0, wx.BOTTOM, 10)
        info_sizer.Add(description, 0)
        
        sizer.Add(info_sizer, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        panel.SetSizer(sizer)
        
        return panel
        
    def _create_developer_panel(self):
        """Create the developer info panel."""
        panel = ModernPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Developer avatar
        try:
            avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "avatar.png")
            if os.path.exists(avatar_path):
                avatar = wx.Bitmap(avatar_path)
                avatar_scaled = avatar.ConvertToImage().Scale(48, 48, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
                avatar_ctrl = wx.StaticBitmap(panel, bitmap=avatar_scaled)
                sizer.Add(avatar_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        except Exception as e:
            # If avatar loading fails, show nothing
            logging.warning(f"Could not load avatar: {e}")
        
        # Developer info
        dev_sizer = wx.BoxSizer(wx.VERTICAL)
        
        dev_title = wx.StaticText(panel, label="Developer")
        dev_title.SetFont(AppTheme.get_bold_font(12))
        
        dev_name = wx.StaticText(panel, label=self.dev_name)
        dev_name.SetFont(AppTheme.get_font())
        
        dev_sizer.Add(dev_title, 0, wx.BOTTOM, 5)
        dev_sizer.Add(dev_name, 0)
        
        sizer.Add(dev_sizer, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        panel.SetSizer(sizer)
        
        return panel
        
    def _create_features_panel(self):
        """Create the features info panel."""
        panel = ModernPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Features title
        features_title = wx.StaticText(panel, label="Key Features")
        features_title.SetFont(AppTheme.get_bold_font(12))
        sizer.Add(features_title, 0, wx.ALL, 10)
        
        # Features list
        features = [
            "✓ Ping test with packet loss and latency analysis",
            "✓ Visual trace route with network path analysis",
            "✓ Comprehensive network information display",
            "✓ Internet speed testing with performance assessment",
            "✓ Modern, user-friendly interface"
        ]
        
        feature_sizer = wx.BoxSizer(wx.VERTICAL)
        for feature in features:
            feature_text = wx.StaticText(panel, label=feature)
            feature_text.SetFont(AppTheme.get_font())
            feature_sizer.Add(feature_text, 0, wx.BOTTOM, 5)
            
        sizer.Add(feature_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        
        return panel
        
    def _create_license_panel(self):
        """Create the license info panel."""
        panel = ModernPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # License title
        license_title = wx.StaticText(panel, label="License")
        license_title.SetFont(AppTheme.get_bold_font(12))
        
        # License text
        license_text = wx.StaticText(
            panel,
            label="This software is provided under the MIT License. "
                  "You are free to use, modify, and distribute this software "
                  "for personal or commercial use."
        )
        license_text.Wrap(600)  # Wrap text at 600 pixels
        license_text.SetFont(AppTheme.get_font(9))
        
        sizer.Add(license_title, 0, wx.ALL, 10)
        sizer.Add(license_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        
        return panel
        
    def _create_connect_panel(self):
        """Create the connect/social panel."""
        panel = ModernPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Connect title
        connect_title = wx.StaticText(panel, label="Connect")
        connect_title.SetFont(AppTheme.get_bold_font(12))
        sizer.Add(connect_title, 0, wx.ALL, 10)
        
        # Social buttons
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        github_button = ModernButton(panel, label="GitHub", size=(120, -1))
        github_button.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://github.com/3yed-61"))
        
        telegram_button = ModernButton(
            panel, 
            label="Telegram", 
            size=(120, -1),
            color=AppTheme.SECONDARY
        )
        telegram_button.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://t.me/talk_to_3yed_bot"))
        
        buttons_sizer.Add(github_button, 0, wx.RIGHT, 10)
        buttons_sizer.Add(telegram_button, 0)
        
        sizer.Add(buttons_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel.SetSizer(sizer)
        
        return panel 