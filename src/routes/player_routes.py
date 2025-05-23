import os
from flask import Blueprint, request, jsonify, send_file
from src.models.player import db, Player
import tempfile
from jinja2 import Template
from sqlalchemy import update

player_bp = Blueprint("player_bp", __name__)

# Helper function to format player data for response
def format_player(player):
    return {
        "id": player.id,
        "name": player.name,
        "handicap": player.handicap,
        "score": player.score,
        "games_played": player.games_played
    }

@player_bp.route("/players", methods=["POST"])
def add_player():
    data = request.get_json()
    if not data or not "name" in data or not "handicap" in data:
        return jsonify({"message": "Nome e handicap são obrigatórios"}), 400
    
    name = data["name"]
    handicap = data["handicap"]

    # Validação básica do handicap
    if not isinstance(handicap, int) or not (0 <= handicap <= 36):
        return jsonify({"message": "Handicap inválido. Deve ser um número inteiro entre 0 e 36."}), 400

    # Verificar se jogador já existe
    if Player.query.filter_by(name=name).first():
        return jsonify({"message": "Jogador com este nome já existe"}), 409

    # games_played defaults to 0 in the model
    new_player = Player(name=name, handicap=handicap)
    
    try:
        db.session.add(new_player)
        db.session.commit()
        return jsonify({"message": "Jogador adicionado com sucesso!", "player": format_player(new_player)}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar jogador: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao adicionar jogador."}), 500

@player_bp.route("/players", methods=["GET"])
def get_players():
    try:
        players = Player.query.all()
        # Usar a função helper para formatar cada jogador
        players_list = [format_player(player) for player in players]
        return jsonify(players_list), 200
    except Exception as e:
        print(f"Erro ao buscar jogadores: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao buscar jogadores."}), 500

@player_bp.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        # Usar a função helper para formatar
        return jsonify(format_player(player)), 200
    except Exception as e:
        # get_or_404 já lida com não encontrado, isso é para outros erros
        print(f"Erro ao buscar jogador {player_id}: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao buscar jogador."}), 500

@player_bp.route("/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    player = Player.query.get_or_404(player_id)
    data = request.get_json()
    if not data:
        return jsonify({"message": "Nenhum dado fornecido para atualização"}), 400

    updated = False
    # Atualizar campos se fornecidos
    if "name" in data:
        # Verificar se o novo nome já existe (e não é o nome atual do jogador)
        existing_player = Player.query.filter(Player.name == data["name"], Player.id != player_id).first()
        if existing_player:
            return jsonify({"message": "Outro jogador com este nome já existe"}), 409
        player.name = data["name"]
        updated = True
        
    if "handicap" in data:
        handicap = data["handicap"]
        if not isinstance(handicap, int) or not (0 <= handicap <= 36):
            return jsonify({"message": "Handicap inválido. Deve ser um número inteiro entre 0 e 36."}), 400
        player.handicap = handicap
        updated = True

    if "score" in data:
        score = data["score"]
        if not isinstance(score, int) or score < 0:
             return jsonify({"message": "Pontuação inválida. Deve ser um número inteiro não negativo."}), 400
        player.score = score
        updated = True
        
    # Permitir atualização de games_played via API? Por enquanto não, é atualizado na geração de times.
    # if "games_played" in data:
    #     games = data["games_played"]
    #     if not isinstance(games, int) or games < 0:
    #          return jsonify({"message": "Número de jogos inválido."}), 400
    #     player.games_played = games
    #     updated = True

    if not updated:
         return jsonify({"message": "Nenhum campo válido fornecido para atualização."}), 400

    try:
        db.session.commit()
        # Usar a função helper para formatar a resposta
        return jsonify({"message": "Jogador atualizado com sucesso!", "player": format_player(player)}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar jogador {player_id}: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao atualizar jogador."}), 500

@player_bp.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    try:
        db.session.delete(player)
        db.session.commit()
        return jsonify({"message": "Jogador excluído com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir jogador {player_id}: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao excluir jogador."}), 500

@player_bp.route("/players/<int:player_id>/edit-handicap", methods=["PUT"])
def edit_handicap(player_id):
    """Rota específica para editar apenas o handicap de um jogador"""
    player = Player.query.get_or_404(player_id)
    data = request.get_json()
    
    if not data or "handicap" not in data:
        return jsonify({"message": "Handicap é obrigatório"}), 400
    
    handicap = data["handicap"]
    if not isinstance(handicap, int) or not (0 <= handicap <= 36):
        return jsonify({"message": "Handicap inválido. Deve ser um número inteiro entre 0 e 36."}), 400
    
    try:
        player.handicap = handicap
        db.session.commit()
        return jsonify({
            "message": "Handicap atualizado com sucesso!", 
            "player": format_player(player)
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar handicap do jogador {player_id}: {e}")
        return jsonify({"message": "Erro interno ao atualizar handicap."}), 500

@player_bp.route("/players/<int:player_id>/edit", methods=["PUT"])
def edit_player(player_id):
    """Rota para editar nome e handicap de um jogador"""
    player = Player.query.get_or_404(player_id)
    data = request.get_json()
    
    if not data or ("name" not in data and "handicap" not in data):
        return jsonify({"message": "Nome ou handicap são obrigatórios"}), 400
    
    try:
        if "name" in data:
            # Verificar se o novo nome já existe (e não é o nome atual do jogador)
            existing_player = Player.query.filter(Player.name == data["name"], Player.id != player_id).first()
            if existing_player:
                return jsonify({"message": "Outro jogador com este nome já existe"}), 409
            player.name = data["name"]
            
        if "handicap" in data:
            handicap = data["handicap"]
            if not isinstance(handicap, int) or not (0 <= handicap <= 36):
                return jsonify({"message": "Handicap inválido. Deve ser um número inteiro entre 0 e 36."}), 400
            player.handicap = handicap
        
        db.session.commit()
        return jsonify({
            "message": "Jogador atualizado com sucesso!", 
            "player": format_player(player)
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar jogador {player_id}: {e}")
        return jsonify({"message": "Erro interno ao atualizar jogador."}), 500

@player_bp.route("/players/reset-wins", methods=["POST"])
def reset_all_wins():
    """Rota para zerar as vitórias de todos os jogadores"""
    try:
        # Atualizar todos os jogadores de uma vez
        Player.query.update({Player.score: 0})
        db.session.commit()
        return jsonify({"message": "Vitórias de todos os jogadores foram zeradas com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao zerar vitórias: {e}")
        return jsonify({"message": "Erro interno ao zerar vitórias."}), 500

@player_bp.route("/players/reset-games", methods=["POST"])
def reset_all_games():
    """Rota para zerar o número de jogos disputados de todos os jogadores"""
    try:
        # Atualizar todos os jogadores de uma vez
        Player.query.update({Player.games_played: 0})
        db.session.commit()
        return jsonify({"message": "Número de jogos de todos os jogadores foram zerados com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao zerar número de jogos: {e}")
        return jsonify({"message": "Erro interno ao zerar número de jogos."}), 500
