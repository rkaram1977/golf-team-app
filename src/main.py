import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
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

# Configuração do banco de dados - ALTERADO PARA SQLITE
# Construir o caminho absoluto para o arquivo do banco de dados
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'golf_app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
# Remover a linha original do MySQL:
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    print(f"Iniciando criação do banco de dados em: {db_path}")
    db.create_all() # Cria as tabelas no banco de dados SQLite se não existirem
    print("Criação do banco de dados concluída.")

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

if __name__ == '__main__':
    # Garante que o diretório pai do db exista, se necessário (SQLite cria o arquivo, mas não o diretório)
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    app.run(host='0.0.0.0', port=5000, debug=True)

