# TregBSPCR_webapp

## Setup

### Linux

```
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge

conda create --name TregBSPCR_webapp --file environment.linux.yaml
conda activate TregBSPCR_webapp
```

### Mac OS

```
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge

conda create --name TregBSPCR_webapp --file environment.macos.yaml
conda activate TregBSPCR_webapp
```
 
## Launch 

```
python app.py 5000
```

Access `http://127.0.0.1:5000/`

## Export enviromnent.yaml (Only for developers)

### Linux

```
conda create -n TregBSPCR_webapp python=3.7 anaconda
conda activate TregBSPCR_webapp
conda install -c https://conda.anaconda.org/biocore scikit-bio
conda install -c bioconda bismark pybedtools
# pip install pybedtools
conda install openblas
conda list --export | grep -v "pyqt" > environment.linux.yaml
```

### Mac OS

```
conda create -n TregBSPCR_webapp python=3.7 anaconda
conda activate TregBSPCR_webapp
conda install -c https://conda.anaconda.org/biocore scikit-bio
conda install -c bioconda bismark
pip install pybedtools
conda install openblas
conda list --export | grep -v "pyqt" > environment.macos.yaml
```

### build bismark index

```
mkdir -p ~/reference/bismark/Gencode_v34/fasta
cd ~/reference/bismark/Gencode_v34/fasta
wget ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_34/GRCh38.p13.genome.fa.gz
bismark_genome_preparation --parallel 40 ~/reference/bismark/Gencode_v34/fasta

mkdir -p ~/reference/bismark/Gencode_M25/fasta
cd ~/reference/bismark/Gencode_M25/fasta
wget ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M25/GRCm38.p6.genome.fa.gz
bismark_genome_preparation --parallel 40 ~/reference/bismark/Gencode_M25/fasta
```

## download reference

```
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_34/gencode.v34.annotation.gff3.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M25/gencode.vM25.annotation.gff3.gz
```

## Developpers

Yoshiaki Yasumizu, Yasunari Matsumoto

## Licence

This software is freely available for academic users. Usage for commercial purposes is not allowed. Please refer to the LICENCE page.

<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a>