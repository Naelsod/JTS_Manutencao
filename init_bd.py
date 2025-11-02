# init_db.py
# Este script serve APENAS para criar as coleções e o usuário admin inicial.

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# --- 1. CONECTA AO BANCO ---
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info() # Força a conexão
    print("✅ Conexão com o MongoDB estabelecida.")
    
    # Seleciona o seu banco de dados
    db = client['JTS_MANUTENCAO']

except Exception as e:
    print(f"❌ Erro ao conectar ao MongoDB: {e}")
    exit() # Para o script se não conseguir conectar

# --- 2. LISTA DE COLEÇÕES ("tabelas") QUE QUEREMOS CRIAR ---
colecoes_para_criar = [
    "usuarios",
    "maquinas",
    "itensEstoque",
    "logs"
]

# --- 3. CRIA AS COLEÇÕES (se elas não existirem) ---
print("\nVerificando coleções...")
lista_de_colecoes_existentes = db.list_collection_names()

for colecao in colecoes_para_criar:
    if colecao not in lista_de_colecoes_existentes:
        try:
            db.create_collection(colecao)
            print(f"  - Coleção '{colecao}' foi criada com sucesso!")
        except Exception as e:
            print(f"  - ❌ Erro ao criar coleção '{colecao}': {e}")
    else:
        print(f"  - Coleção '{colecao}' já existe. (Pulando)")

# --- 4. CRIA O USUÁRIO ADMIN (se ele não existir) ---
print("\nVerificando usuário Admin...")
collection_usuarios = db['usuarios']

# Procura se o admin já existe
if collection_usuarios.find_one({"email": "admin@jts.com"}):
    print("  - Usuário 'admin@jts.com' já existe. (Pulando)")
else:
    # Se não existe, cria ele
    senha_hash = generate_password_hash("senhaForte123")
    novo_admin = {
        "nome": "Admin JTS",
        "email": "admin@jts.com",
        "senha_hash": senha_hash,
        "permissao": "Admin",
        "ultimo_login": None
    }
    collection_usuarios.insert_one(novo_admin)
    print("  - 👤 Usuário 'admin@jts.com' foi criado com sucesso!")

print("\n✅ Banco de dados 'JTS_MANUTENCAO' está pronto para ser usado!")
client.close()