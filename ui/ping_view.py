import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from .modern_widgets import ModernPanel, ModernButton, ModernTextCtrl, ModernGauge
from .modern_widgets import ResultCard, AppTheme

class PingTestView(ModernPanel):
    """Panel for the Ping Test tab."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Default ping targets
        self.default_targets = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
        
        self._create_ui()
        self._bind_events()
        
        # Ensure proper layout
        self.Layout()
        
    def _create_ui(self):
        """Create the UI elements."""
        # Main container with some padding
        container = wx.BoxSizer(wx.VERTICAL)
        
        # Top controls section
        controls_panel = ModernPanel(self)
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Target selection group
        target_group = self._create_target_selection(controls_panel)
        
        # Test parameters group
        params_group = self._create_test_parameters(controls_panel)
        
        # Start button 
        self.start_button = ModernButton(
            controls_panel, 
            label="Start Test",
            size=(-1, 36)
        )
        
        # Add the groups to the controls section
        controls_sizer.Add(target_group, 2, wx.EXPAND | wx.RIGHT, 10)
        controls_sizer.Add(params_group, 1, wx.EXPAND)
        controls_sizer.Add(self.start_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        controls_panel.SetSizer(controls_sizer)
        
        # Progress gauge
        self.progress_gauge = ModernGauge(self, label="Ping Test Progress")
        
        # Results area with increased height and scrolling
        self.results_text = ModernTextCtrl(
            self,
            size=(-1, 100),  # Slightly reduced height
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL  # Added scrolling
        )
        self.results_text.SetFont(AppTheme.get_font(10))
        
        # Chart for visualization - Reduced size
        self.figure, self.ax = plt.subplots(figsize=(6, 2))
        self.figure.patch.set_facecolor(AppTheme.PANEL_BG.GetAsString(wx.C2S_HTML_SYNTAX))
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        # Result card container with fixed height
        self.result_card_container = ModernPanel(self)
        self.result_card_container.SetMinSize((-1, 100))  # Set minimum height
        self.result_card_container.SetSizer(wx.BoxSizer(wx.VERTICAL))
        
        # Add components to the main container with adjusted proportions
        container.Add(controls_panel, 0, wx.EXPAND | wx.ALL, 10)
        container.Add(self.progress_gauge, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        container.Add(self.results_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        container.Add(self.canvas, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        container.Add(self.result_card_container, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Set the main sizer
        self.main_sizer.Add(container, 1, wx.EXPAND)
        
        # Initialize chart
        self._init_chart()
        
    def _init_chart(self):
        """Initialize the ping chart."""
        self.ax.clear()
        self.ax.set_title("Ping Latency")
        self.ax.set_xlabel("Ping #")
        self.ax.set_ylabel("Latency (ms)")
        self.ax.grid(True)
        self.ax.text(0.5, 0.5, "Start a ping test to see results", 
                    ha='center', va='center', fontsize=12)
        self.figure.tight_layout()
        self.canvas.draw()
        
    def _create_target_selection(self, parent):
        """Create the target selection controls."""
        group_box = wx.StaticBox(parent, label="Target")
        group_box.SetFont(AppTheme.get_bold_font(10))
        sizer = wx.StaticBoxSizer(group_box, wx.VERTICAL)
        
        # IP choice and input field
        ip_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ip_choice = wx.Choice(group_box, choices=self.default_targets)
        self.ip_choice.SetSelection(0)
        
        # Or label
        or_label = wx.StaticText(group_box, label="or")
        or_label.SetFont(AppTheme.get_font(9))
        
        # Custom target input
        self.target_input = wx.TextCtrl(group_box, size=(150, -1))
        
        ip_sizer.Add(self.ip_choice, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        ip_sizer.Add(or_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        ip_sizer.Add(self.target_input, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        
        # Hostname info
        info_text = wx.StaticText(
            group_box, 
            label="Enter an IP address or hostname (e.g., google.com)"
        )
        info_text.SetFont(AppTheme.get_font(8))
        info_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        sizer.Add(ip_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(info_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        return sizer
    
    def _create_test_parameters(self, parent):
        """Create the test parameters controls."""
        group_box = wx.StaticBox(parent, label="Parameters")
        group_box.SetFont(AppTheme.get_bold_font(10))
        sizer = wx.StaticBoxSizer(group_box, wx.VERTICAL)
        
        # Parameters grid
        params_grid = wx.FlexGridSizer(2, 2, 5, 10)
        params_grid.AddGrowableCol(1)
        
        # Ping count
        count_label = wx.StaticText(group_box, label="Count:")
        self.ping_count = wx.SpinCtrl(group_box, value="4", min=1, max=100, size=(70, -1))
        
        # Ping interval
        interval_label = wx.StaticText(group_box, label="Interval (s):")
        self.ping_interval = wx.SpinCtrl(group_box, value="1", min=1, max=10, size=(70, -1))
        
        params_grid.Add(count_label, 0, wx.ALIGN_CENTER_VERTICAL)
        params_grid.Add(self.ping_count, 0, wx.EXPAND)
        params_grid.Add(interval_label, 0, wx.ALIGN_CENTER_VERTICAL)
        params_grid.Add(self.ping_interval, 0, wx.EXPAND)
        
        sizer.Add(params_grid, 0, wx.EXPAND | wx.ALL, 5)
        
        return sizer
        
    def _bind_events(self):
        """Bind control events."""
        self.ip_choice.Bind(wx.EVT_CHOICE, self.on_ip_choice)
        
    def on_ip_choice(self, event):
        """Handle IP choice selection."""
        # Clear the custom input when selecting from dropdown
        self.target_input.Clear()
        
    def get_target(self):
        """Get the selected target (IP or hostname)."""
        custom_target = self.target_input.GetValue().strip()
        if custom_target:
            return custom_target
        else:
            return self.ip_choice.GetStringSelection()
            
    def get_test_parameters(self):
        """Get the test parameters."""
        return {
            'count': self.ping_count.GetValue(),
            'interval': self.ping_interval.GetValue()
        }
        
    def update_progress(self, value):
        """Update the progress gauge."""
        self.progress_gauge.SetValue(value)
        
    def clear_results(self):
        """Clear previous results."""
        self.results_text.Clear()
        self.ax.clear()
        self.canvas.draw_idle()
        
        # Clear any previous result cards
        self.result_card_container.GetSizer().Clear(True)
        self.result_card_container.Hide()
        self.Layout()
        
    def update_results(self, latency_data, packet_loss, stats=None):
        """Update the results display with ping results."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_update_results, latency_data, packet_loss, stats)
        else:
            self._safe_update_results(latency_data, packet_loss, stats)
            
    def _safe_update_results(self, latency_data, packet_loss, stats=None):
        """Thread-safe implementation of update_results."""
        try:
            self.results_text.Clear()
            
            if stats:
                # Add results with proper formatting
                self.results_text.AppendText("Ping Test Results:\n\n")
                self.results_text.AppendText(f"Average Latency: {stats['avg_latency']:.2f} ms\n")
                self.results_text.AppendText(f"Minimum Latency: {stats['min_latency']:.2f} ms\n")
                self.results_text.AppendText(f"Maximum Latency: {stats['max_latency']:.2f} ms\n")
                self.results_text.AppendText(f"Packet Loss: {packet_loss:.2f}%\n")
                
                # Add quality assessment based on latency
                if stats['avg_latency'] < 50:
                    quality = "Excellent"
                elif stats['avg_latency'] < 100:
                    quality = "Good"
                elif stats['avg_latency'] < 150:
                    quality = "Moderate"
                else:
                    quality = "Poor"
                    
                self.results_text.AppendText(f"\nConnection Quality: {quality}")
                
            self.update_chart(latency_data)
            
            # Ensure text is visible
            self.results_text.ShowPosition(0)
            
        except Exception as e:
            import logging
            logging.error(f"Error updating ping results: {e}")
        
    def update_chart(self, latency_data):
        """Update the latency chart."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_update_chart, latency_data)
        else:
            self._safe_update_chart(latency_data)
            
    def _safe_update_chart(self, latency_data):
        """Thread-safe implementation of update_chart."""
        try:
            self.ax.clear()
            if latency_data:
                self.ax.plot(
                    latency_data, 
                    label="Ping Latency (ms)", 
                    color=AppTheme.PRIMARY.GetAsString(wx.C2S_HTML_SYNTAX), 
                    marker="o", 
                    linestyle="-", 
                    linewidth=1.5,  # Reduced line width
                    markersize=4  # Reduced marker size
                )
                
            self.ax.set_ylim(bottom=0)
            self.ax.set_title("Ping Latency Over Time", fontsize=10)  # Reduced font size
            self.ax.set_xlabel("Ping Count", fontsize=9)  # Reduced font size
            self.ax.set_ylabel("Latency (ms)", fontsize=9)  # Reduced font size
            self.ax.legend(fontsize=8)  # Reduced font size
            self.ax.grid(True, linestyle="--", alpha=0.7)
            self.figure.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            import logging
            logging.error(f"Error updating chart: {e}")
            
    def show_quality_assessment(self, quality, description, icon_bitmap=None):
        """Show a quality assessment card."""
        if not wx.IsMainThread():
            wx.CallAfter(self._safe_show_quality_assessment, quality, description, icon_bitmap)
        else:
            self._safe_show_quality_assessment(quality, description, icon_bitmap)
            
    def _safe_show_quality_assessment(self, quality, description, icon_bitmap=None):
        """Thread-safe implementation of show_quality_assessment."""
        try:
            # Clear previous cards
            self.result_card_container.GetSizer().Clear(True)
            
            # Create a new result card with increased size
            card = ResultCard(
                self.result_card_container,
                title=f"Network Quality: {quality.capitalize()}",
                details=description,
                icon=icon_bitmap,
                quality=quality,
                size=(-1, 90)  # Increased height for better visibility
            )
            
            # Add the card with some padding
            self.result_card_container.GetSizer().Add(card, 1, wx.EXPAND | wx.ALL, 5)
            self.result_card_container.Show()
            
            # Force layout update
            self.result_card_container.Layout()
            self.Layout()
            self.GetParent().Layout()
            
            # Ensure the card is visible
            self.result_card_container.Refresh()
            
        except Exception as e:
            import logging
            logging.error(f"Error showing quality assessment: {e}") 