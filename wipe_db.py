from app import create_app
from app.models import db, Batch, Repository, AnalysisResult

app = create_app()
with app.app_context():
    try:
        # Delete in order to satisfy foreign key constraints
        AnalysisResult.query.delete()
        Repository.query.delete()
        Batch.query.delete()
        db.session.commit()
        print("Database cleared successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing database: {e}")
