import os
from flask import current_app, url_for
from werkzeug.utils import secure_filename

def handle_image_upload(file, item_id):
    # Retrieve upload folder from the app's config
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        try:
            file.save(file_path)
            url = url_for('static', filename=f'uploads/{filename}', _external=False)
            print(f"Generated URL: {url}")  # Print the URL
            return url
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    return None
