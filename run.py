from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ensure sonar-scanner is in the environment
    # On Windows, you might need to point to the full path if it's not in PATH
    app.run(host='0.0.0.0', port=5000, debug=True)
