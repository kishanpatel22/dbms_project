import os
from flask import current_app, flash
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def upload_file(request):
    """Upload a file to the server and return success status"""

    # pretty_print_POST(request)

    # check if POST object has a file
    if 'file' not in request.files:
        flash('No file part')
        return False
    file = request.files['file']

    # accept only if file has a name
    if file.filename == '':
        flash('No selected file')
        return False
    
    if file and allowed_file(file.filename):
        # sanitize the filename
        filename = secure_filename(file.filename)
        # file.save(os.path.join("~/Downloads", filename))
        file.save(os.path.join(current_app.config['IMAGE_FOLDER'], filename))
        return True
    
    return False