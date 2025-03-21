import wx
import logging
import os
import subprocess
from .modern_widgets import ModernPanel, ModernButton, ModernTextCtrl, ModernGauge, AppTheme
from .modern_widgets import ResultCard, MetricCard

class SpeedTestView(ModernPanel):
    """Panel for the Speed Test tab."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Define available test servers with additional metadata
        self.test_servers = {
            "Automatic (Recommended)": {
                "url": "auto",
                "location": "Multiple Regions",
                "provider": "Various",
                "status": "unknown"
            },
            "Cloudflare (Global CDN)": {
                "url": "https://www.cloudflare.com",
                "location": "Global CDN",
                "provider": "Cloudflare",
                "status": "unknown"
            },
            "Google (Global CDN)": {
                "url": "https://www.google.com",
                "location": "Global CDN",
                "provider": "Google",
                "status": "unknown"
            },
            "Microsoft (Global CDN)": {
                "url": "https://www.microsoft.com",
                "location": "Global CDN",
                "provider": "Microsoft",
                "status": "unknown"
            },
            "AWS CloudFront (Global CDN)": {
                "url": "https://d1.awsstatic.com",
                "location": "Global CDN",
                "provider": "Amazon AWS",
                "status": "unknown"
            },
            "Fast.com (Netflix CDN)": {
                "url": "https://fast.com",
                "location": "Global CDN",
                "provider": "Netflix",
                "status": "unknown"
            },
            "Local Connection": {
                "url": "https://127.0.0.1",
                "location": "Local Network",
                "provider": "Your Router",
                "status": "unknown"
            }
        }
        
        self._create_ui()
        self._check_server_status()
        
    def _create_ui(self):
        """Create the UI elements."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header section
        header_panel = ModernPanel(self)
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(header_panel, label="Internet Speed Test")
        title.SetFont(AppTheme.get_bold_font(12))
        
        # Server selection section
        server_panel = ModernPanel(header_panel)
        server_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        server_label = wx.StaticText(server_panel, label="Test Server:")
        server_label.SetFont(AppTheme.get_font(10))
        
        # Create a combo box with server details
        self.server_choice = wx.ComboBox(
            server_panel,
            style=wx.CB_DROPDOWN | wx.CB_READONLY,
            choices=list(self.test_servers.keys())
        )
        self.server_choice.SetSelection(0)  # Set to "Automatic" by default
        self.server_choice.Bind(wx.EVT_COMBOBOX, self._on_server_selected)
        
        # Server info display
        self.server_info = wx.StaticText(server_panel, label="")
        self.server_info.SetFont(AppTheme.get_font(9))
        self.server_info.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        # Status indicator
        self.status_indicator = wx.StaticText(server_panel, label="●")
        self.status_indicator.SetFont(AppTheme.get_bold_font(12))
        self.status_indicator.SetForegroundColour(wx.Colour(128, 128, 128))  # Gray for unknown
        
        # Refresh button
        self.refresh_button = wx.Button(
            server_panel,
            label="↻",
            size=(28, 28)
        )
        self.refresh_button.SetToolTip("Refresh server status")
        self.refresh_button.Bind(wx.EVT_BUTTON, self.trigger_refresh)
        
        self.start_button = ModernButton(
            server_panel,
            label="Start Test",
            size=(-1, 32)
        )
        
        server_sizer.Add(server_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        server_sizer.Add(self.server_choice, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        server_sizer.Add(self.status_indicator, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        server_sizer.Add(self.server_info, 2, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        server_sizer.Add(self.refresh_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        server_sizer.Add(self.start_button, 0, wx.ALIGN_CENTER_VERTICAL)
        server_panel.SetSizer(server_sizer)
        
        header_sizer.Add(title, 0, wx.BOTTOM, 10)
        header_sizer.Add(server_panel, 0, wx.EXPAND)
        header_panel.SetSizer(header_sizer)
        
        # Progress section
        self.progress_panel = ModernPanel(self)
        progress_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.progress_gauge = ModernGauge(self.progress_panel, label="Speed Test Progress")
        self.status_text = wx.StaticText(self.progress_panel, label="Ready to test")
        self.status_text.SetFont(AppTheme.get_font(9))
        self.status_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        # Current speed display
        self.current_speed_text = wx.StaticText(self.progress_panel, label="")
        self.current_speed_text.SetFont(AppTheme.get_bold_font(10))
        self.current_speed_text.SetForegroundColour(AppTheme.PRIMARY)
        
        progress_sizer.Add(self.progress_gauge, 0, wx.EXPAND | wx.BOTTOM, 5)
        progress_sizer.Add(self.status_text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 3)
        progress_sizer.Add(self.current_speed_text, 0, wx.ALIGN_CENTER)
        self.progress_panel.SetSizer(progress_sizer)
        
        # Results section - cards for speed metrics
        self.results_panel = ModernPanel(self)
        results_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Download speed card
        self.download_card = MetricCard(
            self.results_panel,
            title="Download Speed",
            value="-- Mbps",
            color=AppTheme.PRIMARY
        )
        
        # Upload speed card
        self.upload_card = MetricCard(
            self.results_panel,
            title="Upload Speed",
            value="-- Mbps",
            color=AppTheme.ACCENT
        )
        
        # Ping card
        self.ping_card = MetricCard(
            self.results_panel,
            title="Ping Latency",
            value="-- ms",
            color=AppTheme.SECONDARY
        )
        
        results_sizer.Add(self.download_card, 1, wx.EXPAND | wx.RIGHT, 5)
        results_sizer.Add(self.upload_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        results_sizer.Add(self.ping_card, 1, wx.EXPAND | wx.LEFT, 5)
        self.results_panel.SetSizer(results_sizer)
        
        # Analysis card container
        self.analysis_container = ModernPanel(self)
        self.analysis_container.SetSizer(wx.BoxSizer(wx.VERTICAL))
        
        # Text log for detailed results
        log_label = wx.StaticText(self, label="Detailed Results")
        log_label.SetFont(AppTheme.get_bold_font(11))
        
        self.log_text = ModernTextCtrl(self)
        
        # Layout all components
        main_sizer.Add(header_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.progress_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        main_sizer.Add(self.results_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.analysis_container, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        main_sizer.Add(log_label, 0, wx.LEFT | wx.TOP, 10)
        main_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)
        
        self.SetSizer(main_sizer)
        
    def update_progress(self, value, status_message=None):
        """Update the progress gauge and status text."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_update_progress, value, status_message)
        else:
            self._safe_update_progress(value, status_message)
            
    def _safe_update_progress(self, value, status_message=None):
        """Thread-safe implementation of update_progress."""
        try:
            # Check if widgets still exist
            if not self or not self.progress_gauge or not self.status_text:
                return
                
            if not self.progress_gauge.IsBeingDeleted() and not self.status_text.IsBeingDeleted():
                self.progress_gauge.SetValue(value)
                
                if status_message:
                    # Check for specific messages and handle specially
                    if "No internet connection detected" in status_message:
                        self.status_text.SetLabel("⚠️ No internet connection detected")
                        self.status_text.SetForegroundColour(wx.Colour(200, 0, 0))  # Red
                        if hasattr(self, 'current_speed_text') and not self.current_speed_text.IsBeingDeleted():
                            self.current_speed_text.SetLabel("")
                    elif "Current:" in status_message:
                        # Split status message into main status and current speed
                        parts = status_message.split("Current:")
                        self.status_text.SetLabel(parts[0].strip())
                        self.status_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
                        
                        # Update current speed text if it exists
                        if hasattr(self, 'current_speed_text') and not self.current_speed_text.IsBeingDeleted():
                            self.current_speed_text.SetLabel(f"Current: {parts[1].strip()}")
                    else:
                        self.status_text.SetLabel(status_message)
                        self.status_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
                        
                        # Clear current speed text
                        if hasattr(self, 'current_speed_text') and not self.current_speed_text.IsBeingDeleted():
                            self.current_speed_text.SetLabel("")
        except Exception as e:
            logging.debug(f"Progress update skipped - widget may have been destroyed: {e}")
            
    def update_speed_results(self, download, upload, ping):
        """Update the speed test results."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_update_speed_results, download, upload, ping)
        else:
            self._safe_update_speed_results(download, upload, ping)
            
    def _safe_update_speed_results(self, download, upload, ping):
        """Thread-safe implementation of update_speed_results."""
        try:
            # Check if widgets still exist
            if not self or not self.download_card or not self.upload_card or not self.ping_card or not self.log_text:
                return
                
            # Update only if widgets are not being deleted
            if (not self.download_card.IsBeingDeleted() and 
                not self.upload_card.IsBeingDeleted() and 
                not self.ping_card.IsBeingDeleted() and 
                not self.log_text.IsBeingDeleted()):
                
                # Clear current speed display
                if hasattr(self, 'current_speed_text') and not self.current_speed_text.IsBeingDeleted():
                    self.current_speed_text.SetLabel("")
                
                # Update the metric cards
                if download is not None:
                    self.download_card.SetValue(f"{download:.2f} Mbps")
                else:
                    self.download_card.SetValue("Failed")
                    
                if upload is not None:
                    self.upload_card.SetValue(f"{upload:.2f} Mbps")
                else:
                    self.upload_card.SetValue("Failed")
                    
                if ping is not None:
                    self.ping_card.SetValue(f"{ping:.2f} ms")
                else:
                    self.ping_card.SetValue("Failed")
                
                # Add to the log text
                self.log_text.Clear()
                self.log_text.AppendText("Speed Test Results:\n\n")
                
                if download is not None:
                    self.log_text.AppendText(f"Download Speed: {download:.2f} Mbps")
                    
                    # Add quality rating based on download speed
                    if download < 10:
                        self.log_text.AppendText(" (Poor)")
                    elif download < 20:
                        self.log_text.AppendText(" (Moderate)")
                    elif download < 50:
                        self.log_text.AppendText(" (Good)")
                    else:
                        self.log_text.AppendText(" (Excellent)")
                        
                    self.log_text.AppendText("\n")
                else:
                    self.log_text.AppendText("Download Speed: Test Failed\n")
                    
                if upload is not None:
                    self.log_text.AppendText(f"Upload Speed: {upload:.2f} Mbps\n")
                else:
                    self.log_text.AppendText("Upload Speed: Test Failed\n")
                    
                if ping is not None:
                    self.log_text.AppendText(f"Ping Latency: {ping:.2f} ms")
                    
                    # Add comparison for ping
                    if ping < 20:
                        self.log_text.AppendText(" (Excellent for competitive gaming)")
                    elif ping < 50:
                        self.log_text.AppendText(" (Good for most online games)")
                    elif ping < 100:
                        self.log_text.AppendText(" (Suitable for casual gaming and video calls)")
                    else:
                        self.log_text.AppendText(" (May experience lag in real-time applications)")
                        
                    self.log_text.AppendText("\n")
                else:
                    self.log_text.AppendText("Ping Latency: Test Failed\n")
                
                # Add connection quality rating based on download speed
                if download is not None:
                    self.log_text.AppendText("\nConnection Quality Rating:\n")
                    if download < 10:
                        self.log_text.AppendText("Poor - May struggle with video streaming and downloads")
                    elif download < 20:
                        self.log_text.AppendText("Moderate - Adequate for standard definition video and general use")
                    elif download < 50:
                        self.log_text.AppendText("Good - Suitable for HD streaming and most online activities")
                    else:
                        self.log_text.AppendText("Excellent - Ideal for 4K streaming, online gaming, and large downloads")
                    self.log_text.AppendText("\n")
                
                # Add test method information
                self.log_text.AppendText("\nTest Method: Multi-stage adaptive testing")
                self.log_text.AppendText("\nTest completed at: " + wx.DateTime.Now().Format("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            logging.debug(f"Results update skipped - widget may have been destroyed: {e}")
        
    def show_quality_assessment(self, quality, description, icon_bitmap=None):
        """Show an internet quality assessment card."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_show_quality_assessment, quality, description, icon_bitmap)
        else:
            self._safe_show_quality_assessment(quality, description, icon_bitmap)
            
    def _safe_show_quality_assessment(self, quality, description, icon_bitmap=None):
        """Thread-safe implementation of show_quality_assessment."""
        try:
            # Check if widget still exists
            if not self or not self.analysis_container:
                return
                
            # Update only if widget is not being deleted
            if not self.analysis_container.IsBeingDeleted():
                # Clear previous assessments
                self.analysis_container.GetSizer().Clear(True)
                
                # Special handling for offline or failure cases
                if quality == "poor" and ("failed" in description.lower() or "check your internet" in description.lower()):
                    # Add troubleshooting tips
                    panel = ModernPanel(self.analysis_container)
                    sizer = wx.BoxSizer(wx.VERTICAL)
                    
                    title = wx.StaticText(panel, label="Connection Issue Detected")
                    title.SetFont(AppTheme.get_bold_font(12))
                    title.SetForegroundColour(wx.Colour(200, 0, 0))  # Red
                    
                    message = wx.StaticText(panel, label=description)
                    message.SetFont(AppTheme.get_font(10))
                    
                    tips_title = wx.StaticText(panel, label="Troubleshooting Tips:")
                    tips_title.SetFont(AppTheme.get_bold_font(10))
                    
                    tips = [
                        "• Check that your device is connected to Wi-Fi or ethernet",
                        "• Restart your router/modem",
                        "• Check if other devices on your network have internet access",
                        "• Contact your Internet Service Provider if the issue persists",
                        "• Try the test again in a few minutes"
                    ]
                    
                    tips_text = wx.StaticText(panel, label="\n".join(tips))
                    tips_text.SetFont(AppTheme.get_font(9))
                    
                    sizer.Add(title, 0, wx.BOTTOM, 10)
                    sizer.Add(message, 0, wx.BOTTOM, 15)
                    sizer.Add(tips_title, 0, wx.BOTTOM, 5)
                    sizer.Add(tips_text, 0)
                    
                    panel.SetSizer(sizer)
                    panel.SetBackgroundColour(wx.Colour(255, 240, 240))  # Light red background
                    
                    self.analysis_container.GetSizer().Add(panel, 0, wx.EXPAND | wx.BOTTOM, 10)
                else:
                    # Create a quality assessment card
                    card = ResultCard(
                        self.analysis_container,
                        title=f"Connection Quality: {quality.capitalize()}",
                        details=description,
                        icon=icon_bitmap,
                        quality=quality
                    )
                    
                    self.analysis_container.GetSizer().Add(card, 0, wx.EXPAND | wx.BOTTOM, 10)
                
                self.analysis_container.Layout()
                self.Layout()
        except Exception as e:
            logging.debug(f"Quality assessment update skipped - widget may have been destroyed: {e}")
        
    def get_selected_server(self):
        """Get the currently selected test server."""
        selection = self.server_choice.GetSelection()
        server_name = self.server_choice.GetString(selection)
        return self.test_servers[server_name]["url"]
        
    def clear_results(self):
        """Clear all result displays."""
        try:
            # Check if widgets still exist
            if not self or not self.download_card or not self.upload_card or not self.ping_card:
                return
                
            if (not self.download_card.IsBeingDeleted() and 
                not self.upload_card.IsBeingDeleted() and 
                not self.ping_card.IsBeingDeleted()):
                
                self.download_card.SetValue("-- Mbps")
                self.upload_card.SetValue("-- Mbps")
                self.ping_card.SetValue("-- ms")
                
                # Clear current speed text
                if hasattr(self, 'current_speed_text') and not self.current_speed_text.IsBeingDeleted():
                    self.current_speed_text.SetLabel("")
                
                if self.log_text and not self.log_text.IsBeingDeleted():
                    self.log_text.Clear()
                
                if self.analysis_container and not self.analysis_container.IsBeingDeleted():
                    self.analysis_container.GetSizer().Clear(True)
                    self.analysis_container.Layout()
                
                self.Layout()
        except Exception as e:
            logging.debug(f"Clear results skipped - widget may have been destroyed: {e}")
        
    def set_testing_state(self, is_testing):
        """Set the UI state based on whether a test is running."""
        try:
            # Check if widgets still exist
            if not self or not self.start_button or not self.server_choice or not self.status_text:
                return
                
            # Update only if widgets are not being deleted
            if (not self.start_button.IsBeingDeleted() and 
                not self.server_choice.IsBeingDeleted() and 
                not self.status_text.IsBeingDeleted()):
                
                self.start_button.Enable(not is_testing)
                self.server_choice.Enable(not is_testing)
                
                # Also disable refresh button during testing
                if hasattr(self, 'refresh_button') and not self.refresh_button.IsBeingDeleted():
                    self.refresh_button.Enable(not is_testing)
                
                if is_testing:
                    self.status_text.SetLabel("Running speed test...")
                else:
                    if hasattr(self, 'progress_gauge') and not self.progress_gauge.IsBeingDeleted():
                        self.progress_gauge.SetValue(0)
                    self.status_text.SetLabel("Ready to test")
                    # Refresh server status after test
                    self._check_server_status()
        except Exception as e:
            logging.debug(f"Testing state update skipped - widget may have been destroyed: {e}")
        
    def _check_server_status(self):
        """Check the status of all servers."""
        import threading
        import requests
        
        def check_server(server_name, server_info):
            try:
                url = server_info["url"]
                if url == "auto":
                    # Automatic selection is always marked as available
                    status = "available"
                    wx.CallAfter(self._update_server_status, server_name, status)
                    return
                
                # Special case for Local Connection
                if "127.0.0.1" in url:
                    status = "available"  # Always mark local as available
                    wx.CallAfter(self._update_server_status, server_name, status)
                    return
                
                # Extract domain for checking
                domain = url.split("//")[1].split("/")[0] if "//" in url else url.split("/")[0]
                
                # Try HTTPS first with very short timeout
                success = False
                for protocol in ["https://", "http://"]:
                    if success:
                        break
                    
                    try:
                        # Use a very short timeout to avoid hanging the UI
                        check_url = f"{protocol}{domain}"
                        response = requests.head(check_url, timeout=1.0, 
                                               allow_redirects=True)
                        if response.status_code < 400:
                            success = True
                    except Exception:
                        # Try next protocol
                        pass
                
                status = "available" if success else "unavailable"
            except Exception as e:
                # Failed to check status
                logging.debug(f"Server status check failed for {server_name}: {e}")
                status = "unavailable"
            
            # Update UI with status
            wx.CallAfter(self._update_server_status, server_name, status)
        
        # Add status checking message
        if hasattr(self, 'status_text') and self.status_text and not self.status_text.IsBeingDeleted():
            self.status_text.SetLabel("Checking server availability...")
        
        # Check all servers in separate threads
        for server_name, server_info in self.test_servers.items():
            threading.Thread(target=check_server, args=(server_name, server_info), daemon=True).start()
            
        # Start a timer to check if all servers are unavailable after checking
        def check_all_unavailable():
            # Wait for status checks to complete (giving some time for threads)
            time.sleep(3)
            
            # Count available servers
            available_count = sum(1 for info in self.test_servers.values() 
                                 if info["status"] == "available" and info["url"] != "auto" and "127.0.0.1" not in info["url"])
            
            if available_count == 0:
                # All servers unavailable - likely offline
                wx.CallAfter(self._show_offline_warning)
        
        # Start the offline check in a background thread
        import time
        threading.Thread(target=check_all_unavailable, daemon=True).start()
    
    def _show_offline_warning(self):
        """Show a warning when all servers are unavailable."""
        if not self or not hasattr(self, 'status_text') or not self.status_text:
            return
            
        if self.status_text.IsBeingDeleted():
            return
            
        self.status_text.SetLabel("⚠️ No internet connection detected - All servers unavailable")
        self.status_text.SetForegroundColour(wx.Colour(200, 0, 0))  # Red
        
        # Maybe also show a more detailed message in the current_speed_text
        if hasattr(self, 'current_speed_text') and not self.current_speed_text.IsBeingDeleted():
            self.current_speed_text.SetLabel("Try refreshing or check your network connection")
            self.current_speed_text.SetForegroundColour(wx.Colour(200, 0, 0))  # Red
        
    def _update_server_status(self, server_name, status):
        """Update the UI with server status."""
        self.test_servers[server_name]["status"] = status
        
        if self.server_choice.GetStringSelection() == server_name:
            self._update_selected_server_info()
    
    def _update_selected_server_info(self):
        """Update the server info display for the selected server."""
        server_name = self.server_choice.GetStringSelection()
        server_info = self.test_servers[server_name]
        
        # Update status indicator color
        status_colors = {
            "available": wx.Colour(0, 200, 0),    # Green
            "unavailable": wx.Colour(200, 0, 0),  # Red
            "unknown": wx.Colour(128, 128, 128)   # Gray
        }
        self.status_indicator.SetForegroundColour(status_colors[server_info["status"]])
        
        # Update server info text
        if server_name == "Automatic (Recommended)":
            info_text = "Tests multiple servers to find the best connection"
        else:
            status_text = {
                "available": "Available",
                "unavailable": "Currently Unavailable",
                "unknown": "Status Unknown"
            }[server_info["status"]]
            info_text = f"{server_info['location']} - {server_info['provider']} ({status_text})"
        
        self.server_info.SetLabel(info_text)
        self.Layout()
    
    def _on_server_selected(self, event):
        """Handle server selection change."""
        self._update_selected_server_info()

    def trigger_refresh(self, event=None):
        """Manually refresh server status."""
        if hasattr(self, 'status_text') and self.status_text and not self.status_text.IsBeingDeleted():
            self.status_text.SetLabel("Refreshing server availability...")
            
        # Clear old statuses first
        for server_info in self.test_servers.values():
            server_info["status"] = "unknown"
            
        # Check again
        self._check_server_status()
        
        # Update the currently selected server info
        self._update_selected_server_info() 

    def update_progress(self, value, message=None):
        """Update progress gauge and message."""
        self.progress_gauge.SetValue(value)
        
        # If we have a message, update status text and ensure it's visible
        if message:
            self.status_text.SetLabel(message)
            # Make text color more prominent for active test
            if value < 100:
                self.status_text.SetForegroundColour(AppTheme.PRIMARY)
            else:
                # Reset to normal text color when complete
                self.status_text.SetForegroundColour(AppTheme.TEXT)
                
        # Force layout update to show changes immediately
        self.progress_panel.Layout() 