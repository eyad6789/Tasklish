# Flow Tracker Backend

Simple Flask backend with SQLite database for the Flow task and habit tracker app.

## Features

- ✅ SQLite database for data persistence
- ✅ RESTful API endpoints
- ✅ CORS enabled for frontend integration
- ✅ Automatic database initialization
- ✅ Task management (create, read, update, delete)
- ✅ Habit tracking with streak management
- ✅ Habit history tracking

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask flask-cors
```

## Running the Server

Simply run:
```bash
python backend.py
```

Or:
```bash
python3 backend.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if server is running

### Tasks
- `GET /api/tasks` - Get all tasks with subtasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task

### Habits
- `GET /api/habits` - Get all habits
- `POST /api/habits` - Save/update all habits
- `PUT /api/habits/<id>` - Update a single habit

### Habit History
- `GET /api/habit-history` - Get all habit history
- `POST /api/habit-history` - Save habit history
- `POST /api/habit-history/<habit_id>/<date>` - Record habit completion
- `DELETE /api/habit-history/<habit_id>/<date>` - Remove habit completion

## Database Schema

### Tasks Table
- `id` - Task ID (primary key)
- `title` - Task title
- `status` - Task status (todo, doing, done)
- `estimated_time` - Estimated time to complete
- `created_at` - Creation timestamp

### Subtasks Table
- `id` - Subtask ID (primary key)
- `task_id` - Parent task ID (foreign key)
- `title` - Subtask title
- `status` - Subtask status
- `estimated_time` - Estimated time

### Habits Table
- `id` - Habit ID (primary key)
- `name` - Habit name
- `streak` - Current streak count
- `completed_today` - Whether completed today (0 or 1)

### Habit History Table
- `id` - Auto-increment ID
- `habit_id` - Habit ID (foreign key)
- `date` - Date (YYYY-MM-DD format)
- `completed` - Completion status (0 or 1)

## Database File

The SQLite database is stored as `flow_tracker.db` in the same directory as the backend script.

## CORS Configuration

CORS is enabled for all origins by default. In production, you should restrict this to your frontend domain only.

## Notes

- The database is automatically created on first run
- All data is stored locally in SQLite
- The server runs in debug mode by default (disable in production)
- Default port is 5000 (can be changed in the code)
