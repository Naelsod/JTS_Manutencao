# app.py (Versão 7 - Com Lixeira)

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps 
from bson.objectid import ObjectId # Import já estava ok!
import os # Para lidar com pastas e arquivos
from werkzeug.utils import secure_filename # Para limpar nomes de arquivos

# ... (seus outros imports, like Flask, MongoClient, etc.)
from bson.objectid import ObjectId
# --- FUNÇÃO DO NOSSO "SEGURANÇA VIP" ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash("Você precisa fazer login para acessar essa página.", "error")
            return redirect(url_for('pagina_login'))
        if session.get('permissao') != 'Admin':
            flash("Você não tem permissão para acessar esta página. Acesso restrito a Admins.", "error")
            return redirect(url_for('pagina_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Checa se o usuário NÃO ESTÁ logado
        if 'email' not in session:
            flash("Você precisa fazer login para acessar essa página.", "error")
            return redirect(url_for('pagina_login'))
        
        # 2. Se está logado, DEIXA ELE PASSAR
        return f(*args, **kwargs)
    return decorated_function

# --- 1. Criando o "Aplicativo" Flask ---
app = Flask(__name__)
app.secret_key = 'minha_chave_secreta_jts_12345'

# --- CONFIGURAÇÃO DE UPLOAD ---
# 1. Define a pasta onde as imagens serão salvas
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
# 2. Cria a pasta 'uploads' se ela não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# 3. Coloca a configuração no app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ------------------------------

# --- 2. Conectando ao Banco de Dados ---
def conectar_banco():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ Conexão com o MongoDB estabelecida.")
        db = client['JTS_MANUTENCAO']
        return db
    except ConnectionFailure:
        print("❌ Erro: Não foi possível conectar ao MongoDB.")
        return None

db = conectar_banco()
if db is None: exit()


# --- 3. FUNÇÕES DE LÓGICA (com upgrade na senha!) ---

def adicionar_usuario(db, nome, email, senha, permissao):
    collection = db['usuarios']
    if collection.find_one({"email": email}):
        print(f"⚠️  Aviso: Usuário com o email '{email}' já existe.")
        return
    senha_hash = generate_password_hash(senha)
    novo_usuario = {
        "nome": nome, "email": email, "senha_hash": senha_hash,
        "permissao": permissao, "ultimo_login": None
    }
    collection.insert_one(novo_usuario)
    print(f"👤 Usuário '{nome}' adicionado com sucesso!")

def listar_usuarios(db):
    collection = db['usuarios']
    return list(collection.find({}, {'senha_hash': 0}))


def adicionar_nova_maquina(db, codigo, tipo, especificacoes=None, imagem_url=None):
    collection = db['maquinas']
    
    # 1. Verifica se o código já existe
    if collection.find_one({"codigo": codigo}):
        flash(f"Erro: Máquina com o código '{codigo}' já existe.", "error")
        return False
        
    # 2. Monta o novo documento da máquina
    nova_maquina = {
        "codigo": codigo,
        "tipo_maquina": tipo,
        "especificacoes": especificacoes,
        "imagem_url": imagem_url,
        "status": "Disponível", # Começa como 'Disponível' por padrão
        "manutencoes": [], # Começa com histórico vazio
        "data_cadastro": datetime.now()
    }
    
    # 3. Salva no banco
    collection.insert_one(nova_maquina)
    flash(f"Máquina '{codigo}' cadastrada com sucesso!", "success")
    adicionar_log(db, session.get('nome', 'Sistema'), f"Cadastrou a nova máquina: {codigo}")
    return True


def deletar_maquina(db, maquina_id_a_deletar):
    collection = db['maquinas']
    
    try:
        # 1. Acha a máquina ANTES de deletar, para pegar o nome da imagem
        maquina = collection.find_one({"_id": ObjectId(maquina_id_a_deletar)})
        
        if not maquina:
            flash("Erro: Máquina não encontrada.", "error")
            return False

        # 2. Deleta a imagem da pasta 'static/uploads' (se ela tiver uma)
        if maquina.get('imagem_url'):
            try:
                # O 'imagem_url' é salvo como '/static/uploads/nome.jpg'
                # 'os.path.basename' pega só o 'nome.jpg'
                nome_arquivo = os.path.basename(maquina['imagem_url'])
                # Monta o caminho completo (C:/.../static/uploads/nome.jpg)
                caminho_do_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
                
                if os.path.exists(caminho_do_arquivo):
                    os.remove(caminho_do_arquivo)
                    print(f"Imagem {nome_arquivo} deletada do servidor.")
                
            except Exception as e:
                print(f"Aviso: Falha ao deletar imagem {maquina['imagem_url']}. Erro: {e}")

        # 3. Deleta a máquina do banco de dados
        query = {"_id": ObjectId(maquina_id_a_deletar)}
        resultado = collection.delete_one(query)
        
        if resultado.deleted_count > 0:
            flash(f"Máquina '{maquina['codigo']}' deletada com sucesso!", "success")
            adicionar_log(db, session.get('nome', 'Sistema'), f"Deletou a máquina: {maquina['codigo']}")
            return True
        else:
            flash("Erro: Máquina não encontrada no banco.", "error")
            return False
            
    except Exception as e:
        flash(f"Erro ao deletar máquina: {e}", "error")
        return False

# app.py (Seção 3 - Funções de Lógica)

def salvar_manutencao(db, maquina_id, novo_status, log_data, log_tipo, log_descricao):
    collection = db['maquinas']
    
    try:
        query = {"_id": ObjectId(maquina_id)}
        
        # Monta o novo "log" que será salvo
        novo_log_manutencao = {
            "log_id": ObjectId(), # Cria um ID único para este log (útil para deletar depois)
            "data": log_data,
            "tipo": log_tipo,
            "descricao": log_descricao,
            "registrado_por": session.get('nome', 'Sistema') # Pega o nome do usuário logado
        }
        
        # O "super-comando" do MongoDB:
        # 1. $set: Atualiza o campo 'status' principal da máquina
        # 2. $push: "Empurra" o novo log para dentro da lista 'manutencoes'
        update_data = {
            "$set": { "status": novo_status },
            "$push": { "manutencoes": novo_log_manutencao }
        }
        
        resultado = collection.update_one(query, update_data)
        
        if resultado.modified_count > 0:
            flash("Manutenção registrada e status atualizado com sucesso!", "success")
            adicionar_log(db, session.get('nome'), f"Registrou manutenção na máquina (ID: {maquina_id})")
        else:
            flash("Nenhuma alteração foi salva.", "info")
            
    except Exception as e:
        flash(f"Erro ao salvar manutenção: {e}", "error")




def adicionar_log(db, usuario_nome, acao):
    try:
        collection = db['logs']
        novo_log = {
            "timestamp": datetime.now(),
            "usuario": usuario_nome,
            "acao": acao
        }
        collection.insert_one(novo_log)
    except Exception as e:
        print(f"AVISO: Falha ao salvar log: {e}")

def listar_logs(db):
    try:
        collection = db['logs']
        # *** A MUDANÇA ESTÁ AQUI! ***
        # Trocamos 50 por 5
        return list(collection.find({}).sort("timestamp", -1).limit(5)) 
    except Exception as e:
        print(f"AVISO: Falha ao buscar logs: {e}")
        return []


# app.py (Seção 3 - Funções de Lógica)

def listar_maquinas(db, busca_codigo=None, busca_tipo=None):
    collection = db['maquinas']
    print(f"Buscando máquinas com código='{busca_codigo}' e tipo='{busca_tipo}'")
    
    # 1. Começa com a lista de condições
    query_parts = []
    
    # 2. Se o usuário digitou um CÓDIGO na busca...
    if busca_codigo:
        query_parts.append({
            "codigo": { "$regex": busca_codigo, "$options": "i" } 
        })
    
    # 3. Se o usuário selecionou um TIPO no filtro...
    if busca_tipo:
        query_parts.append({
            "tipo_maquina": busca_tipo
        })
    
    # 4. Monta a query final
    if not query_parts:
        query = {} # Se não filtrou nada, busca tudo
    else:
        # "$and" -> tem que bater com TODAS as condições
        query = { "$and": query_parts }
        
    print(f"Query final do MongoDB: {query}")
    return list(collection.find(query).sort("data_cadastro", -1))

def get_maquina_by_id(db, maquina_id):
    try:
        maquina = db.maquinas.find_one({"_id": ObjectId(maquina_id)})
        return maquina
    except Exception as e:
        print(f"Erro ao buscar máquina por ID: {e}")
        return None


def listar_itens_estoque(db, busca=None, tipos=None):
    collection = db['itensEstoque']
    print(f"Buscando com busca='{busca}' e tipos='{tipos}'")
    
    # 1. Criamos uma lista de "condições"
    query_parts = []
    
    # 2. Se o usuário digitou algo na busca, adiciona a condição de busca
    if busca:
        query_parts.append({
            "$or": [
                { "nome_item": { "$regex": busca, "$options": "i" } },
                { "codigo_item": { "$regex": busca, "$options": "i" } },
                { "marca": { "$regex": busca, "$options": "i" } }
            ]
        })
    
    # 3. Se o usuário marcou algum checkbox de tipo...
    if tipos: # 'tipos' será uma lista, ex: ['peca', 'filtro']
        # Adiciona a condição de "tipo"
        # "$in" significa: "o campo 'tipo' tem que ser UM DESSES da lista"
        query_parts.append({
            "tipo": { "$in": tipos }
        })
    
    # 4. Montamos a query final
    if not query_parts:
        query = {} # Se não filtrou nada, busca tudo
    else:
        # "$and" significa: "o item tem que bater com TODAS as condições"
        query = { "$and": query_parts }
        
    print(f"Query final do MongoDB: {query}")
    return list(collection.find(query))
    
def deletar_item_estoque(db, item_id_a_deletar):
    try:
        collection = db['itensEstoque']
        # Converte o ID de string (que vem da URL) para ObjectId do Mongo
        query = {"_id": ObjectId(item_id_a_deletar)}
        
        resultado = collection.delete_one(query)
        
        if resultado.deleted_count > 0:
            flash("Item deletado do estoque com sucesso!", "success")
            return True
        else:
            flash("Erro: Item não encontrado no banco.", "error")
            return False
    except Exception as e:
        flash(f"Erro ao deletar o item: {e}", "error")
        return False

def adicionar_item_estoque(db, codigo_item, nome_item, quantidade, localizacao, tipo=None, marca=None, maquina_compativel=None, descricao=None):
    collection = db['itensEstoque']
    if collection.find_one({"codigo_item": codigo_item}):
        print(f"⚠️  Aviso: Item com o código '{codigo_item}' já existe no estoque.")
        flash(f"⚠️  Aviso: Item com o código '{codigo_item}' já existe no estoque.", "error")
        return # Para a execução se o item já existir

    novo_item = {
        "codigo_item": codigo_item,
        "nome_item": nome_item,
        "quantidade": quantidade,
        "localizacao": localizacao,
        "tipo": tipo, # <-- NOVO
        "marca": marca, # <-- NOVO
        "maquina_compativel": maquina_compativel, # <-- NOVO
        "descricao": descricao, # <-- NOVO
        "data_cadastro": datetime.now()
    }
    collection.insert_one(novo_item)
    print(f"📦 Item de estoque '{nome_item}' adicionado com sucesso!")
    flash(f"📦 Item de estoque '{nome_item}' adicionado com sucesso!", "success")

def get_item_by_id(db, item_id):
    try:
        # Busca um único item pelo seu ID (convertido de string para ObjectId)
        item = db.itensEstoque.find_one({"_id": ObjectId(item_id)})
        return item
    except Exception as e:
        print(f"Erro ao buscar item por ID: {e}")
        return None

def update_item_estoque(db, item_id, dados_novos):
    try:
        collection = db.itensEstoque
        # Converte o ID
        query = {"_id": ObjectId(item_id)}
        # Prepara os dados para atualizar. O "$set" atualiza só o que foi passado.
        update_data = {"$set": dados_novos}
        
        resultado = collection.update_one(query, update_data)
        
        if resultado.modified_count > 0:
            flash("Item atualizado com sucesso!", "success")
            return True
        else:
            # Isso acontece se o usuário "Salvar" sem mudar nada. Não é um erro.
            flash("Nenhuma alteração foi feita.", "info")
            return True
    except Exception as e:
        flash(f"Erro ao atualizar o item: {e}", "error")
        return False











# <-- MUDANÇA AQUI (1/4): Adicionamos a função de lógica DELETAR ---
def deletar_usuario(db, user_id_a_deletar):
    # Regra de segurança: não deixar o admin se deletar
    if user_id_a_deletar == session.get('user_id'):
        flash("Erro: Você não pode deletar sua própria conta enquanto está logado.", "error")
        return False
        
    try:
        collection = db['usuarios']
        query = {"_id": ObjectId(user_id_a_deletar)} # Converte a string em ObjectId
        resultado = collection.delete_one(query)
        
        if resultado.deleted_count > 0:
            flash("Usuário deletado com sucesso!", "success")
            return True
        else:
            flash("Erro: Usuário não encontrado.", "error")
            return False
    except Exception as e:
        flash(f"Erro ao deletar: {e}", "error")
        return False

# --- 4. AS ROTAS DO SITE (com a lógica de login) ---

@app.route('/')
def pagina_login():
    return render_template('login.html')

# app.py (Seção 4 - Rotas)

# app.py (Seção 4 - Rotas)

@app.route('/dashboard')
@login_required
def pagina_dashboard():
    # 1. Proteção (já estava certa)
    if 'email' not in session:
        flash("Você precisa fazer login para acessar essa página.", "error")
        return redirect(url_for('pagina_login'))

    print("Servindo a página do Dashboard com dados reais...")

    # 2. Lógica dos STATS (você já tem isso)
    all_maquinas = listar_maquinas(db) 
    
    # 3. Prepara os contadores (você já tem isso)
    stats = {
        "disponivel": 0,
        "manutencao": 0,
        "indisponivel": 0,
        "total": len(all_maquinas)
    }
    
    # 4. Loop para contar os status (você já tem isso)
    for maquina in all_maquinas:
        status_da_maquina = maquina.get('status') 
        
        if status_da_maquina == 'Disponível':
            stats['disponivel'] += 1
        elif status_da_maquina == 'Em Manutenção':
            stats['manutencao'] += 1
        elif status_da_maquina == 'Indisponível':
            stats['indisponivel'] += 1
            
    # 5. Lógica dos LOGS (você já tem isso)
    ultimos_logs = listar_logs(db)
    
    # --- MÁGICA NOVA: CÁLCULO DAS PORCENTAGENS ---
    # (Adicione este bloco novo)
    percentages = {
        "disponivel": 0,
        "manutencao": 0,
        "indisponivel": 0
    }
    
    # Evita o erro de divisão por zero se não houver máquinas
    if stats["total"] > 0: 
        # round(..., 1) -> Arredonda para 1 casa decimal
        percentages["disponivel"] = round((stats["disponivel"] / stats["total"]) * 100, 1)
        percentages["manutencao"] = round((stats["manutencao"] / stats["total"]) * 100, 1)
        percentages["indisponivel"] = round((stats["indisponivel"] / stats["total"]) * 100, 1)
    # --- FIM DA MÁGICA NOVA ---
    
    # --- MUDANÇA FINAL: "Turbine" esta linha ---
    # 6. Envia TUDO (stats, logs E percentages) para o HTML
    return render_template(
        'dashboard.html', 
        stats=stats, 
        ultimos_logs=ultimos_logs, 
        percentages=percentages # <-- Adiciona a variável nova aqui
    )

# --- ROTA PARA MOSTRAR A PÁGINA 'gerenciar.html' ---
@app.route('/gerenciar')
@admin_required
def pagina_gerenciar():
    print("Servindo a página de gerenciamento (ADMIN)...")
    lista_de_usuarios = listar_usuarios(db)
    return render_template('gerenciar.html', usuarios=lista_de_usuarios)


# app.py (Seção 4 - Rotas)

# MUDAMOS A ROTA para ela aceitar um ID!
@app.route('/manutencao/<maquina_id>')
@login_required
def pagina_manutencao(maquina_id):
    print(f"Servindo a página de manutenção para a máquina ID: {maquina_id}")
    
    # Precisamos de uma função que busca UMA máquina (vamos criar!)
    maquina = get_maquina_by_id(db, maquina_id)
    
    if maquina is None:
        flash("Máquina não encontrada.", "error")
        return redirect(url_for('pagina_maquinas'))

    # O próximo passo (que faremos DEPOIS) é:
    # 1. Pegar o histórico de manutenções
    # 2. Criar o form para mudar o status
    
    # Por enquanto, só passamos os dados da máquina para o HTML
    return render_template('manutencao.html', maquina=maquina)

@app.route('/processar_adicionar_maquina', methods=['POST'])
@login_required # Só usuários logados podem cadastrar
def rota_processar_adicionar_maquina():
    try:
        # 1. Pega os dados do formulário (dos atributos 'name')
        tipo = request.form.get('tipo_maquina')
        codigo = request.form.get('codigo_maquina')
        especificacoes = request.form.get('especificacoes')
        
        imagem_url_para_db = None # Começa como nulo
        
        # 2. Lógica de Upload da Imagem
        if 'imagem_maquina' in request.files:
            file = request.files['imagem_maquina']
            
            # Se o usuário enviou um arquivo
            if file and file.filename != '':
                # Limpa o nome do arquivo (ex: "espaço 1.jpg" -> "espaco_1.jpg")
                filename = secure_filename(file.filename)
                # Cria o caminho completo (ex: .../static/uploads/espaco_1.jpg)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # Salva o arquivo na pasta
                file.save(save_path)
                # Salva no banco o CAMINHO DE URL (para o <img> no HTML)
                imagem_url_para_db = f"/static/uploads/{filename}"

        # 3. Chama a função de lógica para salvar no banco
        adicionar_nova_maquina(db, codigo, tipo, especificacoes, imagem_url_para_db)

    except Exception as e:
        flash(f"Erro ao cadastrar máquina: {e}", "error")
        # Se der erro, devolve o usuário para a página de adicionar
        return redirect(url_for('pagina_adicionar_maquina'))
    
    # 4. Se deu tudo certo, manda o usuário para a lista de máquinas
    return redirect(url_for('pagina_maquinas'))

# app.py (Seção 4 - Rotas)

# --- ROTA PARA PROCESSAR O FORMULÁRIO DE MANUTENÇÃO (POST) ---
@app.route('/processar_manutencao/<maquina_id>', methods=['POST'])
@login_required
def rota_processar_manutencao(maquina_id):
    try:
        # 1. Pega os dados do formulário
        novo_status = request.form.get('status')
        log_data = request.form.get('data_manutencao')
        log_tipo = request.form.get('tipo_manutencao')
        log_descricao = request.form.get('descricao_manutencao')
        
        # 2. Chama a lógica para salvar
        salvar_manutencao(db, maquina_id, novo_status, log_data, log_tipo, log_descricao)

    except Exception as e:
        flash(f"Erro ao processar o formulário: {e}", "error")
    
    # 3. Devolve o usuário PARA A MESMA PÁGINA, que agora estará atualizada
    return redirect(url_for('pagina_manutencao', maquina_id=maquina_id))



# --- ROTA DE LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('nome', None)
    session.pop('permissao', None) # <-- MUDANÇA AQUI (2/4): Esquecer o ID no logout
    session.pop('user_id', None) 
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for('pagina_login'))

# --- A ROTA MÁGICA QUE RECEBE OS DADOS DO LOGIN ---
@app.route('/login_processar', methods=['POST'])
def processar_login():
    email_do_form = request.form['email']
    senha_do_form = request.form['password']
    
    usuarios_collection = db['usuarios']
    usuario_encontrado = usuarios_collection.find_one({"email": email_do_form})
    
    if usuario_encontrado:
        if check_password_hash(usuario_encontrado['senha_hash'], senha_do_form):
            session['email'] = usuario_encontrado['email']
            session['nome'] = usuario_encontrado['nome']
            session['permissao'] = usuario_encontrado['permissao']
            # <-- MUDANÇA AQUI (3/4): Lembrar do ID no login
            session['user_id'] = str(usuario_encontrado['_id']) 
            
            usuarios_collection.update_one(
                {"email": email_do_form}, 
                {"$set": {"ultimo_login": datetime.now()}}
            )
            return redirect(url_for('pagina_dashboard'))
        else:
            flash("Senha incorreta. Tente novamente.", "error")
            return redirect(url_for('pagina_login'))
    else:
        flash("Usuário não encontrado. Verifique o email.", "error")
        return redirect(url_for('pagina_login'))
    

# --- ROTA PARA PROCESSAR O CADASTRO (RECEBER O FORM) ---
@app.route('/processar_gerenciamento', methods=['POST'])
@admin_required
def processar_gerenciamento():
    print("Recebendo dados para cadastrar novo usuário...")
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['password']
    permissao = request.form['permissao']
    
    adicionar_usuario(db, nome, email, senha, permissao)
    
    flash(f"Usuário '{nome}' cadastrado com sucesso!", "success")
    return redirect(url_for('pagina_gerenciar'))

# <-- MUDANÇA AQUI (4/4): Adicionamos a ROTA DE DELETAR ---
@app.route('/deletar_usuario/<user_id>')
@admin_required
def rota_deletar_usuario(user_id):
    deletar_usuario(db, user_id)
    return redirect(url_for('pagina_gerenciar'))


# app.py

# --- ROTA PARA LISTAR O ESTOQUE (pagina 'estoque.html') ---
@app.route('/estoque')
@login_required
def pagina_estoque():
    print("Servindo a página de listagem de estoque...")
    
    # 1. Lemos o termo da busca (igual antes)
    termo_de_busca = request.args.get('busca')
    
    # 2. Lemos a LISTA de checkboxes 'tipo'
    tipos_filtrados = request.args.getlist('tipo')
    print(f"Filtros de tipo recebidos: {tipos_filtrados}")
    
    # 3. Passamos os DOIS filtros para a função de lógica
    lista_itens = listar_itens_estoque(db, busca=termo_de_busca, tipos=tipos_filtrados) 
    
    # 4. Passamos os filtros de volta para o HTML (para "grudar")
    return render_template('estoque.html', 
                           itens=lista_itens, 
                           busca_atual=termo_de_busca, 
                           tipos_atuais=tipos_filtrados)


@app.route('/deletar_item_estoque/<item_id>')
@login_required # Só usuários logados podem deletar
def rota_deletar_item_estoque(item_id):
    deletar_item_estoque(db, item_id)
    # Devolve o usuário para a lista de estoque atualizada
    return redirect(url_for('pagina_estoque'))

@app.route('/editar_item_estoque/<item_id>')
@login_required
def pagina_editar_item_estoque(item_id):
    # 1. Busca os dados atuais do item no banco
    item_para_editar = get_item_by_id(db, item_id)
    
    if item_para_editar is None:
        flash("Erro: Item não encontrado.", "error")
        return redirect(url_for('pagina_estoque'))
        
    # 2. Renderiza a página 'editar_item.html' e "injeta" os dados nele
    return render_template('editar_item.html', item=item_para_editar)


# --- ROTA PARA PROCESSAR A EDIÇÃO (POST) ---
@app.route('/processar_edicao_item/<item_id>', methods=['POST'])
@login_required
def rota_processar_edicao(item_id):
    try:
        # 1. Pega TODOS os dados que vieram do formulário
        dados_para_atualizar = {
            "codigo_item": request.form['codigo_item'],
            "nome_item": request.form['nome_item'],
            "quantidade": int(request.form.get('quantidade', 0)),
            "localizacao": request.form.get('localizacao'),
            "tipo": request.form.get('tipo'),
            "marca": request.form.get('marca'),
            "maquina_compativel": request.form.get('maquina_compativel'),
            "descricao": request.form.get('descricao')
            # (Adicione qualquer outro campo que seu form tenha)
        }
        
        # 2. Chama a função de lógica para atualizar
        update_item_estoque(db, item_id, dados_para_atualizar)
        
    except Exception as e:
        flash(f"Erro ao processar edição: {e}", "error")
    
    # 3. Devolve o usuário para a lista de estoque
    return redirect(url_for('pagina_estoque'))





# --- ROTA PARA MOSTRAR O FORM DE ADICIONAR ('adc.html') ---
@app.route('/adicionar_item_estoque')
def pagina_adicionar_item_estoque():
    print("Servindo a página de adicionar item...")
    return render_template('adc.html')


# --- ROTA PARA RECEBER OS DADOS DO FORM ('adc.html') ---
@app.route('/processar_item_estoque', methods=['POST'])
@login_required
def processar_item_estoque():
    print("Recebendo dados de um novo item de estoque...")
    try:
        # 1. Pegar os dados do formulário (os que já tínhamos)
        codigo = request.form['codigo_item']
        nome = request.form['nome_item']
        quantidade = int(request.form.get('quantidade', 0)) 
        localizacao = request.form['localizacao']
        
        # 2. Pegar os DADOS NOVOS do formulário
        # Usamos .get() para ser seguro caso o campo venha vazio
        tipo = request.form.get('tipo')
        marca = request.form.get('marca')
        maquina_compativel = request.form.get('maquina_compativel')
        descricao = request.form.get('descricao')

        # 3. Chamar nossa função PRONTA e ATUALIZADA!
        adicionar_item_estoque(db, codigo, nome, quantidade, localizacao, 
                             tipo, marca, maquina_compativel, descricao)
    
    except Exception as e:
        print(f"Erro ao adicionar item: {e}")
        flash(f"Erro ao adicionar item: {e}", "error")

    # 4. Mandar o usuário de volta para a LISTA de estoque
    return redirect(url_for('pagina_estoque'))


# app.py (Seção 4 - Rotas)

@app.route('/maquinas')
@login_required
def pagina_maquinas():
    print("Servindo a página de listagem de máquinas...")
    
    # 1. Lê os filtros que vieram da URL (do formulário GET)
    busca_codigo = request.args.get('busca_codigo')
    busca_tipo = request.args.get('busca_tipo')
    
    # 2. Passa os filtros para a função de lógica
    lista_de_maquinas = listar_maquinas(db, busca_codigo=busca_codigo, busca_tipo=busca_tipo)
    
    # 3. Envia a lista FILTRADA e os filtros "grudentos" para o HTML
    return render_template('maquinas_geren.html', 
                           maquinas=lista_de_maquinas,
                           busca_codigo_atual=busca_codigo,
                           busca_tipo_atual=busca_tipo)

# --- ROTA VAZIA PARA 'add_maquina.html' (só para o link funcionar) ---
@app.route('/adicionar_maquina')
@login_required
def pagina_adicionar_maquina():
    # Vamos usar o 'add_maquina.html' que você tem
    return render_template('add_maquina.html')

@app.route('/deletar_maquina/<maquina_id>')
@login_required # <-- Vamos deixar @login_required (ou @admin_required se preferir)
def rota_deletar_maquina(maquina_id):
    deletar_maquina(db, maquina_id)
    # Devolve o usuário para a lista de máquinas
    return redirect(url_for('pagina_maquinas'))


# --- 5. O COMANDO PARA LIGAR O SERVIDOR ---
if __name__ == "__main__":
    print("Iniciando o servidor web...")
    app.run(debug=True, port=5000)