import os
from flask import url_for
from werkzeug.utils import secure_filename

def handle_image_upload(file, item_id):
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            file.save(file_path)
            return url_for('static', filename=f'uploads/{filename}')
        except Exception as e:
            return None
    return None
