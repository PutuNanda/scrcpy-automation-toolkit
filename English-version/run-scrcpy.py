import os
import subprocess
import time
import sys
import threading
import json

# Epic Color Palette 🎨
class Colors:
    PRIMARY = '\033[96m'    # Soft Cyan
    SUCCESS = '\033[92m'    # Soft Green
    WARNING = '\033[93m'    # Soft Yellow
    ERROR = '\033[91m'      # Soft Red
    DEVICE = '\033[95m'     # Soft Magenta
    PORT = '\033[94m'       # Soft Blue
    DIM = '\033[90m'        # Gray
    BOLD = '\033[1m'        # Bold
    RESET = '\033[0m'

class ScrcpyManager:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.setup_environment()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"{Colors.SUCCESS}✅ Configuration loaded successfully{Colors.RESET}")
            return config
        except Exception as e:
            print(f"{Colors.ERROR}❌ Failed to load configuration: {e}{Colors.RESET}")
            sys.exit(1)
    
    def setup_environment(self):
        """Setup scrcpy environment and PATH"""
        scrcpy_folder = self.config.get("scrcpy_folder", "scrcpy-win64-v3.2")
        
        if os.path.exists(scrcpy_folder):
            os.chdir(scrcpy_folder)
            # Add current directory to PATH for adb and scrcpy
            os.environ['PATH'] = os.getcwd() + os.pathsep + os.environ['PATH']
            print(f"{Colors.SUCCESS}✅ scrcpy environment setup at: {os.getcwd()}{Colors.RESET}")
        else:
            print(f"{Colors.ERROR}❌ scrcpy folder not found: {scrcpy_folder}{Colors.RESET}")
            sys.exit(1)

    def run_command(self, cmd, silent=False):
        """Run command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if not silent and result.stdout.strip():
                print(f"{Colors.DIM}↳ {result.stdout.strip()}{Colors.RESET}")
            return result.stdout
        except Exception as e:
            if not silent:
                print(f"{Colors.ERROR}↳ Error: {e}{Colors.RESET}")
            return ""

    def print_step(self, step, message):
        """Print clean step message"""
        print(f"{Colors.PRIMARY}[{step}] {message}{Colors.RESET}")

    def print_big_message(self, message, color, icon="✨"):
        """Print big epic message"""
        print(f"\n{color}{Colors.BOLD}{icon} {'═' * 50}{icon}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}   {message}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{icon} {'═' * 50}{icon}{Colors.RESET}\n")

    def print_device_info(self, devices_output):
        """Print clean device information"""
        lines = devices_output.strip().split('\n')
        
        print(f"{Colors.DIM}╔══════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.DIM}║           📱 AVAILABLE DEVICES          ║{Colors.RESET}")
        print(f"{Colors.DIM}╚══════════════════════════════════════════╗{Colors.RESET}")
        
        for line in lines[1:]:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    device_id = parts[0].strip()
                    status = parts[1].strip()
                    
                    if status == 'device':
                        status_color = Colors.SUCCESS
                        status_icon = "✅"
                    elif status == 'offline':
                        status_color = Colors.WARNING
                        status_icon = "⚠️"
                    else:
                        status_color = Colors.ERROR
                        status_icon = "❌"
                    
                    if ':' in device_id:
                        ip, port = device_id.split(':')
                        device_display = f"{Colors.DEVICE}{ip}{Colors.RESET}:{Colors.PORT}{port}{Colors.RESET}"
                    else:
                        device_display = f"{Colors.DEVICE}{device_id}{Colors.RESET}"
                    
                    print(f"{Colors.DIM}║ {status_icon} {device_display} {status_color}{status}{Colors.RESET}{Colors.DIM} ║{Colors.RESET}")
        
        print(f"{Colors.DIM}╚══════════════════════════════════════════╝{Colors.RESET}")

    def find_usb_device(self):
        """Find USB device by ID or name"""
        devices_output = self.run_command("adb devices -l", silent=True)
        
        # Search by device_id
        if self.config["device_id"] in devices_output and "device" in devices_output:
            return self.config["device_id"]
        
        # Search by device_name
        if self.config["device_name"] in devices_output:
            lines = devices_output.strip().split('\n')
            for line in lines:
                if self.config["device_name"] in line and "device" in line:
                    parts = line.split()
                    if parts:
                        return parts[0]
        
        return None

    def setup_usb_connection(self):
        """Setup USB connection and enable TCP/IP mode"""
        print(f"{Colors.WARNING}  ↳ Trying USB connection...{Colors.RESET}")
        
        usb_device = self.find_usb_device()
        
        if usb_device:
            print(f"{Colors.SUCCESS}    ✅ USB device detected: {usb_device}{Colors.RESET}")
            print(f"{Colors.WARNING}    ↳ Enabling TCP/IP mode...{Colors.RESET}")
            
            self.run_command(f"adb -s {usb_device} tcpip {self.config['port']}", silent=True)
            time.sleep(3)
            
            return True
        else:
            print(f"{Colors.ERROR}    ❌ USB device not detected{Colors.RESET}")
            return False

    def connect_with_timeout(self, connection_name, connection_ip, timeout=None):
        """Try to connect with timeout and REAL verification"""
        if timeout is None:
            timeout = int(self.config.get("timeout_delay", 3))
            
        print(f"  ↳ Trying {connection_name}...")
        
        # Disconnect first to clean state
        self.run_command(f"adb disconnect {connection_ip}", silent=True)
        time.sleep(0.5)
        
        def connect():
            self.run_command(f"adb connect {connection_ip}", silent=True)
        
        # Run connect in separate thread
        thread = threading.Thread(target=connect)
        thread.start()
        thread.join(timeout)
        
        # Give time for device list update
        time.sleep(1)
        
        # REAL VERIFICATION - check if it's actually a device (not offline)
        new_devices = self.run_command("adb devices", silent=True)
        
        # Check if IP exists and status is DEVICE (not offline)
        if connection_ip in new_devices and f"{connection_ip}\tdevice" in new_devices:
            ip, port = connection_ip.split(':')
            print(f"{Colors.SUCCESS}    ✅ Connected to {Colors.DEVICE}{ip}{Colors.SUCCESS}:{Colors.PORT}{port}{Colors.SUCCESS}{Colors.RESET}")
            return True
        else:
            # Cleanup if failed
            self.run_command(f"adb disconnect {connection_ip}", silent=True)
            print(f"{Colors.WARNING}    ⏰ Timeout {timeout}s - Moving to next mode...{Colors.RESET}")
            return False

    def get_connection_methods(self):
        """Get connection methods based on priority configuration"""
        priority = self.config.get("priority", ["tailscale", "local-ip", "usb"])
        methods = []
        
        for method in priority:
            if method == "tailscale":
                methods.append((
                    "🌐 TAILSCALE", 
                    f"{self.config['tailscale_ip']}:{self.config['port']}",
                    "tailscale"
                ))
            elif method == "local-ip":
                methods.append((
                    "📡 LOCAL WIFI", 
                    f"{self.config['local_ip']}:{self.config['port']}",
                    "wifi"
                ))
            elif method == "usb":
                methods.append((
                    "🔌 USB DIRECT", 
                    self.find_usb_device(),
                    "usb"
                ))
        
        return methods

    def parse_scrcpy_output(self, line):
        """Parse and style scrcpy output lines"""
        line = line.strip()
        
        # Filter and style only desired information
        if "Device: [" in line and "]" in line:
            # INFO: Device: [TECNO] TECNO TECNO LG7n (Android 12)
            device_info = line.split("Device: ", 1)[1]
            return f"{Colors.PRIMARY}📱 Device: {Colors.DEVICE}{device_info}{Colors.RESET}"
        
        elif "Texture:" in line:
            # INFO: Texture: 448x1024
            resolution = line.split("Texture: ", 1)[1]
            return f"{Colors.PRIMARY}🖼️  Resolution: {Colors.PORT}{resolution}{Colors.RESET}"
        
        elif "server" in line and "Device: [" in line:
            # [server] INFO: Device: [TECNO] TECNO TECNO LG7n (Android 12)
            device_info = line.split("Device: ", 1)[1]
            return f"{Colors.PRIMARY}📱 Device: {Colors.DEVICE}{device_info}{Colors.RESET}"
        
        return None

    def run_scrcpy_with_filtered_output(self, device_ip):
        """Run scrcpy with filtered and styled output"""
        try:
            process = subprocess.Popen(
                f"scrcpy -s {device_ip} --no-audio --max-size 1024",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read real-time output
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Parse and display only desired information
                styled_line = self.parse_scrcpy_output(line)
                if styled_line:
                    print(styled_line)
                    
                # Check if process has terminated
                if process.poll() is not None:
                    break
                    
            return process.wait()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}👋 Mirroring stopped{Colors.RESET}")
            if process:
                process.terminate()
            sys.exit(0)
        except Exception as e:
            print(f"{Colors.ERROR}↳ Error: {e}{Colors.RESET}")
            return 1

    def main(self):
        print(f"\n{Colors.PRIMARY}✨ SCRCPY ULTIMATE CONNECTOR ✨{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

        # [1] Scanning devices
        self.print_step("1", "Scanning devices...")
        devices_output = self.run_command("adb devices", silent=True)
        self.print_device_info(devices_output)

        # [2] Preparation - Setup USB if needed
        self.print_step("2", "Preparing connection...")
        
        usb_device = self.find_usb_device()
        usb_detected = usb_device is not None
        
        # Check if USB setup needed (only if USB device exists and wireless is offline)
        wireless_offline = (
            f"{self.config['tailscale_ip']}:{self.config['port']}" in devices_output and "offline" in devices_output or
            f"{self.config['local_ip']}:{self.config['port']}" in devices_output and "offline" in devices_output
        )
        
        if wireless_offline and usb_detected:
            print(f"{Colors.WARNING}  ↳ Wireless device offline, trying USB...{Colors.RESET}")
            if self.setup_usb_connection():
                time.sleep(2)
                devices_output = self.run_command("adb devices", silent=True)
                self.print_device_info(devices_output)

        # [3] CONNECTION SYSTEM BASED ON PRIORITY
        self.print_step("3", f"Priority connection system ({', '.join(self.config['priority'])})...")
        
        connection_methods = self.get_connection_methods()
        connected = False
        
        for connection_name, connection_target, connection_type in connection_methods:
            if connection_type == "usb":
                # USB connection
                print(f"  ↳ Trying {connection_name}...")
                if usb_detected:
                    self.print_big_message("CONNECTED TO USB", Colors.WARNING, "🔌")
                    print(f"{Colors.WARNING}💡 WARNING: Unlock your device!{Colors.RESET}")
                    print(f"{Colors.WARNING}   ↳ Enter PIN/pattern/password{Colors.RESET}")
                    print(f"{Colors.WARNING}   ↳ Or open with face unlock{Colors.RESET}")
                    
                    connected = True
                    self.run_scrcpy(connection_target, connection_type)
                    return
                else:
                    print(f"{Colors.ERROR}    ❌ USB device not detected{Colors.RESET}")
            else:
                # Wireless connection (Tailscale/Local IP)
                if self.connect_with_timeout(connection_name, connection_target):
                    color = Colors.SUCCESS if connection_type == "tailscale" else Colors.PRIMARY
                    icon = "🌐" if connection_type == "tailscale" else "📡"
                    self.print_big_message(f"CONNECTED TO {connection_name.split()[1]}", color, icon)
                    connected = True
                    self.run_scrcpy(connection_target, connection_type)
                    return

        if not connected:
            print(f"{Colors.ERROR}  ❌ No devices could be reached{Colors.RESET}")
            print(f"{Colors.WARNING}  ↳ Retrying in 5 seconds...{Colors.RESET}")
            time.sleep(5)
            self.main()

    def run_scrcpy(self, device_ip, connection_type):
        if ':' in device_ip:
            ip, port = device_ip.split(':')
            display_text = f"{Colors.DEVICE}{ip}{Colors.RESET}:{Colors.PORT}{port}{Colors.RESET}"
        else:
            display_text = f"{Colors.DEVICE}{device_ip}{Colors.RESET}"
        
        # Connection type styling
        type_styles = {
            "tailscale": f"{Colors.SUCCESS}Tailscale{Colors.RESET}",
            "wifi": f"{Colors.PRIMARY}Local WiFi{Colors.RESET}", 
            "usb": f"{Colors.WARNING}USB Direct{Colors.RESET}"
        }
        
        print(f"\n{Colors.SUCCESS}🎯 CONNECTION SUCCESSFUL{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
        print(f"{Colors.PRIMARY}📍 Device: {display_text}{Colors.RESET}")
        print(f"{Colors.PRIMARY}🔗 Type: {type_styles[connection_type]}{Colors.RESET}")
        print(f"{Colors.DIM}⏹️  Press Ctrl+C to stop{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

        connection_count = 0
        auto_reconnect_delay = int(self.config.get("auto_reconnect_delay", 3))
        
        while True:
            connection_count += 1
            print(f"\n{Colors.PRIMARY}🔄 Starting mirroring... ({connection_count}){Colors.RESET}")
            
            # Run scrcpy with filtered output
            return_code = self.run_scrcpy_with_filtered_output(device_ip)

            print(f"\n{Colors.WARNING}⚠️  Connection lost{Colors.RESET}")
            print(f"{Colors.DIM}↳ Reconnecting in {auto_reconnect_delay} seconds...{Colors.RESET}")
            
            for i in range(auto_reconnect_delay, 0, -1):
                print(f"{Colors.DIM}   {i}...{Colors.RESET}", end=' ', flush=True)
                time.sleep(1)
            print()

if __name__ == "__main__":
    try:
        manager = ScrcpyManager()
        manager.main()
    except KeyboardInterrupt:
        print(f"\n{Colors.PRIMARY}✨ Thank you! ✨{Colors.RESET}")