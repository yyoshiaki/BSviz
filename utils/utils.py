from datetime import datetime
import os
import shutil
import zipfile

from flask import Flask, render_template, request, make_response, jsonify
import werkzeug

from skbio import DNA
from skbio.alignment import local_pairwise_align_ssw

def process_zip(file, UPLOAD_DIR):
    print("hi")

    if 'uploadFile' not in file:
        # return [0, make_response(jsonify({'result':'uploadFile or Fasta is required.'}))]
        return [0, render_template('error.html', error='uploadFile or Fasta is required.')]

    file = file['uploadFile']

    print(file)
    fileName = file.filename
    if '' == fileName:
        # return [0, make_response(jsonify({'result':'filename must not empty.'}))]
        return [0, render_template('error.html', error='filename must not empty.')]
   
    saveFileName = datetime.now().strftime("%Y%m%d_%H%M%S_") \
         + werkzeug.utils.secure_filename(fileName)

    if not saveFileName.endswith(".zip"):
        # return [0, make_response(jsonify({'result':'uploadFile must be a zip file.'}))]
        return [0, render_template('error.html', error='uploadFile must be a zip file.')]
    print("file", saveFileName)
    saveFilePath = os.path.join(UPLOAD_DIR, saveFileName)
    file.save(saveFilePath)

    dir_extracted = saveFilePath.replace('.zip', '')

    with zipfile.ZipFile(saveFilePath) as zf:
        zf.extractall(dir_extracted)

    dir_extracted = dir_extracted + '/' + fileName.replace(".zip", "")
    f_fa = dir_extracted + "/" + "tmp.fa"
    list_sample = os.listdir(dir_extracted)
    # print(list_sample)

    fasta = convert_seq2fasta(dir_extracted, f_fa)

    os.remove(saveFilePath)
    shutil.rmtree(dir_extracted)

    return [1, fasta]

def check_fasta(fasta):
    print("Opps")

def convert_seq2fasta(dir_seqs, f_fa):
    list_files = os.listdir(dir_seqs)

    # chack file types
    list_files = [x for x in list_files if x.endswith('.seq')]

    if len(list_files) == 0:
        print('No .seq file was contained.')

    list_tmp = []
    for f in list_files:
        path = '{}/'.format(dir_seqs) + f

        with open(path, 'r') as file:
            seq = file.read()
            seq = seq.replace('\n', '')
            seq = DNA(seq)
            try:
                seq = DNA(seq)
            except:
                print('Error occured. See ', path)

        seq.metadata = {"id" : f}
        seq.write('{d}/tmp.{f}.fa'.format(d=dir_seqs, f=f))
        list_tmp.append('{d}/tmp.{f}.fa'.format(d=dir_seqs, f=f))

    out = ""
    for f in list_tmp:
        with open(f, 'r') as file:
            out += file.read()
    #         out += '\n'
        os.remove(f)

    with open(f_fa, 'w') as f:
        f.write(out)

    return out