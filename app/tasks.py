import threading
import os
import tempfile
from app.models import db, Repository, AnalysisResult
from app.services.git_service import GitService
from app.services.sonar_service import SonarService

def start_analysis_task(app, repository_id, sonar_config):
    """Starts the background thread for analysis."""
    thread = threading.Thread(target=run_automated_analysis, args=(app, repository_id, sonar_config))
    thread.daemon = True
    thread.start()

def run_automated_analysis(app, repository_id, sonar_config):
    """The automated end-to-end analysis workflow."""
    with app.app_context():
        repo = Repository.query.get(repository_id)
        if not repo:
            return

        try:
            repo.status = 'Running'
            db.session.commit()

            # 1. Prepare temp directory
            temp_dir = tempfile.mkdtemp(prefix="sonar_scan_")
            
            # 2. Clone Repository
            success, msg = GitService.clone_repo(repo.url, temp_dir)
            if not success:
                repo.status = 'Failed'
                repo.error_message = msg
                db.session.commit()
                return

            # 3. Trigger SonarQube Analysis
            sonar = SonarService(sonar_config['host_url'], sonar_config['token'])
            project_name = sonar_config.get('project_name', repo.project_key)
            success, msg = sonar.run_analysis(repo.project_key, project_name, temp_dir)
            
            if not success:
                repo.status = 'Failed'
                repo.error_message = msg
                db.session.commit()
                GitService.cleanup(temp_dir)
                return

            # 4. Wait for completion (Optional, but good for status tracking)
            success, msg = sonar.wait_for_completion(repo.project_key)
            if not success:
                repo.status = 'Failed'
                repo.error_message = msg
                db.session.commit()
                GitService.cleanup(temp_dir)
                return

            repo.status = 'Completed'
            db.session.commit()
            
            # 5. Cleanup
            GitService.cleanup(temp_dir)

        except Exception as e:
            repo.status = 'Failed'
            repo.error_message = str(e)
            db.session.commit()
            print(f"Error in automated analysis: {e}")
