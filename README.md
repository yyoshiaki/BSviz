# TregBSPCR_webapp

Yoshiaki Yasumizu, 

## Setup

```
conda create --name TregBSPCR_webapp --file environment.yaml
conda activate TregBSPCR_webapp
```
 
## Launch 

```
python app.py
```

Access `http://127.0.0.1:5000/`

## Export enviromnent.yaml (Only for developers)

```
conda list --export > environment.yaml
```