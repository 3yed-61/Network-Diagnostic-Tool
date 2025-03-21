import wx
import wx.lib.agw.flatnotebook as fnb
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import sys
import psutil
import platform
import traceback

# Configure logging with more detailed format
class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    def format(self, record):
        timestamp = self.formatTime(record, self.datefmt)
        level_name = record.levelname
        message = record.getMessage()
        return f"{timestamp} - {level_name} - {message}"

# Configure logging
log_file_handler = logging.FileHandler("network_checker.log", mode='w')  # Use 'w' mode to clear the log each time
log_file_handler.setFormatter(CustomFormatter("%(asctime)s - %(levelname)s - %(message)s"))

# StreamHandler for the debug window
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter("%(asctime)s - %(levelname)s - %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_file_handler, stream_handler]
)

# Global logger instance
logger = logging.getLogger()

# Handle console window in Windows
if platform.system() == 'Windows':
    import ctypes
    
    # Windows API constants for console handling
    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    # Function to properly close the console window
    def close_console():
        """Force close the console window using Windows API."""
        kernel32.FreeConsole()

# Import UI components
from ui.modern_widgets import AppTheme
from ui.ping_view import PingTestView
from ui.traceroute_view import TracerouteView
from ui.network_info_view import NetworkInfoView
from ui.speedtest_view import SpeedTestView
from ui.about_view import AboutView

# Import core utilities
from core.network_utils import NetworkUtils, NetworkValidator

# Debug window for showing logs in real-time
class DebugLogWindow(wx.Frame):
    """Debug window to show log messages in real-time."""
    
    def __init__(self, parent):
        super().__init__(
            parent, 
            title="Debug Log",
            size=(800, 400),
            style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER
        )
        
        self.parent = parent
        self.SetBackgroundColour(AppTheme.BACKGROUND)
        
        # Create the log text control
        self.log_text = wx.TextCtrl(
            self, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL,
            size=(-1, -1)
        )
        self.log_text.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Create a clear button
        self.clear_button = wx.Button(self, label="Clear Log")
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_log)
        
        # Create a save button
        self.save_button = wx.Button(self, label="Save Log")
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_log)
        
        # Create button sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.clear_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.save_button, 0)
        
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Set up log handler to redirect to this window
        self.log_handler = LogHandler(self)
        logger.addHandler(self.log_handler)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    def on_clear_log(self, event):
        """Clear the log text control."""
        self.log_text.Clear()
        
    def on_save_log(self, event):
        """Save the log to a file."""
        with wx.FileDialog(
            self, "Save Log File", wildcard="Text files (*.txt)|*.txt",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
                
            # Save the log
            try:
                with open(fileDialog.GetPath(), 'w') as file:
                    file.write(self.log_text.GetValue())
                wx.MessageBox("Log saved successfully.", "Success", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Error saving log: {e}", "Error", wx.OK | wx.ICON_ERROR)
                
    def on_close(self, event):
        """Hide the window instead of closing it."""
        self.Hide()
        
    def append_log(self, message):
        """Append message to the log text control."""
        # Append to text control
        self.log_text.AppendText(message + "\n")
        # Auto-scroll to bottom
        self.log_text.ShowPosition(self.log_text.GetLastPosition())

# Custom log handler to redirect logs to the debug window
class LogHandler(logging.Handler):
    """Custom log handler to redirect logs to a wx window."""
    
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.setFormatter(CustomFormatter("%(asctime)s - %(levelname)s - %(message)s"))
        
    def emit(self, record):
        """Emit the log record to the debug window."""
        msg = self.format(record)
        wx.CallAfter(self.window.append_log, msg)

class NetworkDiagnosticApp(wx.Frame):
    """Main application window for the Network Diagnostic Tool."""
    
    def __init__(self):
        super().__init__(
            None, 
            title="Network Diagnostic Tool", 
            size=(900, 700),
            style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER
        )
        
        self.SetMinSize((800, 600))
        self.SetBackgroundColour(AppTheme.BACKGROUND)
        
        # Create debug window
        self.debug_window = DebugLogWindow(self)
        
        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "icon.png")
            if os.path.exists(icon_path):
                self.SetIcon(wx.Icon(icon_path))
        except Exception as e:
            logging.warning(f"Could not load application icon: {e}")
            
        # Initialize network utilities
        self.network_utils = NetworkUtils()
        
        # Create shared thread pool for background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize UI
        self._create_ui()
        self._bind_events()
        
        # Add view debug log checkbox to menu
        self._create_menus()
        
        # Load initial network info
        self._load_network_info()
        
        # Center on screen and show
        self.Center()
        self.Show()
        
        # Log application startup
        logging.info("Application started successfully")
        
    def _create_menus(self):
        """Create application menus."""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        view_debug_log = file_menu.Append(wx.ID_ANY, "View Debug Log", "Show/hide debug log window")
        exit_item = file_menu.Append(wx.ID_EXIT, "Exit", "Exit the application")
        
        menubar.Append(file_menu, "File")
        self.SetMenuBar(menubar)
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_view_debug_log, view_debug_log)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        
    def on_view_debug_log(self, event):
        """Show or hide the debug log window."""
        if self.debug_window.IsShown():
            self.debug_window.Hide()
        else:
            self.debug_window.Show()
            self.debug_window.Raise()
            
    def on_exit(self, event):
        """Exit the application."""
        self.Close()
        
    def _create_ui(self):
        """Create the main UI components."""
        # Main container panel
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour(AppTheme.BACKGROUND)
        
        # Create notebook with tabs
        self.notebook = fnb.FlatNotebook(
            main_panel, 
            agwStyle=fnb.FNB_NO_X_BUTTON | fnb.FNB_SMART_TABS | fnb.FNB_NO_NAV_BUTTONS
        )
        
        # Set notebook colors
        self.notebook.SetTabAreaColour(AppTheme.BACKGROUND)
        self.notebook.SetActiveTabColour(AppTheme.PANEL_BG)
        self.notebook.SetNonActiveTabTextColour(AppTheme.TEXT)
        self.notebook.SetActiveTabTextColour(AppTheme.PRIMARY)
        
        # Create tab pages
        self._create_tab_pages()
        
        # Status bar
        self.status_bar = self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-2, -1, -1])
        self.status_bar.SetStatusText("Ready", 0)
        self.status_bar.SetStatusText("No Active Test", 1)
        self.status_bar.SetStatusText("v3.5", 2)  # Updated version
        self.status_bar.SetBackgroundColour(AppTheme.BACKGROUND)
        
        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        main_panel.SetSizer(main_sizer)
        main_panel.Layout()
        self.Layout()
        
    def _create_tab_pages(self):
        """Create and add all tab pages to the notebook."""
        # Ping Test
        self.ping_view = PingTestView(self.notebook)
        self.notebook.AddPage(self.ping_view, "Ping Test")
        
        # Trace Route
        self.traceroute_view = TracerouteView(self.notebook)
        self.notebook.AddPage(self.traceroute_view, "Trace Route")
        
        # Network Info
        self.network_info_view = NetworkInfoView(self.notebook)
        self.notebook.AddPage(self.network_info_view, "Network Info")
        
        # Speed Test
        self.speedtest_view = SpeedTestView(self.notebook)
        self.notebook.AddPage(self.speedtest_view, "Speed Test")
        
        # About
        self.about_view = AboutView(self.notebook)
        self.notebook.AddPage(self.about_view, "About")
        
    def _bind_events(self):
        """Bind event handlers to controls."""
        # Window events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Ping Test events
        self.ping_view.start_button.Bind(wx.EVT_BUTTON, self.on_start_ping)
        
        # Trace Route events
        self.traceroute_view.start_button.Bind(wx.EVT_BUTTON, self.on_start_trace)
        self.traceroute_view.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_trace)
        
        # Network Info events
        self.network_info_view.refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh_network_info)
        
        # Speed Test events
        self.speedtest_view.start_button.Bind(wx.EVT_BUTTON, self.on_start_speed_test)
        
    def on_close(self, event):
        """Handle application close event."""
        # Clean shutdown of thread pool
        logging.info("Application closing - shutting down all processes...")
        
        # Cancel any running tests
        if hasattr(self, 'trace_future') and not self.trace_future.done():
            logging.info("Cancelling running trace route test")
            self.trace_future.cancel()
        
        # Set flags to signal threads to terminate
        self.network_utils.shutdown()
        
        # Shutdown the thread pool with a short timeout to allow tasks to clean up
        try:
            logging.info("Shutting down thread pool...")
            self.executor.shutdown(wait=True, timeout=2)
        except TypeError:
            # For Python versions that don't support timeout parameter
            self.executor.shutdown(wait=False)
            
        # Kill any running subprocesses
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        for child in children:
            try:
                logging.info(f"Terminating child process: {child.pid}")
                child.terminate()
            except:
                pass
                
        # Prepare for console closure on Windows
        if platform.system() == 'Windows':
            def delayed_exit():
                """Delay exit to allow for cleanup"""
                import time
                time.sleep(0.2)  # Small delay
                try:
                    # Attempt to close the console before exiting
                    close_console()
                except:
                    pass
                finally:
                    # Force exit after delay
                    os._exit(0)
            
            import threading
            exit_thread = threading.Thread(target=delayed_exit)
            exit_thread.daemon = True
            exit_thread.start()
            
        logging.info("Application shutdown complete")
        
        # Use CallAfter to destroy the window after all events are processed
        wx.CallAfter(self.Destroy)
        
        # Allow the window to be closed
        event.Skip()
        
    def on_start_ping(self, event):
        """Start ping test."""
        # Get parameters
        target = self.ping_view.get_target()
        if not target:
            wx.MessageBox("Please enter a target IP or hostname", "Input Required", wx.OK | wx.ICON_INFORMATION)
            return
            
        params = self.ping_view.get_test_parameters()
        
        # Update UI
        self.ping_view.clear_results()
        self.ping_view.start_button.Disable()
        self.status_bar.SetStatusText(f"Running Ping Test to {target}...", 0)
        
        # Start background task
        def ping_task():
            try:
                # Update progress as the ping runs
                def progress_callback(value):
                    wx.CallAfter(self.ping_view.update_progress, value)
                
                # Run the ping test
                latency_data, packet_loss = self.network_utils.run_ping(
                    target, 
                    params['count'], 
                    params['interval'],
                    progress_callback
                )
                
                # Process and display results
                if latency_data is None:
                    wx.CallAfter(self.show_ping_results, None, 100.0, None)
                    return
                    
                valid_latencies = [lat for lat in latency_data if lat > 0]
                if valid_latencies:
                    stats = {
                        'avg_latency': sum(valid_latencies) / len(valid_latencies),
                        'min_latency': min(valid_latencies),
                        'max_latency': max(valid_latencies)
                    }
                else:
                    stats = {
                        'avg_latency': 0,
                        'min_latency': 0,
                        'max_latency': 0
                    }
                    
                wx.CallAfter(self.show_ping_results, latency_data, packet_loss, stats)
                
            except Exception as e:
                logging.error(f"Ping test error: {e}")
                wx.CallAfter(self.status_bar.SetStatusText, f"Error in ping test: {str(e)}", 0)
            finally:
                wx.CallAfter(self.ping_view.start_button.Enable)
        
        self.executor.submit(ping_task)
        
    def show_ping_results(self, latency_data, packet_loss, stats):
        """Show ping results in the UI."""
        # Update status bar
        self.status_bar.SetStatusText("Ping Test Complete", 0)
        
        # Update results view
        self.ping_view.update_results(latency_data, packet_loss, stats)
        
        # Show quality assessment
        if latency_data is None or not latency_data:
            quality = "poor"
            description = "Network is disconnected. Check your internet connection."
            self.ping_view.show_quality_assessment(quality, description)
            return
            
        # Get quality assessment
        avg_latency = stats['avg_latency'] if stats else 0
        quality, description, icon_name = self.network_utils.analyze_ping_results(avg_latency, packet_loss)
        
        # Load the icon if available
        icon_bitmap = None
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icons", icon_name)
            if os.path.exists(icon_path):
                icon_bitmap = wx.Bitmap(icon_path)
        except Exception as e:
            logging.warning(f"Could not load icon: {icon_name}, error: {e}")
            
        # Show the assessment
        self.ping_view.show_quality_assessment(quality, description, icon_bitmap)
        
    def on_start_trace(self, event):
        """Start trace route test."""
        # Get parameters
        target = self.traceroute_view.get_target()
        if not target:
            wx.MessageBox("Please enter a target IP or hostname", "Input Required", wx.OK | wx.ICON_INFORMATION)
            return
            
        max_hops = self.traceroute_view.get_max_hops()
        
        # Update UI
        self.traceroute_view.clear_results()
        self.traceroute_view.set_controls_state(True)  # Set to running state
        self.status_bar.SetStatusText(f"Running Trace Route to {target}...", 0)
        
        # Start background task
        def trace_task():
            try:
                # Run the trace with real-time updates
                output = self.network_utils.run_trace_route(
                    target, 
                    max_hops,
                    lambda line: wx.CallAfter(self.traceroute_view.update_trace_output, line)
                )
                
                # Process completed trace
                if "Error" in output:
                    wx.CallAfter(
                        self.traceroute_view.show_notification,
                        f"Trace route failed: {output}",
                        "error"
                    )
                elif "timeout" in output.lower():
                    wx.CallAfter(
                        self.traceroute_view.show_notification,
                        "Trace route timed out. The target may be unreachable.",
                        "warning"
                    )
                else:
                    # Analyze for high-latency hops
                    high_latency = any("ms" in line and any(int(val) > 100 for val in line.split() if val.isdigit()) for line in output.splitlines())
                    if high_latency:
                        wx.CallAfter(
                            self.traceroute_view.show_notification,
                            "High-latency hops detected in the route. Highlighted in orange.",
                            "warning"
                        )
                    else:
                        wx.CallAfter(
                            self.traceroute_view.show_notification,
                            "Trace route completed successfully with good latency.",
                            "success"
                        )
                
            except Exception as e:
                logging.error(f"Trace route error: {e}")
                wx.CallAfter(
                    self.traceroute_view.show_notification,
                    f"Error: {str(e)}",
                    "error"
                )
            finally:
                wx.CallAfter(self.status_bar.SetStatusText, "Trace Route Complete", 0)
                wx.CallAfter(self.traceroute_view.set_controls_state, False)  # Set to not running
                
        self.trace_future = self.executor.submit(trace_task)
        
    def on_cancel_trace(self, event):
        """Cancel a running trace route."""
        if hasattr(self, 'trace_future') and not self.trace_future.done():
            self.trace_future.cancel()
            self.status_bar.SetStatusText("Trace Route Cancelled", 0)
            self.traceroute_view.set_controls_state(False)
            self.traceroute_view.show_notification("Trace route cancelled by user", "info")
        
    def _load_network_info(self):
        """Load network information in the background."""
        self.network_info_view.set_loading_state(True)
        
        def get_network_info_task():
            try:
                # Get network information
                info = self.network_utils.get_network_info()
                
                # Update UI with the information
                wx.CallAfter(self.network_info_view.update_network_info, info)
                wx.CallAfter(self.status_bar.SetStatusText, "Network Information Loaded", 0)
            except Exception as e:
                logging.error(f"Error loading network info: {e}")
                wx.CallAfter(
                    self.network_info_view.show_notification,
                    f"Error loading network information: {str(e)}",
                    "error"
                )
                wx.CallAfter(self.status_bar.SetStatusText, "Error Loading Network Info", 0)
            finally:
                wx.CallAfter(self.network_info_view.set_loading_state, False)
                
        self.executor.submit(get_network_info_task)
        
    def on_refresh_network_info(self, event):
        """Refresh network information."""
        self._load_network_info()
        
    def on_start_speed_test(self, event):
        """Start speed test."""
        # Get selected server
        selected_server = self.speedtest_view.get_selected_server()
        
        # Update UI
        self.speedtest_view.clear_results()
        self.speedtest_view.set_testing_state(True)
        self.status_bar.SetStatusText("Running Speed Test...", 0)
        self.status_bar.SetStatusText("Testing Internet Connection", 1)
        
        # Start background task
        def speed_test_task():
            try:
                # Progress callback for UI updates
                def progress_callback(value, message):
                    wx.CallAfter(self.speedtest_view.update_progress, value, message)
                    # Update status bar with current activity
                    if "Testing ping" in message:
                        wx.CallAfter(self.status_bar.SetStatusText, "Testing Ping", 1)
                    elif "Testing download" in message:
                        wx.CallAfter(self.status_bar.SetStatusText, "Testing Download", 1)
                    elif "Testing upload" in message:
                        wx.CallAfter(self.status_bar.SetStatusText, "Testing Upload", 1)
                    elif "No internet" in message:
                        wx.CallAfter(self.status_bar.SetStatusText, "No Internet Connection", 1)
                
                # Run the speed test with selected server
                download, upload, ping = self.network_utils.run_speed_test(
                    progress_callback,
                    selected_server
                )
                
                # Update UI with results
                wx.CallAfter(self.speedtest_view.update_speed_results, download, upload, ping)
                
                # Show quality assessment
                if download is not None and upload is not None:
                    quality, description, icon_name = self.network_utils.analyze_speed_test_results(
                        download, upload
                    )
                    
                    # Load the icon if available
                    icon_bitmap = None
                    try:
                        icon_path = os.path.join(os.path.dirname(__file__), "icons", icon_name)
                        if os.path.exists(icon_path):
                            icon_bitmap = wx.Bitmap(icon_path)
                    except Exception as e:
                        logging.warning(f"Could not load icon: {icon_name}, error: {e}")
                        
                    wx.CallAfter(
                        self.speedtest_view.show_quality_assessment,
                        quality,
                        description,
                        icon_bitmap
                    )
                else:
                    # Handle offline case with more detailed message
                    try:
                        # Attempt a basic connectivity check
                        internet_available = self.network_utils._check_internet_connectivity()
                        
                        if internet_available:
                            message = "Speed test failed. Your internet connection appears to be active but unreliable. Try again or select a different server."
                        else:
                            message = "Speed test failed. No internet connection detected. Check your network settings and connection."
                            
                        wx.CallAfter(
                            self.speedtest_view.show_quality_assessment,
                            "poor",
                            message,
                            None
                        )
                        
                    except Exception:
                        # Fallback message if connectivity check fails
                        wx.CallAfter(
                            self.speedtest_view.show_quality_assessment,
                            "poor",
                            "Speed test failed. Check your internet connection and try again.",
                            None
                        )
                    
            except Exception as e:
                logging.error(f"Speed test error: {e}")
                wx.CallAfter(self.status_bar.SetStatusText, f"Error in speed test: {str(e)}", 0)
                
                # Show error message in UI
                wx.CallAfter(
                    self.speedtest_view.show_quality_assessment,
                    "poor",
                    f"Speed test error: {str(e)}. Please try again later.",
                    None
                )
            finally:
                wx.CallAfter(self.speedtest_view.set_testing_state, False)
                wx.CallAfter(self.status_bar.SetStatusText, "Speed Test Complete", 0)
                wx.CallAfter(self.status_bar.SetStatusText, "No Active Test", 1)
                
        self.executor.submit(speed_test_task)


def main():
    """Application entry point."""
    # Hide console window in Windows when running from .py file
    if platform.system() == 'Windows':
        try:
            # Hide the console window by changing the window style
            import win32gui
            import win32con
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        except ImportError:
            # Fallback if win32gui is not available - use ctypes
            try:
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            except:
                logging.warning("Could not hide console window")
    
    # Create icons directory if it doesn't exist
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    if not os.path.exists(icons_dir):
        try:
            os.makedirs(icons_dir)
            logging.info(f"Created icons directory: {icons_dir}")
        except Exception as e:
            logging.error(f"Failed to create icons directory: {e}")
    
    app = wx.App()
    frame = NetworkDiagnosticApp()
    
    # Register app exit handler
    app.SetExitOnFrameDelete(True)
    
    # Set frame as top window
    app.SetTopWindow(frame)
    
    # Start the main loop
    app.MainLoop()
    
    # Force close the console window on Windows
    if platform.system() == 'Windows':
        try:
            logging.info("Closing console window...")
            close_console()
        except Exception as e:
            logging.error(f"Error closing console: {e}")
    
    # Ensure clean exit after main loop ends
    sys.exit(0)


if __name__ == "__main__":
    main() 