from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
DATABASE = 'flow_tracker.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL,
            estimated_time TEXT,
            labels TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    ''')
    
    # Add new columns to existing tables if they don't exist
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT DEFAULT ''")
    except:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN labels TEXT DEFAULT '[]'")
    except:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
    except:
        pass  # Column already exists
    
    # Subtasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            estimated_time TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    ''')
    
    # Habits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            completed_today INTEGER DEFAULT 0
        )
    ''')
    
    # Habit history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            completed INTEGER DEFAULT 1,
            UNIQUE(habit_id, date),
            FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Serve Frontend
@app.route('/')
def index():
    """Serve the frontend HTML file"""
    return send_from_directory('.', 'flow-task-tracker.html')

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"})

# Tasks endpoints
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with their subtasks"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all tasks
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = cursor.fetchall()
    
    result = []
    for task in tasks:
        # Get subtasks for each task
        cursor.execute('SELECT * FROM subtasks WHERE task_id = ?', (task['id'],))
        subtasks = cursor.fetchall()
        
        # Get description and labels safely (may not exist in old databases)
        try:
            description = task['description'] or ''
        except (KeyError, IndexError):
            description = ''
        
        try:
            labels = json.loads(task['labels']) if task['labels'] else []
        except (KeyError, IndexError):
            labels = []
        
        result.append({
            'id': task['id'],
            'title': task['title'],
            'description': description,
            'status': task['status'],
            'estimatedTime': task['estimated_time'],
            'labels': labels,
            'createdAt': task['created_at'],
            'subtasks': [dict(st) for st in subtasks]
        })
    
    conn.close()
    return jsonify(result)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task with subtasks"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Insert task
        cursor.execute('''
            INSERT INTO tasks (id, title, description, status, estimated_time, labels, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['title'],
            data.get('description', ''),
            data['status'],
            data['estimatedTime'],
            json.dumps(data.get('labels', [])),
            data['createdAt']
        ))
        
        # Insert subtasks
        for subtask in data['subtasks']:
            cursor.execute('''
                INSERT INTO subtasks (id, task_id, title, status, estimated_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                subtask['id'],
                data['id'],
                subtask['title'],
                subtask['status'],
                subtask['estimatedTime']
            ))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Task created successfully", "id": data['id']}), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task and its subtasks"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Set completed_at if task is being marked as done
        completed_at = None
        if data['status'] == 'done':
            from datetime import datetime
            completed_at = datetime.utcnow().isoformat() + 'Z'
        
        # Update task
        cursor.execute('''
            UPDATE tasks
            SET title = ?, description = ?, status = ?, estimated_time = ?, labels = ?, completed_at = ?
            WHERE id = ?
        ''', (
            data['title'],
            data.get('description', ''),
            data['status'],
            data['estimatedTime'],
            json.dumps(data.get('labels', [])),
            completed_at,
            task_id
        ))
        
        # Delete existing subtasks
        cursor.execute('DELETE FROM subtasks WHERE task_id = ?', (task_id,))
        
        # Insert updated subtasks
        for subtask in data['subtasks']:
            cursor.execute('''
                INSERT INTO subtasks (id, task_id, title, status, estimated_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                subtask['id'],
                task_id,
                subtask['title'],
                subtask['status'],
                subtask['estimatedTime']
            ))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Task updated successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task and its subtasks"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task deleted successfully"})

@app.route('/api/tasks/history', methods=['GET'])
def get_task_history():
    """Get completed tasks grouped by month"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all completed tasks
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE status = 'done' 
        ORDER BY completed_at DESC, created_at DESC
    ''')
    tasks = cursor.fetchall()
    
    # Group by month
    history = {}
    for task in tasks:
        # Get subtasks
        cursor.execute('SELECT * FROM subtasks WHERE task_id = ?', (task['id'],))
        subtasks = cursor.fetchall()
        
        # Determine completion month
        try:
            completed_date = task['completed_at'] or task['created_at']
        except (KeyError, IndexError):
            completed_date = task['created_at']
            
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))
            month_key = dt.strftime('%Y-%m')
            month_name = dt.strftime('%B %Y')
        except:
            month_key = 'unknown'
            month_name = 'Unknown'
        
        if month_key not in history:
            history[month_key] = {
                'month': month_name,
                'count': 0,
                'tasks': []
            }
        
        # Get description and labels safely
        try:
            description = task['description'] or ''
        except (KeyError, IndexError):
            description = ''
        
        try:
            labels = json.loads(task['labels']) if task['labels'] else []
        except (KeyError, IndexError):
            labels = []
        
        history[month_key]['count'] += 1
        history[month_key]['tasks'].append({
            'id': task['id'],
            'title': task['title'],
            'description': description,
            'estimatedTime': task['estimated_time'],
            'labels': labels,
            'completedAt': completed_date,
            'createdAt': task['created_at'],
            'subtasks': [dict(st) for st in subtasks]
        })
    
    conn.close()
    return jsonify(history)

# Habits endpoints
@app.route('/api/habits', methods=['GET'])
def get_habits():
    """Get all habits"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM habits ORDER BY id')
    habits = cursor.fetchall()
    
    result = [dict(habit) for habit in habits]
    conn.close()
    return jsonify(result)

@app.route('/api/habits', methods=['POST'])
def save_habits():
    """Save or update habits"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Clear existing habits
        cursor.execute('DELETE FROM habits')
        
        # Insert new habits
        for habit in data:
            cursor.execute('''
                INSERT INTO habits (id, name, streak, completed_today)
                VALUES (?, ?, ?, ?)
            ''', (
                habit['id'],
                habit['name'],
                habit['streak'],
                1 if habit['completedToday'] else 0
            ))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Habits saved successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

@app.route('/api/habits/<int:habit_id>', methods=['PUT'])
def update_habit(habit_id):
    """Update a single habit"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE habits
        SET name = ?, streak = ?, completed_today = ?
        WHERE id = ?
    ''', (
        data['name'],
        data['streak'],
        1 if data['completedToday'] else 0,
        habit_id
    ))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Habit updated successfully"})

# Habit history endpoints
@app.route('/api/habit-history', methods=['GET'])
def get_habit_history():
    """Get all habit history"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM habit_history')
    history = cursor.fetchall()
    
    # Format as {habit_id: {date: true}}
    result = {}
    for record in history:
        habit_id = str(record['habit_id'])
        if habit_id not in result:
            result[habit_id] = {}
        result[habit_id][record['date']] = bool(record['completed'])
    
    conn.close()
    return jsonify(result)

@app.route('/api/habit-history', methods=['POST'])
def save_habit_history():
    """Save habit history"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Clear existing history
        cursor.execute('DELETE FROM habit_history')
        
        # Insert new history
        for habit_id, dates in data.items():
            for date, completed in dates.items():
                cursor.execute('''
                    INSERT INTO habit_history (habit_id, date, completed)
                    VALUES (?, ?, ?)
                ''', (int(habit_id), date, 1 if completed else 0))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Habit history saved successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

@app.route('/api/habit-history/<int:habit_id>/<date>', methods=['POST'])
def add_habit_completion(habit_id, date):
    """Add a habit completion for a specific date"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO habit_history (habit_id, date, completed)
            VALUES (?, ?, 1)
        ''', (habit_id, date))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Habit completion recorded"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

@app.route('/api/habit-history/<int:habit_id>/<date>', methods=['DELETE'])
def remove_habit_completion(habit_id, date):
    """Remove a habit completion for a specific date"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM habit_history WHERE habit_id = ? AND date = ?', (habit_id, date))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Habit completion removed"})

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists(DATABASE):
        print("Creating new database...")
        init_db()
    
    print("Starting Flow Tracker Backend Server...")
    print("Server running on http://localhost:5000")
    print("API endpoints available at http://localhost:5000/api/")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
