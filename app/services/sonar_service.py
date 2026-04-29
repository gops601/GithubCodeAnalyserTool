import subprocess
import os
import requests
import time
import shutil
from app.services.tooling_service import ToolingService

class SonarService:
    def __init__(self, host_url, token):
        # Fallback for missing host_url to prevent crash
        self.host_url = (host_url or "http://localhost:9000").rstrip('/')
        self.token = token or ""

    def run_analysis(self, project_key, project_name, source_dir):
        """Runs sonar-scanner CLI on the source directory."""
        try:

            # 1. Determine the scanner executable
            # In Docker/Linux, it's 'sonar-scanner'. On Windows local, we use ToolingService.
            scanner_exe = "sonar-scanner"
            
            # Check if sonar-scanner is in PATH (standard for Docker)
            if shutil.which(scanner_exe) is None:
                # Fallback to local auto-downloaded tool (for Windows local development)
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                scanner_exe = ToolingService.ensure_scanner(base_dir)

            print(f"Running automated sonar-scanner for {project_key}...")
            
            # Command to run sonar-scanner
            command = [
                scanner_exe,
                f"-Dsonar.projectKey={project_key}",
                f"-Dsonar.projectName={project_name}",
                f"-Dsonar.sources=.",
                f"-Dsonar.host.url={self.host_url}",
                f"-Dsonar.login={self.token}",
                "-Dsonar.scm.disabled=true",
                "-Dsonar.sourceEncoding=UTF-8",
                "-Dsonar.exclusions=**/node_modules/**,**/venv/**,**/env/**,**/.git/**,**/target/**,**/dist/**,**/build/**"
            ]

            # If an organization is provided in environment, add it (required for SonarCloud)
            org = os.getenv('SONAR_ORGANIZATION')
            if org:
                command.append(f"-Dsonar.organization={org}")
            
            # On Linux (Docker), we should NOT use shell=True with a list.
            # On Windows, we need shell=True for .bat files.
            use_shell = os.name == 'nt'
            
            result = subprocess.run(
                command,
                cwd=source_dir,
                capture_output=True,
                text=True,
                shell=use_shell
            )
            
            if result.returncode != 0:
                return False, f"Sonar analysis failed: {result.stderr or result.stdout}"
            
            return True, "Analysis triggered successfully"
        except Exception as e:
            return False, str(e)

    def wait_for_completion(self, project_key, timeout=300):
        """Polls SonarQube API until the analysis task is finished."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check for the latest task status for this project
                r = requests.get(
                    f"{self.host_url}/api/ce/component",
                    params={"component": project_key},
                    auth=(self.token, "")
                )
                r.raise_for_status()
                data = r.json()
                
                queue = data.get("queue", [])
                current = data.get("current", {})
                
                if not queue and current.get("status") == "SUCCESS":
                    return True, "Analysis completed"
                
                if current.get("status") in ["FAILED", "CANCELED"]:
                    return False, f"Analysis task {current.get('status')}"
                
                print(f"Waiting for analysis completion for {project_key}...")
                time.sleep(10)
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(5)
        
        return False, "Analysis timed out"

    def fetch_metrics(self, project_key):
        """Fetches key metrics from SonarQube API."""
        metric_keys = "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc"
        try:
            r = requests.get(
                f"{self.host_url}/api/measures/component",
                params={"component": project_key, "metricKeys": metric_keys},
                auth=(self.token, "")
            )
            r.raise_for_status()
            data = r.json()
            
            metrics = {
                "bugs": 0,
                "vulnerabilities": 0,
                "code_smells": 0,
                "coverage": 0.0,
                "duplications": 0.0,
                "ncloc": 0
            }
            
            for m in data.get("component", {}).get("measures", []):
                key = m["metric"]
                val = m.get("value", 0)
                if key == "bugs": metrics["bugs"] = int(val)
                elif key == "vulnerabilities": metrics["vulnerabilities"] = int(val)
                elif key == "code_smells": metrics["code_smells"] = int(val)
                elif key == "coverage": metrics["coverage"] = float(val)
                elif key == "duplicated_lines_density": metrics["duplications"] = float(val)
                elif key == "ncloc": metrics["ncloc"] = int(val)
            
            return metrics
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return None
