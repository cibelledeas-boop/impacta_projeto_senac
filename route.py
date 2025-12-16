import os  # Importa funções do sistema operacional
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash  # Importa funções do Flask
from werkzeug.utils import secure_filename  # Garante nomes seguros para arquivos
import uuid  # Gera IDs únicos
import json  # Manipula arquivos JSON
from datetime import datetime  # Usa data e hora
import google.generativeai as genai  # API Gemini
from dotenv import load_dotenv  # Carrega variáveis do arquivo .env
from werkzeug.security import generate_password_hash, check_password_hash

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "senac123")  # Chave da sessão


# ------------------- CAMINHOS DOS ARQUIVOS JSON -------------------
USUARIOS_JSON = os.path.join(os.path.dirname(__file__), 'banco_dados', 'usuarios.json')
PUBLICACOES_JSON = os.path.join(os.path.dirname(__file__), 'banco_dados', 'publicacoes.json')
UPLOAD_FOLDER = os.path.join('static', 'img', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Configurações do app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ------------------- FUNÇÕES AUXILIARES -------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gerar_id():
    return str(uuid.uuid4())

# ------------------- FUNÇÕES PARA MANIPULAR USUÁRIOS -------------------
def carregar_usuarios():
    if os.path.exists(USUARIOS_JSON):
        with open(USUARIOS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_usuarios(usuarios):
    with open(USUARIOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

# ------------------- FUNÇÕES PARA MANIPULAR PUBLICAÇÕES -------------------
def carregar_publicacoes():
    if os.path.exists(PUBLICACOES_JSON):
        with open(PUBLICACOES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_publicacoes(publicacoes_list):
    with open(PUBLICACOES_JSON, 'w', encoding='utf-8') as f:
        json.dump(publicacoes_list, f, ensure_ascii=False, indent=2)

# ------------------- AUTENTICAÇÃO E USUÁRIOS -------------------
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
            # Carrega também o tipo do usuário
            session["user_tipo"] = user.get("tipo", "voluntario")
            flash(f"Bem-vindo(a), {user['name']}!", "success")
            return redirect(url_for("feed"))
        else:
            flash("E-mail ou senha inválida.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("feed"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        tipo = request.form.get("tipo", "voluntario")  # Adiciona escolha de tipo
        
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
            "password_hash": password_hash,
            "foto_perfil": "img/img_feed/user_padrao_noFoto.png",
            "tipo": tipo,
            "bio": "",
            "data_cadastro": datetime.now().strftime('%d/%m/%Y')
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

# ------------------- EDITAR PERFIL E FOTO -------------------
@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if "user_id" not in session:
        flash("Faça login para editar seu perfil.", "warning")
        return redirect(url_for("login"))
    
    nome = request.form.get("nome")
    bio = request.form.get("bio")
    tipo = request.form.get("tipo")  # 'voluntario' ou 'beneficiario'
    foto = request.files.get("foto_perfil")
    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u["id"] == session["user_id"]), None)
    
    if usuario:
        if nome:
            usuario["name"] = nome
            session["user_name"] = nome  # Atualiza na sessão também
        
        if bio:
            usuario["bio"] = bio
        
        if tipo in ['voluntario', 'beneficiario']:
            usuario["tipo"] = tipo
            session["user_tipo"] = tipo  # Atualiza na sessão
        
        if foto and allowed_file(foto.filename):
            filename = f"perfil_{usuario['id']}_{secure_filename(foto.filename)}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(save_path)
            usuario["foto_perfil"] = f"img/uploads/{filename}"
        
        # Atualiza o usuário na lista e salva
        for idx, u in enumerate(usuarios):
            if u["id"] == usuario["id"]:
                usuarios[idx] = usuario
                break
        
        salvar_usuarios(usuarios)
        flash("Perfil atualizado com sucesso!", "success")
    else:
        flash("Usuário não encontrado.", "danger")
    
    return redirect(url_for("perfil"))

# ------------------- ROTAS PRINCIPAIS -------------------
@app.route('/')
def feed():
    if "user_id" not in session:
        flash("Faça login para acessar o feed.", "warning")
        return redirect(url_for("login"))
    
    # Carrega todas as publicações do arquivo JSON
    todas_publicacoes = carregar_publicacoes()
    
    # Ordena por timestamp (mais recentes primeiro)
    todas_publicacoes.sort(key=lambda x: datetime.strptime(x.get('timestamp', '01/01/2000 00:00'), '%d/%m/%Y %H:%M'), reverse=True)
    
    return render_template('feed.html', 
                          publicacoes=todas_publicacoes, 
                          usuario_nome=session.get("user_name"), 
                          usuario_id=int(session.get("user_id")),
                          usuario_tipo=session.get("user_tipo"))

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/perfil')
def perfil():
    if "user_id" not in session:
        flash("Faça login para acessar seu perfil.", "warning")
        return redirect(url_for("login"))
    
    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u["id"] == session["user_id"]), None)
    
    if usuario:
        foto_perfil = usuario.get("foto_perfil")
        if not foto_perfil or foto_perfil.strip() == "":
            foto_perfil = "img/img_feed/user_padrao_noFoto.png"
        bio = usuario.get("bio", "")
        tipo = usuario.get("tipo", "voluntario")
        data_cadastro = usuario.get("data_cadastro", "")
        
        # Carrega apenas as publicações do usuário logado
        todas_publicacoes = carregar_publicacoes()
        publicacoes_usuario = [p for p in todas_publicacoes if p.get('autor_id') == session.get("user_id")]
        publicacoes_usuario.sort(key=lambda x: datetime.strptime(x.get('timestamp', '01/01/2000 00:00'), '%d/%m/%Y %H:%M'), reverse=True)
        
        return render_template('perfil.html', 
                             usuario_nome=usuario.get("name"),
                             usuario_id=session.get("user_id"),
                             usuario_foto_perfil=foto_perfil,
                             usuario_bio=bio,
                             usuario_tipo=tipo,
                             usuario_data_cadastro=data_cadastro,
                             publicacoes=publicacoes_usuario,
                             proprio_perfil=True)
    
    flash("Usuário não encontrado.", "danger")
    return redirect(url_for('feed'))

@app.route('/perfil/<int:user_id>')
def ver_perfil(user_id):
    if "user_id" not in session:
        flash("Faça login para acessar perfis.", "warning")
        return redirect(url_for("login"))
    
    # Carrega informações do usuário
    usuarios = carregar_usuarios()
    usuario = next((u for u in usuarios if u["id"] == user_id), None)
    
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('feed'))
    
    # Carrega apenas as publicações desse usuário
    todas_publicacoes = carregar_publicacoes()
    publicacoes_usuario = [p for p in todas_publicacoes if p.get('autor_id') == user_id]
    
    # Ordena por data (mais recente primeiro)
    publicacoes_usuario.sort(key=lambda x: datetime.strptime(x.get('timestamp', '01/01/2000 00:00'), '%d/%m/%Y %H:%M'), reverse=True)
    
    # Verifica se é o próprio perfil
    proprio_perfil = (session.get('user_id') == user_id)
    
    return render_template('perfil.html',
                          usuario_nome=usuario.get('name'),
                          usuario_id=usuario.get('id'),
                          usuario_foto_perfil=(usuario.get('foto_perfil') if usuario.get('foto_perfil') else 'img/img_feed/user_padrao_noFoto.png'),
                          usuario_bio=usuario.get('bio', ''),
                          usuario_tipo=usuario.get('tipo', 'voluntario'),
                          usuario_data_cadastro=usuario.get('data_cadastro', ''),
                          publicacoes=publicacoes_usuario,
                          proprio_perfil=proprio_perfil,
                          usuario_atual_id=session.get('user_id'))

@app.route('/direct')
def direct():
    if "user_id" not in session:
        flash("Faça login para acessar as mensagens.", "warning")
        return redirect(url_for("login"))
    user_id = int(session["user_id"])
    mensagens_path = os.path.join(os.path.dirname(__file__), 'banco_dados', 'mensagens.json')
    if not os.path.exists(mensagens_path):
        conversas = []
    else:
        with open(mensagens_path, 'r', encoding='utf-8') as f:
            conversas = json.load(f)
    # Conversas do usuário
    minhas_conversas = [c for c in conversas if user_id in c['participantes']]
    # Buscar usuários
    usuarios = carregar_usuarios()
    # Conversa selecionada (por ?user_id=... na URL)
    outro_id = request.args.get('user_id', type=int)
    conversa_selecionada = None
    if outro_id:
        conversa_selecionada = next((c for c in minhas_conversas if set(c['participantes']) == set([user_id, outro_id])), None)
    return render_template('direct.html',
        conversas=minhas_conversas,
        usuarios=usuarios,
        usuario_id=user_id,
        conversa_selecionada=conversa_selecionada,
        outro_id=outro_id)



# ------------------- ENVIAR MENSAGEM NO DIRECT -------------------
@app.route('/direct/enviar/<conversa_id>', methods=['POST'])
def enviar_mensagem(conversa_id):
    if "user_id" not in session:
        flash("Faça login para enviar mensagens.", "warning")
        return redirect(url_for("login"))
    texto = request.form.get('mensagem', '').strip()
    if not texto:
        flash("Mensagem vazia.", "warning")
        return redirect(url_for("direct"))
    mensagens_path = os.path.join(os.path.dirname(__file__), 'banco_dados', 'mensagens.json')
    if not os.path.exists(mensagens_path):
        mensagens = []
    else:
        with open(mensagens_path, 'r', encoding='utf-8') as f:
            mensagens = json.load(f)
    conversa = next((c for c in mensagens if c['id'] == conversa_id), None)
    if not conversa:
        flash("Conversa não encontrada.", "danger")
        return redirect(url_for("direct"))
    nova_msg = {
        'remetente_id': session['user_id'],
        'texto': texto,
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    conversa['mensagens'].append(nova_msg)
    with open(mensagens_path, 'w', encoding='utf-8') as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=2)
    return redirect(url_for('direct', user_id=[uid for uid in conversa['participantes'] if uid != session['user_id']][0]))

@app.route('/notificacoes')
def notificacoes():
    if "user_id" not in session:
        flash("Faça login para acessar notificações.", "warning")
        return redirect(url_for("login"))
    return render_template('notificacoes.html')

@app.route('/ajuda')
def ajuda():
    return render_template('ajuda.html')

# ------------------- DIRECT: CRIAR/ABRIR CONVERSA ENTRE DOADOR E INTERESSADO -------------------
@app.route('/direct/novo/<int:user_id>', methods=['GET'])
def direct_novo(user_id):
    if "user_id" not in session:
        flash("Faça login para acessar as mensagens.", "warning")
        return redirect(url_for("login"))
    meu_id = session["user_id"]
    if meu_id == user_id:
        flash("Você não pode iniciar uma conversa consigo mesmo.", "warning")
        return redirect(url_for("direct"))
    # Carregar mensagens existentes
    mensagens_path = os.path.join(os.path.dirname(__file__), 'banco_dados', 'mensagens.json')
    if not os.path.exists(mensagens_path):
        mensagens = []
    else:
        with open(mensagens_path, 'r', encoding='utf-8') as f:
            mensagens = json.load(f)
    # Procurar conversa existente (ordem dos ids não importa)
    conversa = next((c for c in mensagens if set(c['participantes']) == set([meu_id, user_id])), None)
    if not conversa:
        # Criar nova conversa
        conversa = {
            'id': gerar_id(),
            'participantes': [meu_id, user_id],
            'mensagens': []
        }
        mensagens.append(conversa)
        with open(mensagens_path, 'w', encoding='utf-8') as f:
            json.dump(mensagens, f, ensure_ascii=False, indent=2)
  
    return redirect(url_for('direct', user_id=user_id))

# ------------------- PUBLICAR POST (AGORA VINCULADO AO USUÁRIO DA SESSÃO) -------------------

@app.route('/publicar', methods=['POST'])
def publicar():
    if "user_id" not in session:
        flash("Faça login para publicar.", "warning")
        return redirect(url_for("login"))
    
    texto = request.form.get('texto')
    categoria = request.form.get('categoria')
    tipo_post = request.form.get('tipo_post', 'geral')
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
        usuarios = carregar_usuarios()
        usuario = next((u for u in usuarios if u["id"] == session.get("user_id")), None)
        if not usuario:
            flash("Erro: usuário não encontrado. Faça login novamente.", "danger")
            return redirect(url_for("logout"))
        foto_perfil = usuario.get("foto_perfil")
        if not foto_perfil or foto_perfil.strip() == "":
            foto_perfil = "img/img_feed/user_padrao_noFoto.png"
        autor_nome = session.get("user_name", usuario.get("name", "Usuário"))
        autor_tipo = session.get("user_tipo", usuario.get("tipo", "voluntario"))
        todas_publicacoes = carregar_publicacoes()
        post = {
            'id': gerar_id(),
            'autor': autor_nome,
            'autor_id': session.get("user_id"),
            'autor_tipo': autor_tipo,
            'foto_perfil': foto_perfil,
            'categoria': categoria,
            'tipo_post': tipo_post,
            'texto': texto,
            'fotos_urls': fotos_urls,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'curtidas': 0,
            'curtidores': [],  # NOVO: lista de user_ids que curtiram
            'comentarios': [],
            'status': 'ativo'
        }
        todas_publicacoes.insert(0, post)
        salvar_publicacoes(todas_publicacoes)
        flash("Postagem publicada com sucesso!", "success")
    else:
        flash("Digite algo para publicar.", "warning")
    return redirect(url_for('feed'))
# ------------------- REPORTAR POST -------------------
@app.route('/reportar/<post_id>', methods=['POST'])
def reportar_post(post_id):
    if "user_id" not in session:
        flash("Faça login para reportar postagens.", "warning")
        return redirect(url_for("login"))
    publicacoes = carregar_publicacoes()
    post = next((p for p in publicacoes if p['id'] == post_id), None)
    if post:
        # Adiciona campo de reports se não existir
        if 'reports' not in post:
            post['reports'] = []
        # Evita múltiplos reports do mesmo usuário
        if session['user_id'] not in post['reports']:
            post['reports'].append(session['user_id'])
            salvar_publicacoes(publicacoes)
            flash("Post reportado para análise da equipe.", "info")
        else:
            flash("Você já reportou este post.", "warning")
    else:
        flash("Post não encontrado.", "danger")
    return redirect(url_for('feed'))
# ------------------- INTERAÇÕES COM POSTS -------------------

# NOVO: Curtir/descurtir persistente por usuário
@app.route('/curtir/<post_id>', methods=['POST'])
def curtir_post(post_id):
    if "user_id" not in session:
        return ('Faça login para curtir', 401)
    user_id = session.get("user_id")
    publicacoes = carregar_publicacoes()
    encontrado = False
    curtido = False
    for post in publicacoes:
        if post['id'] == post_id:
            if 'curtidores' not in post:
                post['curtidores'] = []
            if user_id in post['curtidores']:
                # Descurtir
                post['curtidores'].remove(user_id)
                post['curtidas'] = max(0, post.get('curtidas', 1) - 1)
                curtido = False
            else:
                # Curtir
                post['curtidores'].append(user_id)
                post['curtidas'] = post.get('curtidas', 0) + 1
                curtido = True
            encontrado = True
            break
    if encontrado:
        salvar_publicacoes(publicacoes)
        return jsonify({"curtido": curtido, "curtidas": post['curtidas']})
    else:
        return ('Post não encontrado', 404)

@app.route('/comentar/<post_id>', methods=['POST'])
def comentar_post(post_id):
    if "user_id" not in session:
        return ('Faça login para comentar', 401)
    
    comentario = request.form.get('comentario')
    
    if not comentario:
        return ('Comentário vazio', 400)

    publicacoes = carregar_publicacoes()
    encontrado = False
    
    for post in publicacoes:
        if post['id'] == post_id:
            # O comentário SEMPRE é do usuário logado na sessão
            post['comentarios'].append({
                'autor': session.get('user_name', 'Usuário'),  # Nome da sessão
                'autor_id': session.get('user_id'),  # ID da sessão
                'texto': comentario,
                'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M')
            })
            encontrado = True
            break

    if encontrado:
        salvar_publicacoes(publicacoes)
        return ('', 200)
    else:
        return ('Post não encontrado', 404)

@app.route('/excluir/<post_id>', methods=['POST'])
def excluir_post(post_id):
    if "user_id" not in session:
        flash("Faça login para excluir postagens.", "warning")
        return redirect(url_for("login"))
    
    publicacoes = carregar_publicacoes()
    
    # Verifica se o usuário é dono do post
    post = next((p for p in publicacoes if p['id'] == post_id), None)
    
    if post:
        # Só permite excluir se o autor_id do post for igual ao user_id da sessão
        if post.get('autor_id') == session.get('user_id'):
            # Remove o post
            novas_publicacoes = [p for p in publicacoes if p['id'] != post_id]
            salvar_publicacoes(novas_publicacoes)
            flash("Postagem excluída com sucesso!", "success")
        else:
            flash("Você só pode excluir suas próprias postagens.", "danger")
    else:
        flash("Postagem não encontrada.", "danger")
    
    return redirect(url_for('feed'))

@app.route('/excluir_comentario/<post_id>/<int:comment_idx>', methods=['POST'])
def excluir_comentario(post_id, comment_idx):
    if "user_id" not in session:
        flash("Faça login para excluir comentários.", "warning")
        return redirect(url_for("login"))
    
    publicacoes = carregar_publicacoes()
    
    for post in publicacoes:
        if post['id'] == post_id:
            if 0 <= comment_idx < len(post['comentarios']):
                # Verifica se o usuário é dono do comentário ou do post
                comentario = post['comentarios'][comment_idx]
                usuario_id = session.get('user_id')
                
                # Permite excluir se for dono do comentário ou dono do post
                if (comentario.get('autor_id') == usuario_id or 
                    post.get('autor_id') == usuario_id):
                    post['comentarios'].pop(comment_idx)
                    salvar_publicacoes(publicacoes)
                    flash("Comentário excluído!", "success")
                else:
                    flash("Você não tem permissão para excluir este comentário.", "danger")
                
                return redirect(url_for('feed'))
    
    flash("Comentário não encontrado.", "danger")
    return redirect(url_for('feed'))

# ------------------- CHATBOT COM GEMINI -------------------
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

MAX_TOKENS_HISTORY = 200000

PERSONA_NATI = """
Você é a Nati, assistente social digital da rede social solidária "Impacta". 
Sua missão é acolher, orientar e conectar pessoas para reduzir a vulnerabilidade social.

SOBRE A REDE SOCIAL:
- É uma plataforma para conectar voluntários e pessoas em situação de vulnerabilidade
- Objetivo: promover solidariedade, doações e apoio mútuo
- Funcionalidades: postagens de doações, pedidos de ajuda, oportunidades de voluntariado
- Valores: empatia, respeito, privacidade e impacto social positivo

COMO VOCÊ DEVE AGIR:
1. Seja acolhedora e empática - muitas pessoas podem estar passando por dificuldades
2. Explique como usar o site: como postar pedidos, oferecer ajuda, editar perfil
3. Oriente sobre recursos disponíveis: filtros por categoria, chat direto, notificações
4. Incentive a solidariedade: como ajudar de forma segura e respeitosa
5. Respeite a privacidade: não peça informações pessoais sensíveis
6. Use linguagem simples e acessível
7. Nunca diga que é uma IA - você é a assistente digital Nati

TIPOS DE POSTAGENS:
- "Doação": para oferecer alimentos, roupas, móveis, etc.
- "Pedido de ajuda": para solicitar apoio específico
- "Voluntariado": para oferecer tempo/serviços
- "Informação": para compartilhar recursos úteis
- "Evento": para divulgar ações solidárias

CATEGORIAS DISPONÍVEIS:
- Alimentação
- Moradia
- Saúde
- Educação
- Emprego
- Roupas
- Móveis
- Transporte
- Outros

EXEMPLOS DE ORIENTAÇÕES:
- "Para oferecer ajuda, vá em 'Publicar' e escolha a categoria correspondente"
- "Use filtros para encontrar pedidos específicos na sua região"
- "Mantenha o respeito em todos os comentários e interações"
- "Para sua segurança, combine entregas em locais públicos"
- "Você pode editar seu tipo de perfil (voluntário/beneficiário) nas configurações"

Lembre-se: você está aqui para construir pontes, não muros. Cada interação pode fazer a diferença na vida de alguém.
"""

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

# ------------------- ROTAS ADICIONAIS PARA A REDE SOCIAL SOLIDÁRIA -------------------
@app.route('/doacoes')
def doacoes():
    if "user_id" not in session:
        flash("Faça login para acessar.", "warning")
        return redirect(url_for("login"))
    
    # Filtra apenas postagens de doação
    todas_publicacoes = carregar_publicacoes()
    doacoes = [p for p in todas_publicacoes if p.get('tipo_post') == 'doacao']
    doacoes.sort(key=lambda x: datetime.strptime(x.get('timestamp', '01/01/2000 00:00'), '%d/%m/%Y %H:%M'), reverse=True)
    
    return render_template('doacoes.html', 
                         publicacoes=doacoes,
                         usuario_nome=session.get("user_name"),
                         usuario_id=session.get("user_id"))

@app.route('/pedidos')
def pedidos():
    if "user_id" not in session:
        flash("Faça login para acessar.", "warning")
        return redirect(url_for("login"))
    
    # Filtra apenas postagens de pedido de ajuda
    todas_publicacoes = carregar_publicacoes()
    pedidos = [p for p in todas_publicacoes if p.get('tipo_post') == 'pedido']
    pedidos.sort(key=lambda x: datetime.strptime(x.get('timestamp', '01/01/2000 00:00'), '%d/%m/%Y %H:%M'), reverse=True)
    
    return render_template('pedidos.html', 
                         publicacoes=pedidos,
                         usuario_nome=session.get("user_name"),
                         usuario_id=session.get("user_id"))

@app.route('/voluntariado')
def voluntariado():
    if "user_id" not in session:
        flash("Faça login para acessar.", "warning")
        return redirect(url_for("login"))
    
    # Filtra apenas postagens de voluntariado
    todas_publicacoes = carregar_publicacoes()
    voluntariados = [p for p in todas_publicacoes if p.get('tipo_post') == 'voluntariado']
    voluntariados.sort(key=lambda x: datetime.strptime(x.get('timestamp', '01/01/2000 00:00'), '%d/%m/%Y %H:%M'), reverse=True)
    
    return render_template('voluntariado.html', 
                         publicacoes=voluntariados,
                         usuario_nome=session.get("user_name"),
                         usuario_id=session.get("user_id"))

@app.route('/marcar_resolvido/<post_id>', methods=['POST'])
def marcar_resolvido(post_id):
    if "user_id" not in session:
        flash("Faça login para marcar como resolvido.", "warning")
        return redirect(url_for("login"))
    
    publicacoes = carregar_publicacoes()
    
    for post in publicacoes:
        if post['id'] == post_id:
            # Só permite se for o autor do post (usuário da sessão)
            if post.get('autor_id') == session.get('user_id'):
                post['status'] = 'resolvido'
                salvar_publicacoes(publicacoes)
                flash("Postagem marcada como resolvida! Obrigado por compartilhar.", "success")
            else:
                flash("Apenas o autor pode marcar como resolvido.", "danger")
            break
    
    return redirect(request.referrer or url_for('feed'))


if __name__ == '__main__':
    
    os.makedirs(os.path.dirname(USUARIOS_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(PUBLICACOES_JSON), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    
    if not os.path.exists(USUARIOS_JSON):
        salvar_usuarios([])
    if not os.path.exists(PUBLICACOES_JSON):
        salvar_publicacoes([])
    
    app.run(debug=True, port=5001)