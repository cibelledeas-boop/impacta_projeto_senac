import os  # Importa funções do sistema operacional
from flask import Flask, render_template, request, redirect, url_for, session, jsonify  # Importa funções do Flask
from werkzeug.utils import secure_filename  # Garante nomes seguros para arquivos
import uuid  # Gera IDs únicos
import json  # Manipula arquivos JSON
from datetime import datetime  # Usa data e hora
import google.generativeai as genai  # API Gemini
from dotenv import load_dotenv  # Carrega variáveis do arquivo .env

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "senac123")  # Chave da sessão

# Caminho do arquivo JSON de publicações
PUBLICACOES_JSON = os.path.join(os.path.dirname(__file__), 'publicacoes.json')

# Função para carregar publicações
def carregar_publicacoes():
    if os.path.exists(PUBLICACOES_JSON):
        with open(PUBLICACOES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Função para salvar publicações
def salvar_publicacoes():
    with open(PUBLICACOES_JSON, 'w', encoding='utf-8') as f:
        json.dump(publicacoes, f, ensure_ascii=False, indent=2)

publicacoes = carregar_publicacoes()

# Gera ID único
def gerar_id():
    return str(uuid.uuid4())

# Caminho para salvar imagens
UPLOAD_FOLDER = os.path.join('app', 'static', 'img', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Verifica extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- ROTAS DA APLICAÇÃO ----------------

@app.route('/')
def feed():
    return render_template('feed.html', publicacoes=publicacoes)

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


# ---------------- PUBLICAR POST ----------------

@app.route('/publicar', methods=['POST'])
def publicar():
    texto = request.form.get('texto')
    categoria = request.form.get('categoria')
    fotos = request.files.getlist('foto')
    fotos_urls = []

    if fotos:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        for foto in fotos[:4]:
            if foto and allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                foto.save(save_path)
                fotos_urls.append(f'img/uploads/{filename}')

    if texto:
        post = {
            'id': gerar_id(),
            'autor': 'Usuário',
            'categoria': categoria,
            'texto': texto,
            'fotos_urls': fotos_urls,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'curtidas': 0,
            'comentarios': []
        }
        publicacoes.insert(0, post)
        salvar_publicacoes()

    return redirect(url_for('feed'))


# ---------------- CURTIR POST ----------------

@app.route('/curtir/<post_id>', methods=['POST'])
def curtir_post(post_id):
    for post in publicacoes:
        if post['id'] == post_id:
            post['curtidas'] += 1
            salvar_publicacoes()
            break
    return ('', 204)


# ---------------- COMENTAR POST ----------------

@app.route('/comentar/<post_id>', methods=['POST'])
def comentar_post(post_id):
    comentario = request.form.get('comentario')
    autor = request.form.get('autor', 'Usuário')

    for post in publicacoes:
        if post['id'] == post_id and comentario:
            post['comentarios'].append({'autor': autor, 'texto': comentario})
            salvar_publicacoes()
            return '', 200

    return '', 400


# ---------------- EXCLUIR POST ----------------

@app.route('/excluir/<post_id>', methods=['POST'])
def excluir_post(post_id):
    global publicacoes
    publicacoes = [p for p in publicacoes if p['id'] != post_id]
    salvar_publicacoes()
    return ('', 204)


# ---------------- CHATBOT (GEMINI) ----------------

# Carrega chave do .env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configura API Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Limite de tokens do histórico
MAX_TOKENS_HISTORY = 200000

# Persona fixa da assistente Nati
PERSONA_NATI = """
Você é Nati, assistente social digital do Impacta.
Sua missão é orientar, acolher, explicar recursos do site
e conversar com empatia. Nunca diga que é uma IA.
"""

# Função para estimar tokens
def estimate_tokens(messages):
    return sum(len(m["role"]) + len(m["content"]) for m in messages) // 2


@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip()

        # Rejeita mensagens vazias
        if not user_msg:
            return jsonify({"erro": "Mensagem vazia"}), 400

        # Rejeita spam
        if len(user_msg) < 2:
            return jsonify({"erro": "Mensagem muito curta"}), 400

        # Carrega histórico
        if "chat_history" not in session:
            session["chat_history"] = [
                {"role": "system", "content": PERSONA_NATI}
            ]

        history = session["chat_history"]

        # Salva mensagem do usuário
        history.append({"role": "user", "content": user_msg})

        # Limpa se atingir limite
        if estimate_tokens(history) > MAX_TOKENS_HISTORY:
            history = history[-30:]
            history.insert(0, {"role": "system", "content": PERSONA_NATI})

        # Junta histórico em texto
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in history])

        # Modelo Gemini correto
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Gera resposta
        response = model.generate_content(prompt)
        bot_reply = response.text

        # Resposta de fallback
        if not bot_reply.strip():
            bot_reply = "Desculpe, tive um problema ao responder. Pode tentar novamente?"

        # Salva resposta no histórico
        history.append({"role": "assistant", "content": bot_reply})
        session["chat_history"] = history

        return jsonify({"resposta": bot_reply})

    except Exception as e:
        return jsonify({"erro": f"Erro ao conectar à IA: {e}"}), 500


# ---------------- EXECUTAR SERVIDOR ----------------

if __name__ == '__main__':
    app.run(debug=True)
