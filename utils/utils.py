import base64
from io import BytesIO
from datetime import datetime
import os
import shutil
import zipfile
import subprocess

from flask import Flask, render_template, request, make_response, jsonify
import werkzeug
import pandas as pd
import matplotlib.pyplot as plt
from skbio import DNA
from skbio.alignment import local_pairwise_align_ssw


def make_tmpdir(UPLOAD_DIR):
    dir_tmp = UPLOAD_DIR + '/job_' +datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(dir_tmp, exist_ok=True)
    return dir_tmp


def process_files(files, dir_tmp):
    file_types = [x.filename.split('.')[-1] for x in files]
    print(file_types)

    fasta = ''
    # file = files[0]
    # print(str(file.read()))

    if set(file_types) == {'zip'}:
        for file in files:
            fasta += process_zip(file, dir_tmp)[1]
    elif (set(file_types) == {'fa'}) or (set(file_types) == {'.fasta'}):
        for file in files:
            fasta += file.read().decode('utf-8')
    elif set(file_types) == {'seq'}:
        for file in files:
            fasta += '>' + file.filename + '\n'
            fasta += file.read().decode('utf-8')
    
    if fasta != "":
        return [1, fasta]
    else:
        return [0, fasta]

def process_zip(file, dir_tmp):
    # if 'uploadFile' not in file:
    #     # return [0, make_response(jsonify({'result':'uploadFile or Fasta is required.'}))]
    #     return [0, render_template('error.html', error='uploadFile or Fasta is required.')]
    fileName = file.filename
    if '' == fileName:
        # return [0, make_response(jsonify({'result':'filename must not empty.'}))]
        return [0, render_template('error.html', error='filename must not empty.')]
   
    saveFileName = werkzeug.utils.secure_filename(fileName)

    if not saveFileName.endswith(".zip"):
        # return [0, make_response(jsonify({'result':'uploadFile must be a zip file.'}))]
        return [0, render_template('error.html', error='uploadFile must be a zip file.')]
    print("file", saveFileName)
    saveFilePath = os.path.join(dir_tmp, saveFileName)
    file.save(saveFilePath)

    dir_extracted = saveFilePath.replace('.zip', '')

    with zipfile.ZipFile(saveFilePath) as zf:
        zf.extractall(dir_extracted)

    dir_extracted = dir_extracted + '/' + fileName.replace(".zip", "")
    f_fa = dir_extracted + "/" + "tmp.fa"
    # list_sample = os.listdir(dir_extracted)
    # print(list_sample)

    fasta = convert_seq2fasta(dir_extracted, f_fa)
    os.remove(saveFilePath)

    return [1, fasta]


def trim_fasta(fasta, res1, res2):
    trimmed_fasta = []
    for i, x in enumerate(fasta.split()):
        if i%2 == 0:
            trimmed_fasta.append(x)
        else:
            trimmed = trim(x, res1, res2)
            if trimmed == "":
                trimmed_fasta.pop()
            else:
                trimmed_fasta.append(trimmed)

    return '\n'.join(trimmed_fasta)


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

    # with open(f_fa, 'w') as f:
    #     f.write(out)

    return out


def trim(seq, res1, res2):
    if res1 != res2:
        seq = DNA(seq)
        alignment1, score1, start_end_positions1 = local_pairwise_align_ssw(seq, DNA(res1))
        alignment2, score2, start_end_positions2 = local_pairwise_align_ssw(seq, DNA(res2))

        # trim only when both restrection enzyme was recognized.
        if (score1 >=10) & (score2 >=10):
            L = (list(start_end_positions1[0]) + list(start_end_positions2[0]))
            L.sort()
            s = L[1]
            e = L[2]
            return str(seq[s:e])
        else:
            print(score1, score2)
            return ""
    else:
        seq = DNA(seq)
        alignment1, score1, start_end_positions1 = local_pairwise_align_ssw(seq, DNA(res1))
        seq1 = seq[:start_end_positions1[0][0]]
        seq2 = seq[start_end_positions1[0][1]:]

        alignment21, score21, start_end_positions21 = local_pairwise_align_ssw(seq1, DNA(res2))
        alignment22, score22, start_end_positions22 = local_pairwise_align_ssw(seq2, DNA(res2))

        if score21 >= score22:
            return str(seq1[start_end_positions21[0][1]:])
        else:
            return str(seq2[:start_end_positions22[0][0]])


def run_bismark(p, dir_tmp, f_fa, species, f_bismark_index):
    cmd = "bismark --parallel {p} --output_dir {o} --temp_dir {o} --non_directional --score_min L,0,-1 -f " +\
            "--genome  {f_bismark_index} {f_fa}"
    cmd = cmd.format(p=p, o=dir_tmp, f_bismark_index=f_bismark_index, f_fa=f_fa)
    print(cmd)
    subprocess.run(cmd, shell=True)

    cmd = 'bismark_methylation_extractor --output {o} --gzip --bedGraph --comprehensive {}_bismark_bt2.bam'
    cmd = cmd.format(f_fa, o=dir_tmp)
    print(cmd)
    subprocess.run(cmd, shell=True)

    return dir_tmp + '/CpG_context_input.fasta_bismark_bt2.txt.gz'


def plot_bismark(dir_tmp, f_bismark, threshold_rate_undetected, f_out, bt_gff3):
    df_bismark = pd.read_csv(f_bismark, sep='\t', skiprows=[0], header=None)
    df_bismark.columns=['read', 'strand', 'chr', 'pos', 'meth']
    df_bismark = df_bismark.pivot(index='read', columns='pos', values='meth')
    df_bismark.columns=df_bismark.columns.astype(str)

    # methylated CpG : 1, unmethylated CpG : 0
    df_bismark = df_bismark.replace('Z', 1).replace('z', 0)

    # remove positions with many undetected reads.
    df_bismark = df_bismark.loc[:,df_bismark.isna().sum() < (df_bismark.shape[0]) * threshold_rate_undetected]

    # sort reads by methylation
    sorted_ind = df_bismark.sum(axis=1).sort_values(ascending=False).index
    df_bismark = df_bismark.loc[sorted_ind]

    gene = query_gene(df_bismark, bt_gff3)

    df=df_bismark.melt(value_name='methylation')
    list_index=list(sorted_ind)
    reads_num = list_index*(df_bismark.shape[1])
    df["read"]=reads_num

    df_0 = df[df.methylation==0.0]
    df_1 = df[df.methylation==1.0]
    df_N = df[df.isnull().any(axis=1)]

    data_2 = {
        "pos":list(df["pos"]), 
        "read":list(reversed(reads_num)),
        "methylation":[0]*len(df.index)
    }

    df_mat_2 = pd.DataFrame(data_2)

    fig, ax = plt.subplots(figsize=(df_bismark.shape[1]/2, df_bismark.shape[0]/2 + .2))
    plt.xticks(rotation=90)

    ax.scatter(x="pos", y="read", data=df_mat_2, marker="", label=None)
    ax.scatter(x="pos", y="read", data=df_1, s=500, linewidths='2', 
            c='#000000', edgecolors='black', label='Methylated')
    ax.scatter(x="pos", y="read", data=df_0, s=500, linewidths='2', 
            c='#ffffff', edgecolors='black', label='Unmethylated')
    ax.scatter(x="pos", y="read", data=df_N, c='#0000ff', marker=".", label='Undetected')

    ax.legend(bbox_to_anchor=(1.1, 0.5), frameon=False, labelspacing=2)
    ax.spines["right"].set_color("none") 
    ax.spines["left"].set_color("none")  
    ax.spines["top"].set_color("none")   
    ax.spines["bottom"].set_color("none")

    ax.set_xlabel('position')
    ax.set_ylim(-0.5,df_bismark.shape[0])
    ax.set_title(gene)
    

    buf = BytesIO()
    # fig.savefig(buf, format="png", bbox_inches='tight', dpi=350)
    # data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.savefig(dir_tmp+'/'+f_out, format="png", bbox_inches='tight', dpi=350)
    # data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return dir_tmp+'/'+f_out


def query_gene(df_bismark, bt_gff3):
    # f_bismark = "data/200522_BSseq_PCR/CpG_context_sample_3.fa_bismark_bt2.txt.gz"
    # f_CpG = "CpG_context_sample_2.fa_bismark_bt2.txt"
    # f_bismark = "data/CpG_context_input.fasta_bismark_bt2.txt.gz"

    # df_bismark = pd.read_csv(f_CpG, sep='\t', skiprows=[0], header=None)
    # df_bismark.columns=['read', 'strand', 'chr', 'pos', 'meth']

    chr_num = list(set(list(df_bismark["chr"])))

    df_bismark = df_bismark.pivot(index='read', columns='pos', values='meth')

    gene_pos = list(df_bismark.columns)
    bed_ori = "{}\t{}\t{}".format(chr_num[0], gene_pos[0], gene_pos[-1])

    bed = BedTool(bed_ori, from_string=True)


    query = bt_gff3.intersect(bed)
    list_gene = []
    for data in query:
        if data[2]=="gene":
            attr = list(data.attrs.items())
            gene_list.append(attr[3][1])
            print("{} {} {}:{}".format(data[0], data[3], data[4], attr[3][1]))
    
    return '; '.join(list_gene)
