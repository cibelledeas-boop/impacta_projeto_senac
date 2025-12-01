# route.py
# Rotas principais do projeto Impacta

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def feed():
    return render_template('feed.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/direct')
def direct():
    return render_template('direct.html')

@app.route('/notificacoes')
def notificacoes():
    return render_template('notificacoes.html')

if __name__ == '__main__':
    app.run(debug=True)
