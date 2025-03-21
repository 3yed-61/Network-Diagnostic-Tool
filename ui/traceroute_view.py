import wx
from .modern_widgets import ModernPanel, ModernButton, ModernTextCtrl, ModernGauge, AppTheme
from .modern_widgets import NotificationBar

class TracerouteView(ModernPanel):
    """Panel for the Traceroute tab."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI elements."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Controls section
        controls_panel = ModernPanel(self)
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Target input section
        target_group = self._create_target_input(controls_panel)
        
        # Buttons
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_button = ModernButton(
            controls_panel, 
            label="Start Trace",
            size=(-1, 36)
        )
        
        self.cancel_button = ModernButton(
            controls_panel, 
            label="Cancel", 
            color=AppTheme.DANGER,
            size=(-1, 36)
        )
        self.cancel_button.Disable()  # Disabled initially
        
        buttons_sizer.Add(self.start_button, 0, wx.RIGHT, 5)
        buttons_sizer.Add(self.cancel_button, 0)
        
        # Add controls to the panel
        controls_sizer.Add(target_group, 1, wx.EXPAND | wx.RIGHT, 10)
        controls_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
        controls_panel.SetSizer(controls_sizer)
        
        # Progress section
        self.progress_gauge = ModernGauge(self, label="Trace Progress")
        
        # Notification area (initially hidden)
        self.notification_area = wx.Panel(self)
        self.notification_area.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.notification_area.Hide()
        
        # Results area
        results_label = wx.StaticText(self, label="Trace Route Results")
        results_label.SetFont(AppTheme.get_bold_font(11))
        
        self.results_text = ModernTextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        # Use a monospace font for better traceroute output display
        self.results_text.SetFont(
            wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )
        
        # Layout
        main_sizer.Add(controls_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.progress_gauge, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self.notification_area, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(results_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self.results_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        self.SetSizer(main_sizer)
            
    def _create_target_input(self, parent):
        """Create target input controls."""
        group_box = wx.StaticBox(parent, label="Trace Target")
        group_box.SetFont(AppTheme.get_bold_font(10))
        sizer = wx.StaticBoxSizer(group_box, wx.VERTICAL)
        
        # Controls
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        target_label = wx.StaticText(group_box, label="IP/Hostname:")
        self.target_input = wx.TextCtrl(group_box, size=(200, -1))
        
        # Max hops
        hops_label = wx.StaticText(group_box, label="Max Hops:")
        self.max_hops = wx.SpinCtrl(group_box, value="30", min=1, max=64, size=(60, -1))
        
        input_sizer.Add(target_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        input_sizer.Add(self.target_input, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        input_sizer.Add(hops_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        input_sizer.Add(self.max_hops, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # Help text
        help_text = wx.StaticText(
            group_box, 
            label="Enter an IP address or hostname to trace the network route."
        )
        help_text.SetFont(AppTheme.get_font(8))
        help_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(help_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        return sizer
        
    def get_target(self):
        """Get the target IP or hostname."""
        return self.target_input.GetValue().strip()
        
    def get_max_hops(self):
        """Get the maximum hops value."""
        return self.max_hops.GetValue()
        
    def clear_results(self):
        """Clear the results area."""
        self.results_text.Clear()
        self.progress_gauge.SetValue(0)
        self.hide_notifications()
        
    def update_trace_output(self, line):
        """Update the trace route output."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_update_trace_output, line)
        else:
            self._safe_update_trace_output(line)
            
    def _safe_update_trace_output(self, line):
        """Thread-safe implementation of update_trace_output."""
        try:
            self.results_text.AppendText(line)
            
            # Auto-scroll to the bottom
            self.results_text.ShowPosition(self.results_text.GetLastPosition())
            
            # Highlight high latency lines with color
            if "ms" in line:
                try:
                    latencies = [int(val.strip()) for val in line.split() if val.strip().isdigit()]
                    if latencies and max(latencies) > 100:
                        # Mark high latency lines
                        pos = self.results_text.GetLastPosition()
                        line_start = self.results_text.GetValue().rfind('\n', 0, pos-1) + 1
                        
                        self.results_text.SetStyle(
                            line_start, pos,
                            wx.TextAttr(AppTheme.WARNING)
                        )
                except (ValueError, IndexError):
                    pass
        except Exception as e:
            import logging
            logging.error(f"Error updating trace output: {e}")
        
    def show_notification(self, message, style="info"):
        """Show a notification message."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_show_notification, message, style)
        else:
            self._safe_show_notification(message, style)
            
    def _safe_show_notification(self, message, style="info"):
        """Thread-safe implementation of show_notification."""
        try:
            # Clear any existing notifications
            self.notification_area.GetSizer().Clear(True)
            
            # Create a new notification
            notification = NotificationBar(self.notification_area, message, style)
            self.notification_area.GetSizer().Add(notification, 0, wx.EXPAND)
            
            self.notification_area.Show()
            self.Layout()
        except Exception as e:
            import logging
            logging.error(f"Error showing notification: {e}")
        
    def hide_notifications(self):
        """Hide all notifications."""
        self.notification_area.Hide()
        self.Layout()
        
    def set_controls_state(self, is_running):
        """Set the state of controls based on whether a trace is running."""
        self.start_button.Enable(not is_running)
        self.cancel_button.Enable(is_running)
        self.target_input.Enable(not is_running)
        self.max_hops.Enable(not is_running)
        
        if is_running:
            self.progress_gauge.Pulse()
        else:
            self.progress_gauge.SetValue(0) 