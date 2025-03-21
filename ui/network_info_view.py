import wx
from .modern_widgets import ModernPanel, ModernButton, ModernTextCtrl, AppTheme
from .modern_widgets import MetricCard, NotificationBar

class NetworkInfoView(ModernPanel):
    """Panel for the Network Information tab."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI elements."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header section with refresh button
        header_panel = ModernPanel(self)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        title = wx.StaticText(header_panel, label="Network Information")
        title.SetFont(AppTheme.get_bold_font(12))
        
        self.refresh_button = ModernButton(
            header_panel, 
            label="Refresh",
            size=(-1, 32)
        )
        
        header_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.Add(self.refresh_button, 0, wx.ALIGN_CENTER_VERTICAL)
        header_panel.SetSizer(header_sizer)
        
        # Status notification area (initially hidden)
        self.notification_area = wx.Panel(self)
        self.notification_area.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.notification_area.Hide()
        
        # Key metrics section - cards for important network info
        metrics_panel = ModernPanel(self)
        metrics_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Create metric cards
        self.hostname_card = MetricCard(metrics_panel, title="Hostname", value="Loading...")
        self.local_ip_card = MetricCard(metrics_panel, title="Local IP", value="Loading...")
        self.public_ip_card = MetricCard(metrics_panel, title="Public IP", value="Loading...")
        
        metrics_sizer.Add(self.hostname_card, 1, wx.EXPAND | wx.RIGHT, 5)
        metrics_sizer.Add(self.local_ip_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        metrics_sizer.Add(self.public_ip_card, 1, wx.EXPAND | wx.LEFT, 5)
        
        metrics_panel.SetSizer(metrics_sizer)
        
        # DNS section
        dns_label = wx.StaticText(self, label="DNS Resolvers")
        dns_label.SetFont(AppTheme.get_bold_font(11))
        
        self.dns_list = wx.ListCtrl(
            self, 
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE
        )
        self.dns_list.SetFont(AppTheme.get_font())
        self.dns_list.InsertColumn(0, "DNS Server IP", width=200)
        
        # Network interfaces section
        interfaces_label = wx.StaticText(self, label="Network Interfaces")
        interfaces_label.SetFont(AppTheme.get_bold_font(11))
        
        self.interfaces_list = wx.ListCtrl(
            self, 
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE
        )
        self.interfaces_list.SetFont(AppTheme.get_font())
        self.interfaces_list.InsertColumn(0, "Interface", width=150)
        self.interfaces_list.InsertColumn(1, "IP Address", width=150)
        self.interfaces_list.InsertColumn(2, "Status", width=100)
        
        # Detailed information text
        info_label = wx.StaticText(self, label="Additional Information")
        info_label.SetFont(AppTheme.get_bold_font(11))
        
        self.info_text = ModernTextCtrl(self)
        
        # Layout all components
        main_sizer.Add(header_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.notification_area, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        main_sizer.Add(metrics_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        main_sizer.Add(dns_label, 0, wx.LEFT | wx.TOP, 10)
        main_sizer.Add(self.dns_list, 0, wx.EXPAND | wx.ALL, 10)
        
        main_sizer.Add(interfaces_label, 0, wx.LEFT | wx.TOP, 10)
        main_sizer.Add(self.interfaces_list, 0, wx.EXPAND | wx.ALL, 10)
        
        main_sizer.Add(info_label, 0, wx.LEFT | wx.TOP, 10)
        main_sizer.Add(self.info_text, 1, wx.EXPAND | wx.ALL, 10)
        
        self.SetSizer(main_sizer)
        
    def update_network_info(self, info):
        """Update the displayed network information."""
        # Update metric cards
        self.hostname_card.SetValue(info.get('hostname', 'Unknown'))
        self.local_ip_card.SetValue(info.get('local_ip', 'Unknown'))
        self.public_ip_card.SetValue(info.get('public_ip', 'Unknown'))
        
        # Update DNS servers
        self.dns_list.DeleteAllItems()
        for i, resolver in enumerate(info.get('dns_resolvers', [])):
            self.dns_list.InsertItem(i, resolver)
            
        # Update network interfaces
        self.interfaces_list.DeleteAllItems()
        interfaces = info.get('interfaces', {})
        row = 0
        for interface, addresses in interfaces.items():
            for addr in addresses:
                self.interfaces_list.InsertItem(row, interface)
                self.interfaces_list.SetItem(row, 1, addr)
                self.interfaces_list.SetItem(row, 2, "Up")
                row += 1
                
        # Update additional information
        self.info_text.Clear()
        self.info_text.AppendText(f"Default Gateway: {info.get('default_gateway', 'Unknown')}\n")
        
        if 'error' in info:
            self.show_notification(
                f"Error retrieving some network information: {info['error']}", 
                "warning"
            )
            
    def show_notification(self, message, style="info"):
        """Show a notification message."""
        # Clear any existing notifications
        self.notification_area.GetSizer().Clear(True)
        
        # Create a new notification
        notification = NotificationBar(self.notification_area, message, style)
        self.notification_area.GetSizer().Add(notification, 0, wx.EXPAND)
        
        self.notification_area.Show()
        self.Layout()
        
    def hide_notification(self):
        """Hide the notification area."""
        self.notification_area.Hide()
        self.Layout()
        
    def set_loading_state(self, is_loading=True):
        """Set the loading state of the view."""
        self.refresh_button.Enable(not is_loading)
        
        if is_loading:
            # Show loading indicators
            self.hostname_card.SetValue("Loading...")
            self.local_ip_card.SetValue("Loading...")
            self.public_ip_card.SetValue("Loading...")
            self.dns_list.DeleteAllItems()
            self.interfaces_list.DeleteAllItems()
            self.info_text.Clear()
            self.info_text.AppendText("Loading network information...") 