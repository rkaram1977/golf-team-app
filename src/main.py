import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from werkzeug.exceptions import HTTPException # Importar HTTPException
# Importar o db e o modelo Player do local correto
from src.models.player import db, Player
# Importar os blueprints
from src.routes.player_routes import player_bp
from src.routes.team_routes import team_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'uma_chave_secreta_forte_aqui'

# Registrar os blueprints
app.register_blueprint(player_bp, url_prefix='/api')
app.register_blueprint(team_bp, url_prefix='/api')

# Configuração do banco de dados - ALTERADO PARA POSTGRESQL
# Ler a URL do banco de dados da variável de ambiente fornecida pelo Render
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("AVISO: Variável de ambiente DATABASE_URL não definida. Verifique a configuração do serviço no Render.")
    raise ValueError("DATABASE_URL não está configurada no ambiente.")

# Corrigir URL do Render se começar com postgres:// (SQLAlchemy prefere postgresql://)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    print(f"Conectando ao banco de dados PostgreSQL...")
    try:
        # Teste de conexão explícito
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        print("Conexão com o banco de dados PostgreSQL estabelecida com sucesso.")
        db.create_all() # Cria as tabelas no banco de dados PostgreSQL se não existirem
        print("Estrutura do banco de dados verificada/criada com sucesso no PostgreSQL.")
    except Exception as e:
        print(f"ERRO FATAL ao conectar ou criar tabelas no PostgreSQL: {e}")
        # Levantar o erro para que o deploy falhe e o problema seja visível
        raise e

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # Se index.html não existir, retornamos uma mensagem informativa da API
            return jsonify({
                "status": "API ativa",
                "mensagem": "Bem-vindo ao Golf Team App!",
                "endpoints": {
                    "Jogadores": {
                        "GET /api/players": "Listar todos os jogadores",
                        "POST /api/players": "Adicionar novo jogador",
                        "GET /api/players/<id>": "Obter jogador específico",
                        "PUT /api/players/<id>": "Atualizar jogador",
                        "DELETE /api/players/<id>": "Excluir jogador"
                    },
                    "Times": {
                        "POST /api/teams/generate": "Gerar times equilibrados (requer player_ids)",
                        "POST /api/teams/record_win": "Registrar vitória para jogadores"
                    }
                }
            }), 200

# Tratador de erro global para garantir respostas JSON
@app.errorhandler(Exception)
def handle_exception(e):
    # Passa por exceções HTTP padrão
    if isinstance(e, HTTPException):
        # Para erros HTTP como 404, 400, etc., retorna a resposta JSON padrão do Flask/Werkzeug se disponível
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response

    # Para exceções não-HTTP (erros 500 internos)
    # Logar o erro completo no servidor para depuração
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    
    # Retornar uma resposta JSON genérica de erro 500
    return jsonify({
        "message": "Erro interno do servidor. Por favor, tente novamente mais tarde.",
        "error_type": str(type(e).__name__) # Opcional: pode ajudar na depuração
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) # Desativar debug em produção/teste final


