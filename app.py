from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def input():
    return render_template("input.html")

@app.route('/', methods=['POST'])
def output():
    species = request.form["species"]
    enz1 = request.form['enz1']
    enz2 = request.form['enz2']
    fasta = request.form['fasta']
    return render_template('output.html', species=species, enz1=enz1, enz2=enz2, fasta=fasta, title='出力ページ')

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)
