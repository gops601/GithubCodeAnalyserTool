import os
import requests
import zipfile
import shutil
import io

class ToolingService:
    SCANNER_VERSION = "6.2.1.4610"
    SCANNER_URL = f"https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-{SCANNER_VERSION}-windows-x64.zip"
    
    @staticmethod
    def ensure_scanner(base_dir):
        """Ensures sonar-scanner is available in the local directory."""
        tool_dir = os.path.join(base_dir, "tools")
        scanner_bin_dir = os.path.join(tool_dir, f"sonar-scanner-{ToolingService.SCANNER_VERSION}-windows-x64", "bin")
        scanner_exe = os.path.join(scanner_bin_dir, "sonar-scanner.bat")
        
        if os.path.exists(scanner_exe):
            return scanner_exe
        
        print(f"Sonar-scanner not found. Downloading version {ToolingService.SCANNER_VERSION}...")
        os.makedirs(tool_dir, exist_ok=True)
        
        response = requests.get(ToolingService.SCANNER_URL)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(tool_dir)
            
        print("Sonar-scanner downloaded and extracted successfully.")
        return scanner_exe
