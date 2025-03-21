import wx
import wx.lib.agw.gradientbutton as GB
from wx.adv import HyperlinkCtrl
import wx.lib.newevent

# Custom events
ProgressUpdateEvent, EVT_PROGRESS_UPDATE = wx.lib.newevent.NewEvent()
StatusUpdateEvent, EVT_STATUS_UPDATE = wx.lib.newevent.NewEvent()

# Define consistent theme colors
class AppTheme:
    """Application theme colors and styles."""
    # Main colors
    PRIMARY = wx.Colour(41, 128, 185)      # Blue
    SECONDARY = wx.Colour(52, 152, 219)    # Lighter Blue
    ACCENT = wx.Colour(46, 204, 113)       # Green
    WARNING = wx.Colour(230, 126, 34)      # Orange
    DANGER = wx.Colour(231, 76, 60)        # Red
    
    # Background and text colors
    BACKGROUND = wx.Colour(240, 244, 247)  # Very light blue/gray
    PANEL_BG = wx.Colour(249, 252, 255)    # Almost white
    TEXT = wx.Colour(44, 62, 80)           # Dark blue/gray
    TEXT_LIGHT = wx.Colour(127, 140, 141)  # Gray
    
    # Sizes
    BUTTON_SIZE = wx.Size(100, 36)
    SMALL_BUTTON_SIZE = wx.Size(80, 30)
    
    # Fonts
    FONT_FAMILY = wx.FONTFAMILY_DEFAULT
    
    @staticmethod
    def get_font(size=11, weight=wx.FONTWEIGHT_NORMAL):
        """Get a font with the specified parameters."""
        return wx.Font(size, AppTheme.FONT_FAMILY, wx.FONTSTYLE_NORMAL, weight)
    
    @staticmethod
    def get_bold_font(size=11):
        """Get a bold font with the specified size."""
        return AppTheme.get_font(size, wx.FONTWEIGHT_BOLD)


class ModernButton(wx.Button):
    """A modern styled button with hover effects."""
    
    def __init__(self, parent, label="", size=AppTheme.BUTTON_SIZE, color=AppTheme.PRIMARY):
        super().__init__(
            parent, 
            label=label,
            size=size,
            style=wx.BORDER_NONE
        )
        
        self.default_color = color
        self.hover_color = color.ChangeLightness(85)
        self.pressed_color = color.ChangeLightness(70)
        self.current_color = self.default_color
        
        # Set font and colors
        self.SetFont(AppTheme.get_bold_font())
        self.SetForegroundColour(wx.WHITE)
        self.SetBackgroundColour(self.current_color)
        
        # Bind events
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        
    def on_mouse_enter(self, event):
        """Handle mouse enter event."""
        self.current_color = self.hover_color
        self.SetBackgroundColour(self.current_color)
        self.Refresh()
        
    def on_mouse_leave(self, event):
        """Handle mouse leave event."""
        self.current_color = self.default_color
        self.SetBackgroundColour(self.current_color)
        self.Refresh()
        
    def on_mouse_down(self, event):
        """Handle mouse down event."""
        self.current_color = self.pressed_color
        self.SetBackgroundColour(self.current_color)
        self.Refresh()
        event.Skip()
        
    def on_mouse_up(self, event):
        """Handle mouse up event."""
        self.current_color = self.hover_color if self.GetScreenRect().Contains(wx.GetMousePosition()) else self.default_color
        self.SetBackgroundColour(self.current_color)
        self.Refresh()
        event.Skip()


class ModernPanel(wx.Panel):
    """A modern styled panel with a clean background."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Set background color
        self.SetBackgroundColour(AppTheme.PANEL_BG)
        
        # Create main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)
        
        # Bind size event to ensure proper layout
        self.Bind(wx.EVT_SIZE, self.on_size)
        
    def on_size(self, event):
        """Handle resize events."""
        self.Layout()
        event.Skip()


class ModernTextCtrl(wx.TextCtrl):
    """A modern styled text control with improved look and feel."""
    
    def __init__(self, parent, value="", size=wx.DefaultSize, style=wx.TE_MULTILINE | wx.TE_READONLY):
        super().__init__(
            parent,
            value=value,
            size=size if size != wx.DefaultSize else wx.Size(200, 100),
            style=style | wx.BORDER_NONE
        )
        
        # Set font and colors
        self.SetFont(AppTheme.get_font())
        self.SetForegroundColour(AppTheme.TEXT)
        self.SetBackgroundColour(wx.WHITE)
        
        # Ensure the control is visible
        self.Show()
        
        # Bind size event to ensure proper layout
        self.Bind(wx.EVT_SIZE, self.on_size)
        
    def on_size(self, event):
        """Handle resize events to ensure proper layout."""
        self.Layout()
        event.Skip()
        
    def AppendText(self, text):
        """Override AppendText to ensure proper thread safety."""
        if not wx.IsMainThread():
            wx.CallAfter(super().AppendText, text)
        else:
            super().AppendText(text)
            
    def SetValue(self, value):
        """Override SetValue to ensure proper thread safety."""
        if not wx.IsMainThread():
            wx.CallAfter(super().SetValue, value)
        else:
            super().SetValue(value)


class StatusLabel(wx.StaticText):
    """A status label that displays status with an appropriate color."""
    
    STATUS_COLORS = {
        "normal": AppTheme.TEXT,
        "info": AppTheme.SECONDARY,
        "success": AppTheme.ACCENT,
        "warning": AppTheme.WARNING,
        "error": AppTheme.DANGER
    }
    
    def __init__(self, parent, label="", status="normal"):
        super().__init__(parent, label=label)
        self.SetFont(AppTheme.get_font(10))
        self.set_status(status)
        
    def set_status(self, status, text=None):
        """Set the status and optionally the text."""
        if text:
            self.SetLabel(text)
        
        if status in self.STATUS_COLORS:
            self.SetForegroundColour(self.STATUS_COLORS[status])
        else:
            self.SetForegroundColour(self.STATUS_COLORS["normal"])
        
        self.Refresh()


class ModernGauge(wx.Panel):
    """A modern styled progress gauge with label and percentage."""
    
    def __init__(self, parent, label="Progress", range=100, size=(-1, 24)):
        super().__init__(parent, size=size)
        self.SetBackgroundColour(AppTheme.PANEL_BG)
        
        # Create controls
        self.label = wx.StaticText(self, label=label)
        self.label.SetFont(AppTheme.get_font(9))
        self.label.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        self.gauge = wx.Gauge(self, range=range, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.gauge.SetBackgroundColour(wx.Colour(230, 230, 230))
        
        self.percent = wx.StaticText(self, label="0%")
        self.percent.SetFont(AppTheme.get_font(9))
        self.percent.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.label, 1, wx.ALIGN_CENTER_VERTICAL)
        top_sizer.Add(self.percent, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        
        sizer.Add(top_sizer, 0, wx.EXPAND | wx.BOTTOM, 2)
        sizer.Add(self.gauge, 0, wx.EXPAND)
        
        self.SetSizer(sizer)
        
        # State
        self.status_text = ""
        
    def SetValue(self, value):
        """Set the gauge value."""
        if not self or not wx.IsMainThread():
            wx.CallAfter(self._safe_set_value, value)
        else:
            self._safe_set_value(value)
        
    def _safe_set_value(self, value):
        """Safely set values on UI controls."""
        try:
            if self and self.gauge:
                # Convert to integer if it's a float
                if isinstance(value, float):
                    value = int(value)
                self.gauge.SetValue(value)
            if self and self.percent:
                self.percent.SetLabel(f"{value}%")
        except Exception as e:
            import logging
            logging.error(f"Error updating gauge: {e}")
        
    def SetStatus(self, text):
        """Set the status text."""
        if not self or not wx.IsMainThread():
            wx.CallAfter(self._safe_set_status, text)
        else:
            self._safe_set_status(text)
            
    def _safe_set_status(self, text):
        """Safely set status text."""
        try:
            if self and self.label:
                self.status_text = text
                self.label.SetLabel(f"{self.label.GetLabel().split(':')[0]}: {text}")
        except Exception as e:
            import logging
            logging.error(f"Error updating status: {e}")
        
    def Pulse(self):
        """Pulse the gauge."""
        if not self or not wx.IsMainThread():
            wx.CallAfter(self._safe_pulse)
        else:
            self._safe_pulse()
            
    def _safe_pulse(self):
        """Safely pulse the gauge."""
        try:
            if self and self.gauge:
                self.gauge.Pulse()
        except Exception as e:
            import logging
            logging.error(f"Error pulsing gauge: {e}")


class MetricCard(wx.Panel):
    """A card that displays a metric with a label, value, and optional icon."""
    
    def __init__(self, parent, title="", value="", icon=None, color=AppTheme.PRIMARY):
        super().__init__(parent)
        self.SetBackgroundColour(wx.WHITE)
        
        # Create a border effect
        self.SetForegroundColour(color)
        self.SetWindowStyle(wx.BORDER_NONE)
        
        # Create controls
        title_text = wx.StaticText(self, label=title)
        title_text.SetFont(AppTheme.get_font(10))
        title_text.SetForegroundColour(AppTheme.TEXT_LIGHT)
        
        self.value_text = wx.StaticText(self, label=value)
        self.value_text.SetFont(AppTheme.get_bold_font(24))
        self.value_text.SetForegroundColour(color)
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title_text, 0, wx.ALL, 10)
        sizer.Add(self.value_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        if icon:
            bitmap = wx.StaticBitmap(self, bitmap=icon)
            sizer.Add(bitmap, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        self.SetSizer(sizer)
        
        # Add border with a thin line
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
    def on_paint(self, event):
        """Paint event handler to draw the border."""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            rect = self.GetClientRect()
            
            # Draw rounded rectangle with a thin border
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, rect.width, rect.height, 5)
            
            # Set pen for the border
            gc.SetPen(wx.Pen(wx.Colour(220, 220, 220), 1))
            gc.StrokePath(path)
        
    def SetValue(self, value):
        """Set the value displayed on the card."""
        if not self or not wx.IsMainThread():
            wx.CallAfter(self._safe_set_value, value)
        else:
            self._safe_set_value(value)
            
    def _safe_set_value(self, value):
        """Safely set the value."""
        try:
            if self and self.value_text:
                self.value_text.SetLabel(value)
        except Exception as e:
            import logging
            logging.error(f"Error updating metric card: {e}")


class IconTextButton(wx.Panel):
    """A button with an icon and text."""
    
    def __init__(self, parent, label="", bitmap=None, color=AppTheme.PRIMARY):
        super().__init__(parent)
        self.SetBackgroundColour(wx.WHITE)
        
        # Create controls
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        if bitmap:
            icon = wx.StaticBitmap(self, bitmap=bitmap)
            sizer.Add(icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
            
        text = wx.StaticText(self, label=label)
        text.SetFont(AppTheme.get_font())
        text.SetForegroundColour(color)
        
        sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.SetSizer(sizer)
        
        # Bind events for button behavior
        for child in self.GetChildren():
            child.Bind(wx.EVT_LEFT_DOWN, self.on_click)
            
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        
    def on_click(self, event):
        """Handle click event."""
        evt = wx.CommandEvent(wx.wxEVT_BUTTON)
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        
    def on_mouse_enter(self, event):
        """Handle mouse enter event."""
        self.SetBackgroundColour(wx.Colour(245, 245, 245))
        self.Refresh()
        
    def on_mouse_leave(self, event):
        """Handle mouse leave event."""
        self.SetBackgroundColour(wx.WHITE)
        self.Refresh()
        
    def Bind(self, event, handler, source=None, id=-1, id2=-1):
        """Override Bind to handle button events."""
        if event == wx.EVT_BUTTON and source is None:
            source = self
        super().Bind(event, handler, source, id, id2)


class ModernHyperlinkCtrl(HyperlinkCtrl):
    """A modern styled hyperlink control."""
    
    def __init__(self, parent, label="", url="", color=AppTheme.PRIMARY):
        super().__init__(
            parent,
            label=label,
            url=url,
            style=wx.HL_DEFAULT_STYLE
        )
        
        self.SetFont(AppTheme.get_font())
        self.SetColours(
            link=color,
            visited=color.ChangeLightness(70),
            hover=color.ChangeLightness(130)
        )
        
        self.SetUnderlines(False, False, True)
        self.UpdateLink(True)


class NotificationBar(wx.Panel):
    """A notification bar that displays messages with an icon and close button."""
    
    def __init__(self, parent, message="", style="info"):
        super().__init__(parent)
        
        # Set appearance based on style
        if style == "error":
            bg_color = wx.Colour(253, 237, 237)
            fg_color = AppTheme.DANGER
        elif style == "warning":
            bg_color = wx.Colour(255, 248, 230)
            fg_color = AppTheme.WARNING
        elif style == "success":
            bg_color = wx.Colour(237, 247, 237)
            fg_color = AppTheme.ACCENT
        else:  # info
            bg_color = wx.Colour(232, 245, 253)
            fg_color = AppTheme.PRIMARY
            
        self.SetBackgroundColour(bg_color)
        
        # Create controls
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        message_text = wx.StaticText(self, label=message)
        message_text.SetFont(AppTheme.get_font(10))
        message_text.SetForegroundColour(fg_color)
        
        close_button = wx.Button(self, label="×", size=(24, 24), style=wx.BORDER_NONE)
        close_button.SetBackgroundColour(bg_color)
        close_button.SetForegroundColour(fg_color)
        
        sizer.Add(message_text, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        sizer.Add(close_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.SetSizer(sizer)
        
        # Bind close event
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        
    def on_close(self, event):
        """Handle close button click."""
        self.Show(False)
        self.GetParent().Layout()


class ResultCard(wx.Panel):
    """A card that displays a test result with an icon, title, and details."""
    
    def __init__(self, parent, title="", details="", icon=None, quality="good", size=wx.DefaultSize):
        super().__init__(parent, style=wx.BORDER_NONE, size=size)
        self.SetBackgroundColour(wx.WHITE)
        
        # Determine color based on quality
        if quality.lower() == "excellent":
            color = AppTheme.ACCENT
        elif quality.lower() == "good":
            color = AppTheme.SECONDARY
        elif quality.lower() == "moderate":
            color = AppTheme.WARNING
        else:  # poor
            color = AppTheme.DANGER
        
        # Create controls
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Icon
        if icon:
            icon_bitmap = wx.StaticBitmap(self, bitmap=icon)
            main_sizer.Add(icon_bitmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        # Text content
        text_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.title_text = wx.StaticText(self, label=title)
        self.title_text.SetFont(AppTheme.get_bold_font(11))  # Slightly larger font
        self.title_text.SetForegroundColour(color)
        
        self.details_text = wx.StaticText(self, label=details)
        self.details_text.SetFont(AppTheme.get_font(10))  # Slightly larger font
        self.details_text.SetForegroundColour(AppTheme.TEXT)
        self.details_text.Wrap(400)  # Wrap text at 400 pixels
        
        text_sizer.Add(self.title_text, 0, wx.EXPAND | wx.BOTTOM, 5)
        text_sizer.Add(self.details_text, 0, wx.EXPAND)
        
        main_sizer.Add(text_sizer, 1, wx.ALL | wx.EXPAND, 10)
        
        self.SetSizer(main_sizer)
        
        # Add border with a thin line
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
        # Ensure proper layout
        self.Layout()
        
        # Bind size event
        self.Bind(wx.EVT_SIZE, self.on_size)
        
    def on_size(self, event):
        """Handle resize events."""
        # Re-wrap text on resize
        if hasattr(self, 'details_text'):
            self.details_text.Wrap(min(400, self.GetSize().width - 40))  # Account for padding
        self.Layout()
        self.Refresh()  # Ensure the border is redrawn
        event.Skip()
        
    def on_paint(self, event):
        """Paint event handler to draw the border."""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            rect = self.GetClientRect()
            
            # Draw rounded rectangle with a thin border
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, rect.width, rect.height, 5)
            
            # Set pen for the border
            gc.SetPen(wx.Pen(wx.Colour(220, 220, 220), 1))
            gc.StrokePath(path)
            
            # Fill with white background
            gc.SetBrush(wx.Brush(wx.WHITE))
            gc.FillPath(path)
            
    def update_content(self, title=None, details=None):
        """Update the card content."""
        if title is not None:
            self.title_text.SetLabel(title)
        if details is not None:
            self.details_text.SetLabel(details)
            self.details_text.Wrap(min(400, self.GetSize().width - 40))
        self.Layout() 