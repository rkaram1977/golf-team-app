from flask import Blueprint, request, jsonify, make_response
from fpdf import FPDF
from src.models.player import db, Player

player_bp = Blueprint("player_bp", __name__)


@player_bp.route("/players", methods=["GET"])
def get_players():
    players = Player.query.all()
    result = []
    for player in players:
        result.append({
            "id": player.id,
            "name": player.name,
            "handicap": player.handicap,
            "score": player.score,
            "games_played": player.games_played
        })
    return jsonify(result)


@player_bp.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"message": "Jogador não encontrado"}), 404
    return jsonify({
        "id": player.id,
        "name": player.name,
        "handicap": player.handicap,
        "score": player.score,
        "games_played": player.games_played
    })


@player_bp.route("/players", methods=["POST"])
def create_player():
    data = request.get_json()
    new_player = Player(
        name=data["name"],
        handicap=data["handicap"],
        score=data["score"],
        games_played=data["games_played"]
    )
    db.session.add(new_player)
    db.session.commit()
    return jsonify({"message": "Jogador criado com sucesso"}), 201


@player_bp.route("/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"message": "Jogador não encontrado"}), 404

    data = request.get_json()
    player.name = data.get("name", player.name)
    player.handicap = data.get("handicap", player.handicap)
    player.score = data.get("score", player.score)
    player.games_played = data.get("games_played", player.games_played)

    db.session.commit()
    return jsonify({"message": "Jogador atualizado com sucesso"})


@player_bp.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"message": "Jogador não encontrado"}), 404

    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": "Jogador deletado com sucesso"})


# ✅ Função para gerar PDF com fpdf2
@player_bp.route("/players/<int:player_id>/pdf", methods=["GET"])
def generate_player_pdf(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"message": "Jogador não encontrado"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "src/static/fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(200, 10, txt="Relatório do Jogador", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"• Nome: {player.name}", ln=True)
    pdf.cell(200, 10, txt=f"• Handicap: {player.handicap}", ln=True)
    pdf.cell(200, 10, txt=f"• Score: {player.score}", ln=True)
    pdf.cell(200, 10, txt=f"• Partidas Jogadas: {player.games_played}", ln=True)

    response = make_response(bytes(pdf.output(dest='S')))
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'inline', filename='jogador.pdf')
    return response
