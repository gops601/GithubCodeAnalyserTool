import subprocess
import os
import shutil
import stat

class GitService:
    @staticmethod
    def clone_repo(repo_url, target_dir):
        """Clones a public git repository to the target directory."""
        try:
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, onerror=GitService._on_rm_error)
            
            os.makedirs(target_dir, exist_ok=True)
            
            print(f"Cloning {repo_url} into {target_dir}...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, "."],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Cloned successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Git clone failed: {e.stderr}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _on_rm_error(func, path, exc_info):
        """Handle read-only files on Windows during deletion."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    @staticmethod
    def cleanup(target_dir):
        """Removes the cloned repository directory."""
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, onerror=GitService._on_rm_error)
