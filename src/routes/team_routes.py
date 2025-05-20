from flask import Blueprint, request, jsonify, send_file
from src.models.player import db, Player
from src.modules.team_logic import create_balanced_teams
import tempfile
import os
from jinja2 import Template
import base64
from fpdf import FPDF
from datetime import datetime

team_bp = Blueprint("team_bp", __name__)

# Armazenar times anteriores para evitar repetições
previous_teams = []

@team_bp.route("/teams/generate", methods=["POST"])
def generate_teams():
    data = request.get_json()
    team_size = data.get("team_size", 4)
    player_ids = data.get("player_ids") # Agora será obrigatório

    if not isinstance(team_size, int) or team_size < 3: # Times precisam de pelo menos 3 jogadores
        return jsonify({"message": "Tamanho do time inválido. Mínimo de 3 jogadores por time."}), 400

    # Tornar player_ids obrigatório
    if not player_ids or not isinstance(player_ids, list) or len(player_ids) == 0:
        return jsonify({"message": "A lista de IDs de jogadores participantes é obrigatória."}), 400

    # Validar se todos os IDs existem
    players_query = Player.query.filter(Player.id.in_(player_ids))
    players_count = players_query.count()
    
    if players_count != len(player_ids):
        # Encontrar quais IDs são inválidos (opcional, mas bom para depuração)
        valid_ids = {p.id for p in players_query}
        invalid_ids = [pid for pid in player_ids if pid not in valid_ids]
        return jsonify({"message": f"Um ou mais IDs de jogadores fornecidos são inválidos: {invalid_ids}"}), 400
        
    players = players_query.all()

    if not players:
        # Isso não deve acontecer se a validação acima funcionar, mas por segurança
        return jsonify({"message": "Nenhum jogador válido encontrado para formar times."}), 404
        
    # Verificar se há jogadores suficientes para o tamanho mínimo do time (3)
    if len(players) < 3:
        return jsonify({"message": f"Jogadores insuficientes ({len(players)}) para formar times (mínimo 3)."}), 400

    # Incrementar games_played para os jogadores selecionados
    for player in players:
        player.games_played += 1
    
    # Salvar o incremento de jogos disputados ANTES de gerar os times
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar games_played: {e}") # Log do erro no servidor
        return jsonify({"message": "Erro interno ao atualizar contagem de jogos disputados."}), 500

    # Preparar dados para a função de lógica (usando o handicap ponderado)
    player_list_for_logic = [
        {
            "id": p.id, 
            "name": p.name, 
            "handicap": p.handicap, # Handicap original ainda pode ser útil
            "weighted_handicap": p.get_weighted_handicap(), # Usar o handicap ponderado para balanceamento
            "score": p.score,
            "games_played": p.games_played
        }
        for p in players
    ]

    try:
        # Usar times anteriores para evitar repetições
        global previous_teams
        teams = create_balanced_teams(player_list_for_logic, team_size, previous_teams)
        # Atualizar times anteriores
        previous_teams = teams
        return jsonify(teams), 200
    except ValueError as e:
        # Reverter o incremento de games_played se a formação de times falhar?
        # Por enquanto, vamos manter o incremento, pois eles foram selecionados para jogar.
        # db.session.rollback() # Descomentar se a lógica de negócio exigir reverter.
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        # Erro genérico na lógica de formação de times
        print(f"Erro na lógica de formação de times: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao gerar os times."}), 500

@team_bp.route("/teams/record_win", methods=["POST"])
def record_win():
    data = request.get_json()
    winning_player_ids = data.get("winning_player_ids")

    if not winning_player_ids or not isinstance(winning_player_ids, list):
        return jsonify({"message": "Lista de IDs de jogadores vencedores é obrigatória."}), 400

    updated_players = []
    not_found_ids = []

    # Usar uma transação para garantir atomicidade
    try:
        for player_id in winning_player_ids:
            player = Player.query.get(player_id)
            if player:
                player.score += 1 # Incrementa a pontuação
                updated_players.append({"id": player.id, "name": player.name, "new_score": player.score})
            else:
                not_found_ids.append(player_id)
        
        if not_found_ids:
            # Se algum ID não foi encontrado, reverter tudo
            db.session.rollback()
            return jsonify({"message": f"Jogadores com IDs {not_found_ids} não encontrados. Nenhuma pontuação atualizada."}), 404
        else:
            # Se todos foram encontrados, salvar as alterações
            db.session.commit()
            return jsonify({
                "message": f"Pontuações atualizadas com sucesso para {len(updated_players)} jogadores.",
                "updated_players": updated_players
            }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar vitória: {e}") # Log do erro
        return jsonify({"message": "Erro interno ao registrar vitória."}), 500

@team_bp.route("/teams/generate-pdf", methods=["POST"])
def generate_teams_pdf():
    data = request.get_json()
    teams = data.get("teams")
    
    if not teams or not isinstance(teams, list) or len(teams) == 0:
        return jsonify({"message": "Dados de times são obrigatórios."}), 400
    
    try:
        # Caminho para os logos
        scramble_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "logo.jpeg")
        karam_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "logo-karam.jpeg")
        
        # Verificar se os arquivos existem
        if not os.path.exists(scramble_logo_path) or not os.path.exists(karam_logo_path):
            return jsonify({"message": "Arquivos de logo não encontrados."}), 500
        
        # Função para determinar a categoria do jogador
        def get_category(handicap):
            if handicap <= 10:
                return 'A'
            elif handicap <= 18:
                return 'B'
            elif handicap <= 27:
                return 'C'
            else:
                return 'D'
        
        # Criar PDF usando FPDF
        class PDF(FPDF):
            def header(self):
                pass  # Vamos personalizar o cabeçalho manualmente
                
            def footer(self):
                pass  # Vamos personalizar o rodapé manualmente
        
        # Criar instância do PDF (orientação paisagem para acomodar melhor os times)
        pdf = PDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Adicionar fonte padrão
        pdf.set_font("helvetica", size=11)
        
        # Adicionar logo no topo
        pdf.image(scramble_logo_path, x=pdf.w/2 - 40, y=10, w=80)
        pdf.ln(85)  # Espaço após o logo
        
        # Título
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(44, 94, 26)  # Verde escuro (#2c5e1a)
        pdf.cell(0, 10, "Formação dos Times de Golfe", align="C")
        pdf.ln(15)
        
        # Data
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", align="R")
        pdf.ln(15)
        
        # Cores para categorias
        category_colors = {
            'A': (204, 229, 255),  # Light blue
            'B': (212, 237, 218),  # Light green
            'C': (255, 243, 205),  # Light yellow
            'D': (248, 215, 218)   # Light red
        }
        
        # Adicionar times
        for team in teams:
            # Título do time
            pdf.set_fill_color(33, 150, 243)  # Azul (#2196F3)
            pdf.set_text_color(255, 255, 255)  # Branco
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, f"Time {team['team_number']} (HCP Ponderado Total: {team['total_weighted_handicap']})", 1, 1, "L", True)
            
            # Jogadores do time
            pdf.set_text_color(0, 0, 0)  # Preto
            pdf.set_font("helvetica", "", 11)
            
            for player in team["players"]:
                category = get_category(player["handicap"])
                pdf.set_fill_color(*category_colors[category])
                pdf.cell(0, 8, f"{player['name']} (HCP: {player['handicap']}, Cat: {category})", 1, 1, "L", True)
            
            pdf.ln(5)  # Espaço entre times
        
        # Verificar se precisamos de uma nova página para as regras
        if pdf.get_y() > 180:
            pdf.add_page()
        
        # Título das regras
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(44, 94, 26)  # Verde escuro (#2c5e1a)
        pdf.cell(0, 10, "Regras Gerais", align="C")
        pdf.ln(15)
        
        # Regra 1
        pdf.set_fill_color(249, 249, 249)  # Cinza claro
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(44, 94, 26)  # Verde escuro
        pdf.cell(0, 10, "1. Cálculo do Handicap Ponderado", 1, 1, "L", True)
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)  # Preto
        pdf.multi_cell(0, 6, "O handicap de cada jogador é ponderado de acordo com sua categoria para equilibrar os times:", 0, "L")
        
        # Lista de categorias
        pdf.ln(2)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• Categoria A (0-10): 25% do handicap", 0, 1)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• Categoria B (11-18): 20% do handicap", 0, 1)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• Categoria C (19-27): 15% do handicap", 0, 1)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• Categoria D (28+): 10% do handicap", 0, 1)
        pdf.ln(2)
        
        pdf.multi_cell(0, 6, "Exemplo: Um jogador com handicap 8 (categoria A) terá handicap ponderado de 2 (25% de 8). Este cálculo é utilizado para garantir uma distribuição mais justa e equilibrada dos times, considerando as diferentes habilidades dos jogadores.", 0, "L")
        pdf.ln(5)
        
        # Regra 2
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(44, 94, 26)  # Verde escuro
        pdf.cell(0, 10, "2. Alívio de Um Taco (Não Mais Perto do Buraco)", 1, 1, "L", True)
        
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)  # Preto
        pdf.multi_cell(0, 6, "Quando permitido pelas regras locais, um jogador pode obter alívio de uma condição anormal do campo:", 0, "L")
        
        # Lista de regras
        pdf.ln(2)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• O jogador pode dropar a bola dentro do comprimento de um taco da posição original", 0, 1)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• A nova posição não pode estar mais próxima do buraco", 0, 1)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• A bola deve ser dropada de altura do joelho", 0, 1)
        pdf.cell(10, 6, "", 0, 0)
        pdf.cell(0, 6, "• O alívio não é permitido em áreas de penalidade ou bunkers, exceto quando especificado", 0, 1)
        pdf.ln(2)
        
        pdf.multi_cell(0, 6, "Esta regra ajuda a manter o jogo justo quando a bola está em condições desfavoráveis. O jogador deve anunciar sua intenção de utilizar esta regra antes de mover a bola, e todos os membros do grupo devem concordar com a aplicação do alívio na situação específica.", 0, "L")
        
        # Rodapé com logo Karam Design
        pdf.ln(10)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, "Design by:", 0, 1, "C")
        pdf.image(karam_logo_path, x=pdf.w/2 - 15, y=pdf.get_y(), w=30)
        pdf.ln(15)
        pdf.cell(0, 6, "© 2025 Todos os direitos reservados a Karam Design", 0, 1, "C")
        
        # Criar arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_path = temp_file.name
        
        # Salvar o PDF
        pdf.output(pdf_path)
        
        # Enviar o arquivo PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name="times_golfe.pdf",
            mimetype="application/pdf"
        )
    
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return jsonify({"message": f"Erro interno ao gerar PDF: {str(e)}"}), 500
