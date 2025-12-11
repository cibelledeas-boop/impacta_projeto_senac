import os  # Importa funções do sistema operacional
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash  # Importa funções do Flask
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


# ------------------- AUTENTICAÇÃO E USUÁRIOS (JSON) -------------------
from werkzeug.security import generate_password_hash, check_password_hash

# Caminho do arquivo JSON de usuários
USUARIOS_JSON = os.path.join(os.path.dirname(__file__), 'banco_dados', 'usuarios.json')

def carregar_usuarios():
    if os.path.exists(USUARIOS_JSON):
        with open(USUARIOS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_usuarios(usuarios):
    with open(USUARIOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

@app.route("/login", methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("feed"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        usuarios = carregar_usuarios()
        user = next((u for u in usuarios if u["email"] == email), None)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Bem-vindo(a), {user['name']}!", "success")
            return redirect(url_for("feed"))
        else:
            flash("E-mail ou senha inválida.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        if password != confirm_password:
            flash("As senhas não conferem.", "danger")
            return redirect(url_for("register"))
        usuarios = carregar_usuarios()
        if any(u["email"] == email for u in usuarios):
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("register"))
        new_id = max([u["id"] for u in usuarios], default=0) + 1
        password_hash = generate_password_hash(password)
        novo_usuario = {
            "id": new_id,
            "name": name,
            "email": email,
            "password_hash": password_hash
        }
        usuarios.append(novo_usuario)
        salvar_usuarios(usuarios)
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/forgot_password", methods=["GET"])
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/forgot_password", methods=["POST"])
def forgot_password_submit():
    email = request.form.get("email", "").strip()
    usuarios = carregar_usuarios()
    if any(u["email"] == email for u in usuarios):
        flash("Se o e-mail existir, você receberá um link para redefinir a senha.", "info")
    else:
        flash("Informe um e-mail válido.", "danger")
    return redirect(url_for("forgot_password"))

@app.route("/termos")
def termos():
    return "<h1>Termos de Uso</h1><p>Exemplo.</p>"

@app.route("/home")
def home():
    if "user_id" not in session:
        flash("Faça login para acessar.", "warning")
        return redirect(url_for("login"))
    return render_template("home.html", name=session.get("user_name"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))

# PERFIL E FOTO -------------------
@app.route('/perfil')
def perfil():
    if "user_id" not in session:
        flash("Faça login para acessar seu perfil.", "warning")
        return redirect(url_for("login"))

    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u["id"] == session["user_id"]), None)

    # Foto padrão caso o usuário não tenha foto
    foto_perfil = usuario.get("foto_perfil")
    if not foto_perfil or foto_perfil.strip() == "":
        foto_perfil = "img/img_feed/user_padrao_noFoto.png"

    bio = usuario.get("bio", "")

    return render_template(
        'perfil.html',
        usuario_nome=session.get("user_name"),
        usuario_id=session.get("user_id"),
        usuario_foto_perfil=foto_perfil,
        usuario_bio=bio
    )


@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if "user_id" not in session:
        flash("Faça login para editar seu perfil.", "warning")
        return redirect(url_for("login"))

    nome = request.form.get("nome")
    bio = request.form.get("bio")
    foto = request.files.get("foto_perfil")

    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u["id"] == session["user_id"]), None)

    if usuario:
        # Atualiza nome e bio
        if nome:
            usuario["name"] = nome
            session["user_name"] = nome

        usuario["bio"] = bio if bio else ""

        # Atualiza foto
        if foto and allowed_file(foto.filename):
            # Remove a foto antiga se não for a padrão
            foto_antiga = usuario.get("foto_perfil")
            if foto_antiga and not foto_antiga.startswith("img/img_feed/user_padrao_noFoto"):
                caminho_antigo = os.path.join(app.static_folder, foto_antiga.replace("img/", "img\\"))
                if os.path.exists(caminho_antigo):
                    try:
                        os.remove(caminho_antigo)
                    except Exception:
                        pass
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = f"perfil_{usuario['id']}_{secure_filename(foto.filename)}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(save_path)
            usuario["foto_perfil"] = f"img/uploads/{filename}"
        elif not usuario.get("foto_perfil") or usuario["foto_perfil"].strip() == "":
            usuario["foto_perfil"] = "img/img_feed/user_padrao_noFoto.jpg"

        # Salva usuário no JSON
        salvar_usuarios(usuarios)
        flash("Perfil atualizado com sucesso!", "success")

    else:
        flash("Usuário não encontrado.", "danger")

    return redirect(url_for("perfil"))



# Caminho do arquivo JSON de publicações
PUBLICACOES_JSON = os.path.join(os.path.dirname(__file__), 'banco_dados', 'publicacoes.json')

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
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'img', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Verifica extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/excluir_comentario/<post_id>/<int:comment_idx>', methods=['POST'])
def excluir_comentario(post_id, comment_idx):
    for post in publicacoes:
        if post['id'] == post_id:
            if 0 <= comment_idx < len(post['comentarios']):
                post['comentarios'].pop(comment_idx)
                salvar_publicacoes()
                return redirect(url_for('feed'))
    return '', 400


# ---------------- ROTAS DA APLICAÇÃO ----------------

@app.route('/')
def feed():
    if "user_id" not in session:
        flash("Faça login para acessar o feed.", "warning")
        return redirect(url_for("login"))
    return render_template('feed.html', publicacoes=publicacoes, usuario_nome=session.get("user_name"), usuario_id=session.get("user_id"))

@app.route('/landing')
def landing():
    return render_template('landing.html')



@app.route('/direct')
def direct():
    return render_template('direct.html')

@app.route('/notificacoes')
def notificacoes():
    return render_template('notificacoes.html')


# ---------------- PUBLICAR POST ----------------


@app.route('/publicar', methods=['POST'])
def publicar():
    if "user_id" not in session:
        flash("Faça login para publicar.", "warning")
        return redirect(url_for("login"))
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
        # Buscar foto de perfil do usuário logado
        usuarios = carregar_usuarios()
        usuario = next((u for u in usuarios if u["id"] == session.get("user_id")), None)
        foto_perfil = usuario.get("foto_perfil") if usuario and usuario.get("foto_perfil") else "img/img_feed/user_padrao_noFoto.png"
        post = {
            'id': gerar_id(),
            'autor': session.get('user_name', 'Usuário'),
            'autor_id': session.get('user_id'),
            'foto_perfil': foto_perfil,
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



@app.route('/curtir/<post_id>', methods=['POST'])
def curtir_post(post_id):
    for post in publicacoes:
        if post['id'] == post_id:
            post['curtidas'] += 1
            salvar_publicacoes()
            break
    return ('', 204)



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



@app.route('/excluir/<post_id>', methods=['POST'])
def excluir_post(post_id):
    global publicacoes
    publicacoes = [p for p in publicacoes if p['id'] != post_id]
    salvar_publicacoes()
    return ('', 204)





GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configura API Gemini
genai.configure(api_key=GOOGLE_API_KEY)


MAX_TOKENS_HISTORY = 200000


PERSONA_NATI = """
Você é Nati, assistente social digital do Impacta.
Sua missão é orientar, acolher, explicar recursos do site
e conversar com empatia. Nunca diga que é uma IA.
"""

#
def estimate_tokens(messages):
    return sum(len(m["role"]) + len(m["content"]) for m in messages) // 2


@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip()

        if not user_msg:
            return jsonify({"erro": "Mensagem vazia"}), 400

        
        if len(user_msg) < 2:
            return jsonify({"erro": "Mensagem muito curta"}), 400

        
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

        
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in history])

        model = genai.GenerativeModel("gemini-2.5-flash")

      
        response = model.generate_content(prompt)
        bot_reply = response.text

        if not bot_reply.strip():
            bot_reply = "Desculpe, tive um problema ao responder. Pode tentar novamente?"

        
        history.append({"role": "assistant", "content": bot_reply})
        session["chat_history"] = history

        return jsonify({"resposta": bot_reply})

    except Exception as e:
        return jsonify({"erro": f"Erro ao conectar à IA: {e}"}), 500




if __name__ == '__main__':
    app.run(debug=True)
