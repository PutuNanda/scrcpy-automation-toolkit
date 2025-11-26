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
            print(f"{Colors.SUCCESS}✅ Konfigurasi berhasil dimuat{Colors.RESET}")
            return config
        except Exception as e:
            print(f"{Colors.ERROR}❌ Gagal memuat konfigurasi: {e}{Colors.RESET}")
            # Fallback config
            return {"scrcpy_folder": "scrcpy-win64-v3.2"}
    
    def setup_environment(self):
        """Setup scrcpy environment and PATH"""
        scrcpy_folder = self.config.get("scrcpy_folder", "scrcpy-win64-v3.2")
        
        if os.path.exists(scrcpy_folder):
            os.chdir(scrcpy_folder)
            # Add current directory to PATH for adb and scrcpy
            os.environ['PATH'] = os.getcwd() + os.pathsep + os.environ['PATH']
            print(f"{Colors.SUCCESS}✅ Environment scrcpy disetup di: {os.getcwd()}{Colors.RESET}")
        else:
            print(f"{Colors.ERROR}❌ Folder scrcpy tidak ditemukan: {scrcpy_folder}{Colors.RESET}")
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
        print(f"{Colors.PRIMARY}🔍 Memindai semua perangkat...{Colors.RESET}")
        
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
            print(f"{Colors.DIM}↳ Tidak bisa mendapatkan detail perangkat: {e}{Colors.RESET}")
            return {
                'model': 'Unknown',
                'brand': 'Unknown', 
                'android_version': 'Unknown',
                'device_name': 'Unknown',
                'product_model': 'Unknown'
            }

    def display_devices_list(self, devices):
        """Display list of devices for user selection"""
        print(f"\n{Colors.SUCCESS}🎯 PERANGKAT YANG DITEMUKAN:{Colors.RESET}")
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
                print(f"\n{Colors.PRIMARY}🔢 Pilih perangkat (1-{len(devices)}):{Colors.RESET}", end=" ")
                choice = input().strip()
                
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(devices):
                        return devices[choice_num - 1]
                
                print(f"{Colors.ERROR}❌ Pilihan tidak valid. Masukkan angka 1-{len(devices)}{Colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}👋 Berhenti oleh pengguna{Colors.RESET}")
                sys.exit(0)
            except Exception as e:
                print(f"{Colors.ERROR}❌ Error: {e}{Colors.RESET}")

    def display_device_info(self, device):
        """Display device information in beautiful format"""
        details = self.get_device_details(device['id'])
        
        print(f"\n{Colors.SUCCESS}🎯 PERANGKAT DIPILIH!{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
        
        device_icon = "🔌" if device['type'] == 'USB' else "🌐"
        type_color = Colors.WARNING if device['type'] == 'USB' else Colors.PRIMARY
        
        print(f"{Colors.PRIMARY}{device_icon} {Colors.BOLD}Tipe Koneksi:{Colors.RESET}")
        print(f"   {type_color}{device['type']}{Colors.RESET}")
        
        print(f"{Colors.PRIMARY}📱 {Colors.BOLD}Device ID:{Colors.RESET}")
        print(f"   {Colors.DEVICE}{device['id']}{Colors.RESET}")
        
        print(f"{Colors.PRIMARY}🏷️  {Colors.BOLD}Informasi Perangkat:{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Merek:     {details['brand']}{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Model:     {details['model']}{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Nama:      {details['device_name']}{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Android:   {details['android_version']}{Colors.RESET}")
        
        print(f"{Colors.PRIMARY}🔧 {Colors.BOLD}Status:{Colors.RESET}")
        print(f"   {Colors.SUCCESS}Status:    {device['status']}{Colors.RESET}")
        
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

    def parse_scrcpy_output(self, line):
        """Parse and style scrcpy output lines"""
        line = line.strip()
        
        # Filter dan style hanya informasi yang diinginkan
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
            
            # Baca output real-time
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Parse dan tampilkan hanya informasi yang diinginkan
                styled_line = self.parse_scrcpy_output(line)
                if styled_line:
                    print(styled_line)
                    
                # Check if process has terminated
                if process.poll() is not None:
                    break
                    
            return process.wait()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}👋 Mirroring dihentikan{Colors.RESET}")
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
        print(f"{Colors.WARNING}🔌 Sambungkan perangkat Android via USB{Colors.RESET}")
        print(f"{Colors.WARNING}   ↳ Pastikan USB Debugging aktif{Colors.RESET}")
        print(f"{Colors.WARNING}   ↳ Izinkan koneksi USB Debugging{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

        # Scan for all devices
        devices = self.detect_all_devices()
        
        if not devices:
            print(f"\n{Colors.ERROR}❌ Tidak ada perangkat yang terdeteksi{Colors.RESET}")
            print(f"{Colors.WARNING}💡 Tips:{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Pastikan kabel USB terpasang dengan baik{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Aktifkan USB Debugging di Developer Options{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Izinkan koneksi USB Debugging di perangkat{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Coba cabut dan pasang kembali kabel USB{Colors.RESET}")
            print(f"{Colors.DIM}   ↳ Untuk WiFi, pastikan perangkat terhubung ke jaringan yang sama{Colors.RESET}")
            
            print(f"\n{Colors.WARNING}🔄 Mencoba ulang dalam 5 detik...{Colors.RESET}")
            time.sleep(5)
            self.main()
            return

        # Tampilkan daftar perangkat dan minta user memilih
        self.display_devices_list(devices)
        
        # Jika hanya ada 1 device, langsung pakai
        if len(devices) == 1:
            device = devices[0]
            print(f"\n{Colors.SUCCESS}✅ Hanya 1 perangkat ditemukan, langsung digunakan...{Colors.RESET}")
        else:
            # Minta user memilih perangkat
            device = self.get_user_choice(devices)

        self.display_device_info(device)

        # Konfirmasi menjalankan scrcpy
        print(f"\n{Colors.PRIMARY}🚀 Menjalankan scrcpy...{Colors.RESET}")
        print(f"{Colors.DIM}⏹️  Tekan Ctrl+C untuk berhenti{Colors.RESET}")
        print(f"{Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

        # Jalankan scrcpy
        connection_count = 0
        
        while True:
            connection_count += 1
            print(f"\n{Colors.PRIMARY}🔄 Memulai mirroring... ({connection_count}){Colors.RESET}")
            
            return_code = self.run_scrcpy_with_filtered_output(device['id'])

            print(f"\n{Colors.WARNING}⚠️  Koneksi terputus{Colors.RESET}")
            print(f"{Colors.DIM}↳ Menghubungkan ulang dalam 3 detik...{Colors.RESET}")
            
            for i in range(3, 0, -1):
                print(f"{Colors.DIM}   {i}...{Colors.RESET}", end=' ', flush=True)
                time.sleep(1)
            print()

if __name__ == "__main__":
    try:
        detector = DeviceDetector()
        detector.main()
    except KeyboardInterrupt:
        print(f"\n{Colors.PRIMARY}✨ Terima kasih! ✨{Colors.RESET}")