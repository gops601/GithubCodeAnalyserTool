from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from app.models import db, Batch, Repository, AnalysisResult
from app.tasks import start_analysis_task
import os
import uuid

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    batches = Batch.query.order_by(Batch.created_at.desc()).all()
    sonar_url_base = os.getenv('SONAR_HOST_URL', '').rstrip('/')
    return render_template('index.html', batches=batches, sonar_url_base=sonar_url_base)

@bp.route('/submit', methods=['POST'])
def submit():
    repo_url = request.form.get('repo_url')
    batch_name = request.form.get('batch_name')

    if not repo_url or not batch_name:
        return jsonify({"error": "Repository URL and Batch Name are required"}), 400

    # 1. Get or create batch
    batch = Batch.query.filter_by(name=batch_name).first()
    if not batch:
        batch = Batch(name=batch_name)
        db.session.add(batch)
        db.session.commit()

    # 2. Extract GitHub username and repository name from URL
    # Format: https://github.com/username/repo
    parts = repo_url.rstrip('/').split('/')
    if len(parts) >= 2:
        github_user = parts[-2]
        repo_name = parts[-1].replace('.git', '')
    else:
        github_user = "unknown"
        repo_name = "project"

    # Generate project key and name as requested: BatchName_githubuser_RepositoryName
    safe_batch = batch_name.replace(' ', '_')
    project_key = f"{safe_batch}_{github_user}_{repo_name}"
    display_name = f"{safe_batch}_{github_user}_{repo_name}"

    # 3. Create repository entry
    repo = Repository(
        batch_id=batch.id,
        url=repo_url,
        project_key=project_key,
        status='Pending'
    )
    db.session.add(repo)
    db.session.commit()

    # 4. Trigger automated analysis in background
    sonar_config = {
        'host_url': os.getenv('SONAR_HOST_URL'),
        'token': os.getenv('SONAR_TOKEN'),
        'project_name': display_name
    }
    
    # We need to pass the actual Flask app object for the app context in the thread
    start_analysis_task(current_app._get_current_object(), repo.id, sonar_config)

    return redirect(url_for('main.index'))

@bp.route('/api/status/<int:repo_id>')
def get_status(repo_id):
    repo = Repository.query.get_or_404(repo_id)
    result = repo.results[-1] if repo.results else None
    
    data = {
        "status": repo.status,
        "error": repo.error_message,
        "project_key": repo.project_key,
        "sonar_url": f"{os.getenv('SONAR_HOST_URL').rstrip('/')}/dashboard?id={repo.project_key}"
    }
    
    if result:
        data["metrics"] = {
            "bugs": result.bugs,
            "vulnerabilities": result.vulnerabilities,
            "code_smells": result.code_smells,
            "coverage": result.coverage,
            "duplications": result.duplications,
            "ncloc": result.ncloc
        }
    
    return jsonify(data)

@bp.route('/api/batches')
def get_batches():
    batches = Batch.query.all()
    output = []
    for b in batches:
        repos = []
        for r in b.repositories:
            repos.append({
                "id": r.id,
                "url": r.url,
                "status": r.status,
                "project_key": r.project_key
            })
        output.append({
            "id": b.id,
            "name": b.name,
            "repositories": repos
        })
    return jsonify(output)
