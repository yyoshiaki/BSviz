from datetime import datetime
import os

from flask import Flask, render_template, request, make_response, jsonify
import werkzeug

def process_zip(file, UPLOAD_DIR):
    print("hi")

    if 'uploadFile' not in file:
        return [0, make_response(jsonify({'result':'uploadFile or Fasta is required.'}))]

    file = file['uploadFile']

    print(file)
    fileName = file.filename
    if '' == fileName:
        return [0, make_response(jsonify({'result':'filename must not empty.'}))]
   
    saveFileName = datetime.now().strftime("%Y%m%d_%H%M%S_") \
         + werkzeug.utils.secure_filename(fileName)

    if not saveFileName.endswith(".zip"):
        return [0, make_response(jsonify({'result':'uploadFile must be a zip file.'}))]
    print("file", saveFileName)
    saveFilePath = os.path.join(UPLOAD_DIR, saveFileName)
    file.save(saveFilePath)

    os.remove(saveFilePath)

    fasta = "fasta edit here!"
    return [1, fasta]

def check_fasta():
    print("Opps")