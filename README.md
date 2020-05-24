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
python app.py
```

Access `http://127.0.0.1:5000/`

## Export enviromnent.yaml (Only for developers)

### Linux

```
conda create -n TregBSPCR_webapp python=3.7 anaconda
pip install flask
conda install -c https://conda.anaconda.org/biocore scikit-bio
conda install -c bioconda bismark
conda list --export > environment.linux.yaml
```

### Mac OS

```
conda create -n TregBSPCR_webapp python=3.7 anaconda
pip install flask
conda install -c https://conda.anaconda.org/biocore scikit-bio
conda install -c bioconda bismark
conda list --export > environment.macos.yaml
```


## Developpers

Yoshiaki Yasumizu, Yasunari Matsumoto
