import logging
import time
import socket
import platform
import subprocess
import ipaddress
import re
import psutil
from ping3 import ping
import speedtest
import pyspeedtest
from concurrent.futures import ThreadPoolExecutor
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("network_checker.log"),
        logging.StreamHandler()
    ]
)

class NetworkValidator:
    """Utilities for validating network addresses and hostnames."""
    
    @staticmethod
    def validate_ip(ip_address):
        """Validate if the given string is a valid IP address."""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def resolve_hostname(hostname):
        """Resolve a hostname to an IP address."""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

class NetworkUtils:
    """Core network utility functions."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._shutdown_requested = False
        
    def shutdown(self):
        """Shutdown the executor and stop all running threads properly."""
        logging.info("NetworkUtils: Shutting down all network operations")
        self._shutdown_requested = True
        
        # Shutdown the executor properly
        try:
            self.executor.shutdown(wait=True, timeout=3)
        except TypeError:
            # For Python versions that don't support timeout parameter
            self.executor.shutdown(wait=False)
            
        logging.info("NetworkUtils: Shutdown complete")
    
    def run_ping(self, target, count=10, interval=1, callback=None):
        """
        Run a ping test to the specified target.
        
        Args:
            target: IP address or hostname to ping
            count: Number of pings to send
            interval: Time interval between pings in seconds
            callback: Optional callback function to update progress
            
        Returns:
            Tuple of (latency_data, packet_loss_percent)
        """
        if not NetworkValidator.validate_ip(target):
            resolved_ip = NetworkValidator.resolve_hostname(target)
            if not resolved_ip:
                return None, 100.0
            target = resolved_ip

        latency_data = []
        lost_packets = 0

        for i in range(count):
            try:
                if callback:
                    callback(i / count * 100)
                    
                delay = ping(target, timeout=2)
                if delay is None:
                    lost_packets += 1
                    latency_data.append(0)
                else:
                    latency_data.append(delay * 1000)  # Convert to ms
            except Exception as e:
                logging.error(f"Ping error for {target}: {e}")
                lost_packets += 1
                latency_data.append(0)
            time.sleep(interval)
        
        if callback:
            callback(100)
            
        packet_loss_percent = (lost_packets / count) * 100
        return latency_data, packet_loss_percent

    def run_trace_route(self, target, max_hops=35, update_ui_callback=None):
        """
        Run a traceroute to the specified target.
        
        Args:
            target: IP address or hostname to trace
            max_hops: Maximum number of hops to trace
            update_ui_callback: Optional callback to update UI with real-time output
            
        Returns:
            String containing the trace route output
        """
        if platform.system() == "Windows":
            command = ["tracert", "-h", str(max_hops), target]
        else:
            command = ["traceroute", "-m", str(max_hops), target]

        process = None
        try:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1, 
                universal_newlines=True
            )
            
            output = []
            while True:
                if self._shutdown_requested:
                    # If shutdown requested, terminate the process
                    if process:
                        try:
                            process.terminate()
                            return "Trace route cancelled due to application shutdown"
                        except:
                            pass
                
                line = process.stdout.readline()
                if not line:
                    break
                # Replace non-numeric values (like '<1') with '0' for processing
                line = re.sub(r'<\d+', '0', line)
                if update_ui_callback and not self._shutdown_requested:
                    update_ui_callback(line.strip() + '\n')
                output.append(line)

            process.wait()
            if process.returncode != 0:
                error_message = process.stderr.read()
                logging.error(f"Trace route error for {target}: {error_message}")
                return f"Error: {error_message}"
            return "".join(output)
        except subprocess.TimeoutExpired:
            # Terminate the process if timeout expired
            if process:
                try:
                    process.terminate()
                except:
                    pass
            return "Trace route timed out after 60 seconds"
        except Exception as e:
            # Terminate the process in case of any other exception
            if process:
                try:
                    process.terminate()
                except:
                    pass
            logging.error(f"Trace route error for {target}: {e}")
            return f"Error: {e}"

    def get_network_info(self):
        """
        Get detailed information about the current network configuration.
        
        Returns:
            Dictionary containing network information
        """
        info = {}
        try:
            # Get the hostname
            info['hostname'] = socket.gethostname()

            # Get the local IP (LAN)
            interfaces = psutil.net_if_addrs()
            local_ip = None
            for iface, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                        local_ip = addr.address
                        break
                if local_ip:
                    break
            info['local_ip'] = local_ip if local_ip else "Local IP not found"

            # Get the public IP (WAN)
            try:
                import requests
                public_ip = requests.get("https://api.ipify.org", timeout=5).text
                info['public_ip'] = public_ip
            except Exception as e:
                logging.error(f"Error retrieving public IP: {e}")
                info['public_ip'] = "Public IP not accessible"

            # Get DNS Resolvers
            info['dns_resolvers'] = self.get_dns_resolvers()

            # Get network interfaces information
            info['interfaces'] = {
                iface: [addr.address for addr in addrs if addr.family == socket.AF_INET]
                for iface, addrs in interfaces.items()
            }

            # Get the default gateway
            default_gateway = None
            net_connections = psutil.net_if_stats()
            for iface, stats in net_connections.items():
                if stats.isup:
                    default_gateway = iface
                    break
            info['default_gateway'] = default_gateway if default_gateway else "Default gateway not found"
            
        except Exception as e:
            logging.error(f"Error retrieving network info: {e}")
            info['error'] = str(e)

        return info

    def get_dns_resolvers(self):
        """
        Get the DNS resolvers configured on the system.
        
        Returns:
            List of DNS resolver IP addresses
        """
        resolvers = []
        try:
            if platform.system() == "Windows":
                # Use ipconfig to get DNS servers
                result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
                output = result.stdout
                for line in output.splitlines():
                    if "DNS Servers" in line or "DNS-Server" in line:
                        resolver = line.split(":")[-1].strip()
                        if resolver:
                            resolvers.append(resolver)
            else:
                # For Linux/Unix, read from /etc/resolv.conf
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            resolvers.append(line.split()[1])
        except Exception as e:
            logging.error(f"Error retrieving DNS resolvers: {e}")
        return resolvers

    def run_speed_test(self, progress_callback=None, selected_server="auto"):
        """
        Run an internet speed test using direct downloads from reliable CDN servers.
        Uses a simplified approach with better error handling.
        
        Args:
            progress_callback: Optional callback function to update progress
            selected_server: Server URL to use for testing, "auto" for automatic selection
            
        Returns:
            Tuple of (download_speed, upload_speed, ping_latency) in Mbps
        """
        try:
            logging.info("Starting speed test...")
            
            if progress_callback:
                progress_callback(5, "Starting speed test...")
            
            # Standard modules only, to minimize dependencies
            import requests
            import time
            import threading
            import random
            import string
            from urllib.parse import urlparse
            
            # Use a session with timeout and headers
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            })

            # Define reliable test servers with direct download links
            # Using standard content delivery networks (CDNs)
            download_servers = [
                {
                    "name": "Cloudflare", 
                    "url": "https://speed.cloudflare.com/__down?bytes=5000000",
                    "size": 5 * 1024 * 1024  # 5 MB - smaller file for better reliability
                },
                {
                    "name": "Google", 
                    "url": "https://www.gstatic.com/generate_204",
                    "size": 204  # Very small file for ping test
                }
            ]
            
            # Test ping to a reliable server
            logging.info("Testing ping latency...")
            if progress_callback:
                progress_callback(10, "Testing network latency...")
            
            ping_urls = [
                "https://www.google.com",
                "https://www.cloudflare.com",
                "https://www.amazon.com"
            ]
            
            ping_results = []
            for url in ping_urls:
                try:
                    start_time = time.time()
                    response = session.head(url, timeout=2)
                    latency = (time.time() - start_time) * 1000  # ms
                    if response.status_code < 400:
                        ping_results.append(latency)
                        logging.info(f"Ping to {url}: {latency:.1f} ms")
                except Exception as e:
                    logging.error(f"Error pinging {url}: {str(e)}")
            
            # Calculate average ping
            if ping_results:
                ping_latency = sum(ping_results) / len(ping_results)
                if progress_callback:
                    progress_callback(15, f"Network latency: {ping_latency:.1f} ms")
            else:
                ping_latency = None
                if progress_callback:
                    progress_callback(15, "Unable to measure network latency")
                logging.warning("Could not measure ping latency to any server")
            
            # Download test
            logging.info("Starting download speed test...")
            if progress_callback:
                progress_callback(20, "Testing download speed...")
            
            # Try multiple servers until one works
            download_urls = [
                "https://speed.cloudflare.com/__down?bytes=10000000",  # 10MB from Cloudflare
                "https://ftp.halifax.rwth-aachen.de/random/10MB.dat",  # 10MB from RWTH Aachen
                "https://speed.hetzner.de/10MB.bin"  # 10MB from Hetzner
            ]
            
            download_results = []
            
            def run_download_test(url, size_estimate=10000000):
                try:
                    logging.info(f"Download test: Starting download from {url}")
                    start_time = time.time()
                    
                    try:
                        response = session.get(url, stream=True, timeout=15)
                    except Exception as e:
                        logging.error(f"Error connecting to download server {url}: {str(e)}")
                        return None
                    
                    if response.status_code != 200:
                        logging.error(f"Download test failed: HTTP {response.status_code} from {url}")
                        return None
                    
                    downloaded = 0
                    download_start = time.time()  # Start time after connection established
                    current_speed = 0
                    
                    try:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                downloaded += len(chunk)
                                # Update real-time progress
                                elapsed = time.time() - download_start
                                if elapsed > 0:
                                    current_speed = (downloaded * 8) / (elapsed * 1000000)  # Mbps
                                    if progress_callback:
                                        progress_callback(30, f"Download speed: {current_speed:.2f} Mbps")
                                
                                # If downloaded > 4MB, we have enough data for an accurate test
                                if downloaded > 4 * 1024 * 1024:
                                    break
                    except Exception as e:
                        logging.error(f"Error during download from {url}: {str(e)}")
                        if downloaded < 1024 * 1024:  # Less than 1MB
                            return None
                    
                    total_time = time.time() - download_start
                    if total_time < 0.1 or downloaded < 100 * 1024:  # Too fast or too small
                        logging.warning(f"Download from {url} was too small or too fast: {downloaded} bytes in {total_time:.2f}s")
                        return None
                        
                    speed_mbps = (downloaded * 8) / (total_time * 1000000)  # Convert to Mbps
                    logging.info(f"Download test completed: {speed_mbps:.2f} Mbps, {downloaded/1024/1024:.1f}MB in {total_time:.1f}s")
                    return speed_mbps
                except Exception as e:
                    logging.error(f"Download test error with {url}: {str(e)}")
                    return None
            
            # Try each download URL until we get a valid result
            successful_download = False
            for url in download_urls:
                if progress_callback:
                    progress_callback(25, f"Testing download server...")
                
                result = run_download_test(url)
                if result:
                    download_results.append(result)
                    successful_download = True
                    break
            
            # Calculate final download speed
            if download_results:
                download_speed = sum(download_results) / len(download_results)
                if progress_callback:
                    progress_callback(50, f"Download speed: {download_speed:.2f} Mbps")
            else:
                download_speed = None
                if progress_callback:
                    progress_callback(50, "Unable to calculate download speed")
                logging.warning("Could not calculate download speed - no successful tests")
            
            # Upload test
            logging.info("Starting upload speed test...")
            if progress_callback:
                progress_callback(60, "Testing upload speed...")
            
            # Try multiple upload servers
            upload_urls = [
                "https://httpbin.org/post",
                "https://postman-echo.com/post"
            ]
            
            upload_sizes = [2 * 1024 * 1024]  # 2MB - smaller for reliability
            upload_results = []
            
            def run_upload_test(url, size):
                try:
                    # Generate random data
                    logging.info(f"Upload test: Generating {size/1024/1024:.1f}MB of test data")
                    data = ''.join(random.choices(string.ascii_letters + string.digits, k=size)).encode()
                    
                    logging.info(f"Upload test: Starting upload of {size/1024/1024:.1f}MB to {url}")
                    start_time = time.time()
                    
                    try:
                        response = session.post(
                            url, 
                            data=data,
                            headers={'Content-Type': 'application/octet-stream'},
                            timeout=15
                        )
                    except Exception as e:
                        logging.error(f"Error connecting to upload server {url}: {str(e)}")
                        return None
                    
                    if response.status_code >= 400:
                        logging.error(f"Upload test failed: HTTP {response.status_code} from {url}")
                        return None
                    
                    total_time = time.time() - start_time
                    speed_mbps = (size * 8) / (total_time * 1000000)  # Convert to Mbps
                    logging.info(f"Upload test completed: {speed_mbps:.2f} Mbps, {size/1024/1024:.1f}MB in {total_time:.1f}s")
                    return speed_mbps
                except Exception as e:
                    logging.error(f"Upload test error with {url}: {str(e)}")
                    return None
            
            # Try each upload URL until we get a valid result
            successful_upload = False
            for url in upload_urls:
                if progress_callback:
                    progress_callback(70, f"Testing upload server...")
                
                for size in upload_sizes:
                    result = run_upload_test(url, size)
                    if result:
                        upload_results.append(result)
                        successful_upload = True
                        break
                
                if successful_upload:
                    break
            
            # Calculate final upload speed
            if upload_results:
                upload_speed = sum(upload_results) / len(upload_results)
                if progress_callback:
                    progress_callback(90, f"Upload speed: {upload_speed:.2f} Mbps")
            else:
                upload_speed = None
                if progress_callback:
                    progress_callback(90, "Unable to calculate upload speed")
                logging.warning("Could not calculate upload speed - no successful tests")
            
            # Process complete results
            if progress_callback:
                progress_callback(95, "Processing results...")
                
            if download_speed is not None or upload_speed is not None:
                download_str = f"{download_speed:.2f} Mbps" if download_speed is not None else "Unknown"
                upload_str = f"{upload_speed:.2f} Mbps" if upload_speed is not None else "Unknown"
                ping_str = f"{ping_latency:.1f} ms" if ping_latency is not None else "Unknown"
                
                result_message = f"Results: Download {download_str}, Upload {upload_str}, Ping {ping_str}"
                logging.info(f"Speed test complete: Download={download_str}, Upload={upload_str}, Ping={ping_str}")
                if progress_callback:
                    progress_callback(100, result_message)
            else:
                error_message = "Unable to complete speed test. Please check your connection."
                logging.error("Speed test failed to complete")
                if progress_callback:
                    progress_callback(100, error_message)
            
            return download_speed, upload_speed, ping_latency
            
        except Exception as e:
            # Log full exception with stack trace for debugging
            logging.error(f"Speed test critical error: {str(e)}")
            logging.error(f"Stack trace: {traceback.format_exc()}")
            if progress_callback:
                progress_callback(100, f"Speed test error: {str(e)}")
            return None, None, None
            
    # Add a more thorough connectivity check
    def _check_internet_connectivity(self):
        """
        Check if internet is available
        
        Returns:
            bool: True if internet is available, False otherwise
        """
        logging.info("Checking internet connectivity...")
        try:
            # Try multiple reliable hosts
            for host in ["www.google.com", "www.cloudflare.com", "1.1.1.1"]:
                try:
                    import socket
                    socket.create_connection((host, 80), timeout=2)
                    logging.info(f"Internet connection available (connected to {host})")
                    return True
                except:
                    continue
                    
            # If socket connection fails, try a HTTP request
            try:
                import requests
                response = requests.get("https://www.google.com", timeout=2)
                if response.status_code < 400:
                    logging.info("Internet connection available (HTTP request succeeded)")
                    return True
            except:
                pass
                
            logging.warning("Internet connection unavailable - all connectivity checks failed")
            return False
        except Exception as e:
            logging.error(f"Error checking internet connectivity: {str(e)}")
            return False

    def analyze_ping_results(self, avg_latency, packet_loss):
        """
        Analyze ping results and provide a quality assessment.
        
        Args:
            avg_latency: Average latency in ms
            packet_loss: Packet loss percentage
            
        Returns:
            Tuple of (quality_level, description, icon_name)
        """
        if packet_loss > 20:
            return "poor", "Network quality is poor! High packet loss indicates connection issues.", "poor_network.png"
            
        if avg_latency < 50:
            return "excellent", "Network quality is excellent (Low latency). Suitable for gaming, video calls, and streaming.", "excellent_network.png"
        elif avg_latency < 100:
            return "good", "Network quality is good. Should support most online activities with minimal delay.", "good_network.png"
        elif avg_latency < 200:
            return "moderate", "Network quality is moderate! Video calls and gaming may experience noticeable delay.", "moderate_network.png"
        else:
            return "poor", "Network quality is poor! High latency may disrupt real-time applications.", "poor_network.png"

    def analyze_speed_test_results(self, download, upload):
        """
        Analyze speed test results and provide a quality assessment.
        
        Args:
            download: Download speed in Mbps
            upload: Upload speed in Mbps
            
        Returns:
            Tuple of (quality_level, description, icon_name)
        """
        if download >= 50:
            return "excellent", "Excellent internet speed. Suitable for 4K streaming, large file transfers, and online gaming.", "excellent_network.png"
        elif download >= 20:
            return "good", "Good internet speed. Suitable for HD streaming and most online activities.", "good_network.png"
        elif download >= 10:
            return "moderate", "Moderate internet speed. Suitable for standard definition streaming and general web browsing.", "moderate_network.png"
        else:
            return "poor", "Poor internet speed. May experience buffering during streaming and slow file transfers.", "poor_network.png" 