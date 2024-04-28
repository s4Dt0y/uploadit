from flask import Blueprint, request, abort, flash, redirect ,send_from_directory, render_template, current_app, url_for
from uploadit import db
from uploadit.models import File
from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.orm as so

upload_page = Blueprint("upload", __name__)

@upload_page.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files["file"]
        except KeyError:
            return "No file chosen", 422

        file_uuid = request.form["dzuuid"]
        # Generate a unique filename to avoid overwriting using 8 chars of uuid before filename.
        secure_filename_var = f"{file_uuid[:8]}_{secure_filename(file.filename)}"
        save_path = Path(current_app.config["UPLOAD_DIRECTORY"], secure_filename_var)
        current_chunk = int(request.form["dzchunkindex"])

        try:
            with open(save_path, "ab") as f:
                f.seek(int(request.form["dzchunkbyteoffset"]))
                f.write(file.stream.read())
        except OSError as e:
            print(f'Error: {e}')
            return "Error saving file.", 500

        total_chunks = int(request.form["dztotalchunkcount"])

        if current_chunk + 1 == total_chunks:
            # This was the last chunk, the file should be complete and the size we expect
            if os.path.getsize(save_path) != int(request.form["dztotalfilesize"]):
                return "Size mismatch.", 500

        key = random_string()
        data = File(filekey=key, filename=file.filename, secure_filename=secure_filename_var)
        db.session.add(data)
        db.session.commit()

        flash(f'Upload Complete. The file {secure_filename_var} has been saved with the key {key}')
        return "Upload Completed", 200
    
    elif request.method == 'GET':
        return render_template('upload.html')