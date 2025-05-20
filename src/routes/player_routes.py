
import os
from flask import Blueprint, request, jsonify, send_file, make_response
from src.models.player import db, Player
from sqlalchemy import update
from fpdf import FPDF

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


from fpdf import FPDF
from flask import make_response

@player_bp.route("/players/<int:player_id>/pdf", methods=["GET"])
def generate_player_pdf(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"message": "Jogador não encontrado"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Relatório do Jogador", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"- Nome: {player.name}", ln=True)
    pdf.cell(200, 10, txt=f"- Handicap: {player.handicap}", ln=True)
    pdf.cell(200, 10, txt=f"- Score: {player.score}", ln=True)
    pdf.cell(200, 10, txt=f"- Partidas Jogadas: {player.games_played}", ln=True)

    response = make_response(bytes(pdf.output(dest='S')))
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'inline', filename='jogador.pdf')
    return response