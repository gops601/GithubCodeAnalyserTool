# ICTAK Code Analysis Tool

This application is a full-stack DevOps tool designed to automate the process of downloading public GitHub repositories and performing code quality analysis using SonarQube. It requires **zero manual configuration** of scanning tools.

## 🚀 How It Works

The application follows a fully automated end-to-end workflow:

### 1. Submission
- User inputs a **Public GitHub URL** and a **Batch Name** into the web dashboard.
- The system parses the URL to extract the `github_user` and `repository_name`.

### 2. Project Naming Convention
- As requested, projects are uniquely identified in SonarQube using the pattern: 
  `{githubuser}_{RepositoryName}`.
- This ensures a clean and organized project list in your SonarQube dashboard.

### 3. Background Processing (Automated Workflow)
To keep the UI responsive, all heavy tasks happen in a background thread:
1.  **Repository Cloning**: The `GitService` clones the public repository into a temporary directory on the server.
2.  **Self-Installing Tooling**: The `ToolingService` checks if the `sonar-scanner` CLI is available. If not, it **automatically downloads** the correct version from SonarSource, extracts it, and sets it up.
3.  **Universal Scanning**: 
    - The `SonarService` triggers the scan. 
    - It is configured to be **"Universal"**, meaning it supports **Python, React, MERN, Java, etc.** 
    - It automatically excludes heavy folders like `node_modules`, `venv`, and `build` to ensure fast and accurate scans.
4.  **Status Tracking**: The app polls the SonarQube API until the analysis is finished and updates the database status.

### 4. Real-time Dashboard
- The frontend uses a lightweight JavaScript polling mechanism to check the status of "Pending" or "Running" scans every 5 seconds.
- Once finished, the status updates to **Completed** or **Failed**, and a direct link to the SonarQube dashboard is provided.

---

## 🛠 Tech Stack
- **Backend**: Flask (Python)
- **Database**: MySQL (Tracks batches, repos, and history)
- **Task Queue**: Python Threading (for background automation)
- **Integration**: SonarQube REST API & Sonar-Scanner CLI

---

## 📂 Project Structure
```text
testproj/
├── app/
│   ├── services/
│   │   ├── git_service.py     # Handles cloning repos
│   │   ├── sonar_service.py   # Manages scan logic & exclusions
│   │   └── tooling_service.py # Auto-downloads sonar-scanner CLI
│   ├── templates/
│   │   └── index.html         # Modern dashboard UI
│   ├── static/css/style.css   # Premium dark-theme styling
│   ├── models.py              # MySQL Database models
│   ├── routes.py              # API & UI endpoints
│   └── tasks.py               # Background workflow coordinator
├── tools/                     # Auto-created: Stores downloaded scanner
├── .env                       # Configuration (URL, Token, DB)
├── requirements.txt           # Python dependencies
└── run.py                     # Entry point
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- **Python 3.8+**
- **MySQL Server**
- **Git** installed on your system

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
SONAR_HOST_URL=http://your-sonar-ip:9000/
SONAR_TOKEN=your_sq_token
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=sonar_devops
```

### 3. Running the App
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python run.py`
3. Access the dashboard: `http://localhost:5000`

---

## 🧩 Language Support
The scanner is configured to be **Universal**. It handles:
- **Frontend**: React, Vue, Angular, Plain HTML/JS
- **Backend**: Node.js (Express), Python (Django/Flask), Java (Maven/Gradle)
- **Full Stack**: MERN, MEAN, etc.
- **Smart Exclusions**: Automatically ignores `node_modules`, `venv`, `dist`, `build`, and `.git` to prevent scan bloat.
