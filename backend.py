from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
import json
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_metadata(filename):
    metadata_file = os.path.join(UPLOAD_FOLDER, 'metadata.json')
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = []
    
    metadata.append({"filename": filename})
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

def commit_and_push():
    subprocess.run(['git', 'add', 'static/uploads'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Updated photo uploads'], check=True)
    subprocess.run(['git', 'push'], check=True)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        save_metadata(filename)
        commit_and_push()
        return jsonify({"success": "File uploaded and pushed to GitHub"})
    
    return jsonify({"error": "Invalid file type"})

if __name__ == '__main__':
    app.run(debug=True)

# Frontend (upload.html)
UPLOAD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photo Uploader</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        form { margin-top: 20px; }
    </style>
</head>
<body>
    <h2>Upload Photos</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="image/*" required>
        <button type="submit">Upload</button>
    </form>
</body>
</html>
"""

with open('templates/upload.html', 'w') as f:
    f.write(UPLOAD_HTML)
