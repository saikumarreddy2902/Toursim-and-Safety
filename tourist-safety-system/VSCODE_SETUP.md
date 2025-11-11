# VS Code Setup Guide

## Quick Start in VS Code

### Method 1: Using the Workspace File (Recommended)

1. **Open VS Code**
2. **File → Open Workspace from File**
3. **Select** `tourist-safety-system.code-workspace`
4. **Install recommended extensions** when prompted
5. **Open Terminal** (`Ctrl+` ` `)
6. **Run the following commands**:
   ```powershell
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
7. **Open browser** to `http://localhost:5000`

### Method 2: Using VS Code Tasks

1. **Open the project folder** in VS Code
2. **Press** `Ctrl+Shift+P` to open Command Palette
3. **Type** "Tasks: Run Task"
4. **Select** "Install Dependencies" (first time only)
5. **Run** "Start Server" task
6. **Open browser** to `http://localhost:5000`

### Method 3: Using VS Code Debugger

1. **Open VS Code**
2. **Go to** Run and Debug view (`Ctrl+Shift+D`)
3. **Select** "Start Tourist Safety System"
4. **Press** `F5` or click the green play button
5. **Open browser** to `http://localhost:5000`

## VS Code Extensions (Recommended)

Install these extensions for better development experience:

- **Python** (`ms-python.python`) - Python language support
- **Live Server** (`ritwickdey.liveserver`) - Live reload for frontend
- **Auto Rename Tag** (`formulahendry.auto-rename-tag`) - HTML tag editing
- **Prettier** (`esbenp.prettier-vscode`) - Code formatting
- **GitLens** (`eamodio.gitlens`) - Git integration

## Keyboard Shortcuts

- `Ctrl+` ` ` - Open integrated terminal
- `Ctrl+Shift+P` - Command palette
- `F5` - Start debugging
- `Ctrl+Shift+D` - Debug view
- `Ctrl+Shift+E` - Explorer view

## Troubleshooting in VS Code

### Python Not Found
1. **Open Command Palette** (`Ctrl+Shift+P`)
2. **Type** "Python: Select Interpreter"
3. **Choose** your Python installation

### Terminal Issues
- Use **PowerShell** or **Command Prompt**
- Avoid Git Bash for running Python scripts

### Port Already in Use
- **Stop the previous server** (`Ctrl+C` in terminal)
- **Or change port** in `app.py` line 167: `app.run(port=5001)`

## Project Structure in VS Code

```
TOURIST-SAFETY-SYSTEM/
├── 📁 backend/
│   ├── 🐍 app.py           # Main Flask application
│   └── 📄 requirements.txt # Python dependencies
├── 📁 frontend/
│   ├── 📁 static/
│   │   ├── 🎨 style.css
│   │   ├── ⚡ common.js
│   │   └── 🌐 translations.json
│   └── 📁 templates/
│       ├── 🏠 index.html
│       ├── 📝 register.html
│       ├── 👤 tourist_dashboard.html
│       └── 👨‍💼 admin_dashboard.html
├── 📁 data/                # Auto-created database folder
├── 📖 README.md
├── 🚀 start_server.bat     # Windows startup script
└── ⚙️ tourist-safety-system.code-workspace
```

## Development Tips

1. **Use split view** - Open HTML and CSS side by side
2. **Live reload** - Install Live Server extension
3. **Debug mode** - Use F5 to run with debugging
4. **Git integration** - Initialize git repo for version control
5. **Snippets** - Use HTML/CSS/JS snippets for faster coding