import os
import subprocess
import time
import sys
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

class DeviceDetector:
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
            # Fallback config
            return {"scrcpy_folder": "scrcpy-win64-v3.2"}
    
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

    def print_big_message(self, message, color, icon="✨"):
        """Print big epic message"""
        print(f"\n{color}{Colors.BOLD}{icon} {'═' * 50}{icon}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}   {message}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{icon} {'═' * 50}{icon}{Colors.RESET}\n")

    def detect_all_devices(self):
        """Detect all devices (USB and network)"""
        print(f"{Colors.PRIMARY}🔍 Scanning for all devices...{Colors.RESET}")
        
        # Get all devices
        devices_output = self.run_command("adb devices", silent=True)
        
        devices = []
        lines = devices_output.strip().split('\n')
        
        for line in lines[1:]:  # Skip first line "List of devices attached"
            if line.strip() and not line.startswith('*'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    device_id = parts[0].strip()
                    status = parts[1].strip()
                    
                    if status == 'device':  # Only take connected devices
                        device_type = "USB" if ':' not in device_id else "NETWORK"
                        devices.append({
                            'id': device_id,
                            'status': status,
                            'type': device_type
                        })
        
        return devices

    def get_device_details(self, device_id):
        """Get detailed information about a specific device"""
        try:
            # Get device model
            model_output = self.run_command(f"adb -s {device_id} shell getprop ro.product.model", silent=True)
            model = model_output.strip() if model_output.strip() else "Unknown"
            
            # Get device brand
            brand_output = self.run_command(f"adb -s {device_id} shell getprop ro.product.brand", silent=True)
            brand = brand_output.strip() if brand_output.strip() else "Unknown"
            
            # Get Android version
            android_output = self.run_command(f"adb -s {device_id} shell getprop ro.build.version.release", silent=True)
            android_version = android_output.strip() if android_output.strip() else "Unknown"
            
            # Get device name
            device_output = self.run_command(f"adb -s {device_id} shell getprop ro.product.name", silent=True)
            device_name = device_output.strip() if device_output.strip() else "Unknown"
            
            # Get product model
            product_model_output = self.run_command(f"adb -s {device_id} shell getprop ro.product.model", silent=True)
            product_model = product_model_output.strip() if product_model_output.strip() else model
            
            return {
                'model': model,
                'brand': brand,
                'android_version': android_version,
                'device_name': device_name,
                'product_model': product_model
            }
        except Exception as e:
            print(f"{Colors.DIM}↳ Could not get device details: {e}{Colors.RESET}")
            return {
                'model': 'Unknown',
                'brand': 'Unknown', 
                'android_version': 'Unknown',
                'device_name': 'Unknown',
                'product_model': 'Unknown'
            }

    def display_devices_list(self, devices):
        """Display list of devices for user selection"""
        print(f"\n{Colors.SUCCESS}🎯 DEVICES FOUND:{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
        
        for index, device in enumerate(devices, 1):
            details = self.get_device_details(device['id'])
            
            device_icon = "🔌" if device['type'] == 'USB' else "🌐"
            type_color = Colors.WARNING if device['type'] == 'USB' else Colors.PRIMARY
            
            print(f"{Colors.PRIMARY}{index}. {device_icon} {type_color}{device['type']}{Colors.RESET}")
            print(f"   {Colors.DEVICE}ID: {device['id']}{Colors.RESET}")
            print(f"   {Colors.SUCCESS}{details['brand']} {details['model']}{Colors.RESET}")
            print(f"   {Colors.DIM}Android {details['android_version']} • {details['device_name']}{Colors.RESET}")
            print(f"{Colors.DIM}   ──────────────────────────────────────{Colors.RESET}")

    def get_user_choice(self, devices):
        """Get user choice for device selection"""
        while True:
            try:
                print(f"\n{Colors.PRIMARY}🔢 Select device (1-{len(devices)}):{Colors.RESET}", end=" ")
                choice = input().strip()
                
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(devices):
                        return devices[choice_num - 1]
                
                print(f"{Colors.ERROR}❌ Invalid choice. Enter a number 1-{len(devices)}{Colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}👋 Stopped by user{Colors.RESET}")
                sys.exit(0)
            except Exception as e:
                print(f"{Colors.ERROR}❌ Error: {e}{Colors.RESET}")

    def display_device_info(self, device):
        """Display device information in beautiful format"""
        details = self.get_device_details(device['id'])
        
        print(f"\n{Colors.SUCCESS}🎯 DEVICE SELECTED!{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
        
        device_icon = "🔌" if device['type'] == 'USB' else "🌐"
        type_color = Colors.WARNING if device['type'] == 'USB' else Colors.PRIMARY
        
        print(f"{Colors.PRIMARY}{device_icon} {Colors.BOLD}Connection Type:{Colors.RESET}")
        print(f"   {type_color}{device['type']}{Colors.RESET}")
        
        print(f"{Colors.PRIMARY}📱 {Colors.BOLD}Device ID:{Colors.RESET}")
        print(f"   {Colors.DEVICE}{device['id']}{Colors.RESET}")
        
        print(f"{Colors.PRIMARY}🏷️  {Colors.BOLD}Device Information:{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Brand:     {details['brand']}{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Model:     {details['model']}{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Name:      {details['device_name']}{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Android:   {details['android_version']}{Colors.RESET}")
        
        print(f"{Colors.PRIMARY}🔧 {Colors.BOLD}Status:{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Status:    {device['status']}{Colors.RESET}")
        
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

    def parse_scrcpy_output(self, line):
        """Parse and style scrcpy output lines"""
        line = line.strip()
        
        # Filter and style only desired information
        if "Device: [" in line and "]" in line:
            device_info = line.split("Device: ", 1)[1]
            return f"{Colors.PRIMARY}📱 Device: {Colors.DEVICE}{device_info}{Colors.RESET}"
        
        elif "Texture:" in line:
            resolution = line.split("Texture: ", 1)[1]
            return f"{Colors.PRIMARY}🖼️  Resolution: {Colors.PORT}{resolution}{Colors.RESET}"
        
        elif "server" in line and "Device: [" in line:
            device_info = line.split("Device: ", 1)[1]
            return f"{Colors.PRIMARY}📱 Device: {Colors.DEVICE}{device_info}{Colors.RESET}"
        
        return None

    def run_scrcpy_with_filtered_output(self, device_id):
        """Run scrcpy with filtered and styled output"""
        try:
            process = subprocess.Popen(
                f"scrcpy -s {device_id} --no-audio --max-size 1024",
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
        """Main function to detect and run scrcpy for devices"""
        print(f"\n{Colors.PRIMARY}✨ USB DEVICE DETECTOR ✨{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
        print(f"{Colors.WARNING}🔌 Connect Android device via USB{Colors.RESET}")
        print(f"{Colors.WARNING}   ↳ Make sure USB Debugging is enabled{Colors.RESET}")
        print(f"{Colors.WARNING}   ↳ Allow USB Debugging connection{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

        # Scan for all devices
        devices = self.detect_all_devices()
        
        if not devices:
            print(f"\n{Colors.ERROR}❌ No devices detected{Colors.RESET}")
            print(f"{Colors.WARNING}💡 Tips:{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Make sure USB cable is properly connected{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Enable USB Debugging in Developer Options{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Allow USB Debugging connection on device{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Try unplugging and reconnecting USB cable{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ For WiFi, make sure device is on the same network{Colors.RESET}")
            
            print(f"\n{Colors.WARNING}🔄 Retrying in 5 seconds...{Colors.RESET}")
            time.sleep(5)
            self.main()
            return

        # Display device list and ask user to choose
        self.display_devices_list(devices)
        
        # If only 1 device found, use it directly
        if len(devices) == 1:
            device = devices[0]
            print(f"\n{Colors.SUCCESS}✅ Only 1 device found, using it directly...{Colors.RESET}")
        else:
            # Ask user to select device
            device = self.get_user_choice(devices)

        self.display_device_info(device)

        # Confirm running scrcpy
        print(f"\n{Colors.PRIMARY}🚀 Running scrcpy...{Colors.RESET}")
        print(f"{Colors.DIM}⏹️  Press Ctrl+C to stop{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

        # Run scrcpy
        connection_count = 0
        
        while True:
            connection_count += 1
            print(f"\n{Colors.PRIMARY}🔄 Starting mirroring... ({connection_count}){Colors.RESET}")
            
            return_code = self.run_scrcpy_with_filtered_output(device['id'])

            print(f"\n{Colors.WARNING}⚠️  Connection lost{Colors.RESET}")
            print(f"{Colors.DIM}↳ Reconnecting in 3 seconds...{Colors.RESET}")
            
            for i in range(3, 0, -1):
                print(f"{Colors.DIM}   {i}...{Colors.RESET}", end=' ', flush=True)
                time.sleep(1)
            print()

if __name__ == "__main__":
    try:
        detector = DeviceDetector()
        detector.main()
    except KeyboardInterrupt:
        print(f"\n{Colors.PRIMARY}✨ Thank you! ✨{Colors.RESET}")