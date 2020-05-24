import base64
from io import BytesIO

from flask import Flask, render_template, request
import numpy as np
from matplotlib.figure import Figure
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter


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

    figs = []

    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.gca(projection='3d')

    # Make data.
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R)

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis,
                        linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    figs.append(data)

    return render_template('output.html', species=species, enz1=enz1, enz2=enz2, fasta=fasta, figs=figs, title='Result')

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)
