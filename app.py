
import os
from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = r'C:\Users\hp\uni.db'

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT MODULES FROM studyfiles WHERE MODULES IS NOT NULL')
    all_modules = [row[0] for row in cursor.fetchall()]
    
    selected_module = request.args.get('module', '')
    search_query = request.args.get('search', '')
    
    query = 'SELECT * FROM studyfiles WHERE 1=1'
    params = []
    
    if selected_module:
        query += ' AND MODULES = ?'
        params.append(selected_module)
        
    if search_query:
        query += ' AND "FILES NAME" LIKE ?'
        params.append(f'%{search_query}%')
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    tree = {}
    total_files = len(rows)
    
    for row in rows:
        mod = row[1] if row[1] else "Non classé"
        cat = row[2] if row[2] else "Général"
        
        if mod not in tree:
            tree[mod] = {}
        if cat not in tree[mod]:
            tree[mod][cat] = []
            
        tree[mod][cat].append(row)

    return render_template('index.html', tree=tree, all_modules=all_modules, selected_module=selected_module, search_query=search_query, total_files=total_files)

@app.route('/open/<int:file_id>')
def open_file(file_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM studyfiles WHERE ID = ?', (file_id,))
    file_row = cursor.fetchone()
    conn.close()
    
    if not file_row:
        return jsonify({'success': False, 'error': 'File not found in DB'}), 404
        
    rel_path = file_row[4] 
    base_study_dir = r"C:\Users\hp\Desktop\study SC-1"
    absolute_path = os.path.join(base_study_dir, rel_path)
    
    print(f"Ouverture du fichier : {absolute_path}")
    
    try:
        if os.path.exists(absolute_path):
            os.startfile(absolute_path)
            return jsonify({'success': True})
        else:
            if os.path.exists(rel_path):
                os.startfile(rel_path)
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Path does not exist on disk'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

