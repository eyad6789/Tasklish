# 🚀 Flow Tracker - Complete Setup Guide

Your beautiful task and habit tracker with AI-powered task breakdown!

## 📦 What You Got

1. **flow-task-tracker.html** - Beautiful frontend with professional icons
2. **backend.py** - Flask backend server with SQLite database
3. **requirements.txt** - Python dependencies
4. **BACKEND_README.md** - Detailed backend documentation

## 🎯 Quick Start (3 Steps!)

### Step 1: Install Python Dependencies

```bash
pip install Flask flask-cors
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend Server

```bash
python backend.py
```

Or:
```bash
python3 backend.py
```

You should see:
```
Starting Flow Tracker Backend Server...
Server running on http://localhost:5000
```

### Step 3: Open the Frontend

Simply open `flow-task-tracker.html` in your browser!

The app will automatically connect to the backend and save everything to the SQLite database.

## ✨ Features

### Frontend
- 🎨 Beautiful gradient design with professional icons (Lucide)
- 🤖 AI-powered task breakdown (uses Gemini API - pre-configured!)
- 📋 Kanban-style task board (To Do → In Progress → Done)
- 🎯 9 daily habits with streak tracking
- 📅 Monthly calendar view of habit completions
- 🔄 Real-time sync with backend database
- 💾 Automatic fallback to local storage if backend is offline

### Backend
- 🗄️ SQLite database for persistent storage
- 🔌 RESTful API with CORS enabled
- 📊 Complete data management (tasks, subtasks, habits, history)
- 🚀 Fast and lightweight
- 🔧 Easy to deploy

## 📝 How to Use

### Creating Tasks
1. Type your task in natural language (e.g., "Create invoice for client X with packaging list")
2. Click "Create with AI Magic"
3. AI will break it down into subtasks with time estimates
4. Manage tasks by dragging through the columns or clicking status buttons

### Managing Habits
1. Click on any habit card to mark it complete for today
2. Build streaks by completing habits daily
3. View your progress in the calendar
4. Edit habits by clicking "Edit Habits" button

### AI Configuration
- **Pre-configured!** API key is already in the code
- Model used: gemini-2.5-flash
- You can change the API key in Settings if needed

## 🔧 Configuration

### Switch Between Backend and Local Storage

In `flow-task-tracker.html`, find this line:
```javascript
const USE_BACKEND = true; // Set to false to use local storage only
```

- `true` = Uses backend + SQLite database
- `false` = Uses browser local storage only (no backend needed)

### Change Backend URL

If you deploy the backend to a different server:
```javascript
const API_BASE_URL = 'http://localhost:5000/api'; // Change this URL
```

## 📂 File Structure

```
flow-tracker/
├── flow-task-tracker.html    # Frontend application
├── backend.py                # Backend server
├── requirements.txt          # Python dependencies
├── BACKEND_README.md         # Backend documentation
└── flow_tracker.db          # SQLite database (created automatically)
```

## 🌐 Deployment Tips

### Frontend
- Can be deployed to any static hosting (Hostinger, Netlify, Vercel, GitHub Pages)
- Just upload the HTML file!

### Backend
- Deploy to services like:
  - Heroku
  - Railway
  - PythonAnywhere
  - AWS EC2
  - DigitalOcean
  - Your own VPS

- Remember to:
  1. Update `API_BASE_URL` in the frontend
  2. Restrict CORS to your frontend domain in production
  3. Disable Flask debug mode

## 🐛 Troubleshooting

### Backend won't start
- Make sure Flask is installed: `pip install Flask flask-cors`
- Check if port 5000 is available
- Try a different port in backend.py

### Frontend can't connect
- Make sure backend is running on http://localhost:5000
- Check browser console for errors
- Try setting `USE_BACKEND = false` to test local mode

### AI not working
- Check your API key in Settings
- Make sure you have internet connection
- Verify Gemini API key is valid at https://aistudio.google.com/

## 🎉 You're All Set!

Enjoy your beautiful, AI-powered productivity app!

Questions? Issues? Check:
- Backend details: BACKEND_README.md
- API endpoints: http://localhost:5000/api/health

Happy tracking! 🚀✨
