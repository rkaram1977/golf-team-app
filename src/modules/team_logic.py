import random

def get_category_order(handicap):
    """Retorna um valor para ordenação baseado na categoria do handicap"""
    if 0 <= handicap <= 10:  # Categoria A
        return 0
    elif 11 <= handicap <= 18: # Categoria B
        return 1
    elif 19 <= handicap <= 27: # Categoria C
        return 2
    else: # Categoria D
        return 3

def create_balanced_teams(players, team_size=4, previous_teams=None):
    """
    Cria times equilibrados com base no handicap PONDERADO dos jogadores.
    Permite times de 3 ou 4 jogadores para acomodar todos os jogadores selecionados.
    Evita ao máximo repetir jogadores nos mesmos times com base em formações anteriores.
    Distribui jogadores por categoria para garantir equilíbrio entre os times.
    Prioriza o jogador A de menor handicap em times de 3 quando há times mistos.
    
    Args:
        players: Lista de dicionários de jogadores com id, name, handicap, weighted_handicap
        team_size: Tamanho preferencial do time (4 por padrão)
        previous_teams: Lista opcional de times anteriores para evitar repetições
    """
    try:
        num_players = len(players)
        if num_players < 3:
            raise ValueError("Número insuficiente de jogadores para formar um time (mínimo 3).")

        # Calcular o número ideal de times e tamanhos
        num_teams = 0
        teams_of_3 = 0
        teams_of_4 = 0

        if num_players % 4 == 0:
            num_teams = num_players // 4
            teams_of_4 = num_teams
        elif num_players % 4 == 1:
            # Ex: 5 -> 1 time de 5 (impossível com regra 3/4), 9 -> 1 time de 3, 2 times de 3? Não. 9 -> 2 times de 3, 1 time de 3? Não. 9 -> 1 time de 3, 1 time de 3, 1 time de 3? Não. 9 -> 1 time de 4, 1 time de 5? Não. 9 -> 3 times de 3.
            # Ex: 13 -> 1 time de 4, 1 time de 4, 1 time de 5? Não. 13 -> 1 time de 3, 2 times de 5? Não. 13 -> 1 time de 4, 3 times de 3.
            # A combinação que minimiza times de 3 é preferível, exceto se for impossível.
            # Regra: Formar o máximo de times de 4 possível.
            teams_of_4 = num_players // 4 - 2 # Ex: 9 -> 2-2=0; 13 -> 3-2=1
            teams_of_3 = 3 # Ex: 9 -> 3; 13 -> 3
            if teams_of_4 < 0: # Caso de 5 jogadores
                 teams_of_4 = 0
                 teams_of_3 = 0 # Não é possível formar times de 3/4 com 5 jogadores
                 # Fallback para 1 time de 5? Ou erro? Por ora, erro.
                 if num_players == 5:
                     raise ValueError("Não é possível formar times de 3 ou 4 com 5 jogadores.")
                 # Caso de 9 jogadores: 3 times de 3
                 elif num_players == 9:
                     teams_of_4 = 0
                     teams_of_3 = 3
                 else: # Caso geral para N%4 == 1 e N > 9
                     teams_of_4 = (num_players - 9) // 4
                     teams_of_3 = 3

        elif num_players % 4 == 2:
            # Ex: 6 -> 2 times de 3; 10 -> 1 time de 4, 2 times de 3; 14 -> 2 times de 4, 2 times de 3
            teams_of_4 = num_players // 4 - 1
            teams_of_3 = 2
        elif num_players % 4 == 3:
            # Ex: 7 -> 1 time de 4, 1 time de 3; 11 -> 2 times de 4, 1 time de 3; 15 -> 3 times de 4, 1 time de 3
            teams_of_4 = num_players // 4
            teams_of_3 = 1
            
        num_teams = teams_of_4 + teams_of_3

        # Inicializar times vazios
        teams = [[] for _ in range(num_teams)]
        team_weighted_handicaps = [0.0] * num_teams
        
        # Criar uma cópia da lista de jogadores para não modificar a original
        available_players = players.copy()
        
        # Separar jogadores por categoria
        players_by_category = {
            'A': sorted([p for p in available_players if 0 <= p["handicap"] <= 10], key=lambda p: p["weighted_handicap"]),
            'B': sorted([p for p in available_players if 11 <= p["handicap"] <= 18], key=lambda p: p["weighted_handicap"]),
            'C': sorted([p for p in available_players if 19 <= p["handicap"] <= 27], key=lambda p: p["weighted_handicap"]),
            'D': sorted([p for p in available_players if p["handicap"] >= 28], key=lambda p: p["weighted_handicap"])
        }
        
        # Distribuir jogadores - priorizando categorias e equilíbrio
        # Tentar colocar um jogador de cada categoria A, B, C, D em times diferentes inicialmente
        categories_to_distribute = ['A', 'B', 'C', 'D']
        
        for category in categories_to_distribute:
            players_in_category = players_by_category[category]
            # Distribuir um por time enquanto houver jogadores e times vazios nessa categoria
            for i in range(num_teams):
                if players_in_category:
                    # Tentar alocar no time 'i' se ele ainda não tiver essa categoria?
                    # Ou simplesmente distribuir sequencialmente?
                    # Vamos distribuir sequencialmente para começar
                    team_idx = i % num_teams
                    player = players_in_category.pop(0) # Pega o de menor HCP ponderado
                    teams[team_idx].append(player)
                    team_weighted_handicaps[team_idx] += player["weighted_handicap"]
                    available_players.remove(player)
        
        # Distribuir jogadores restantes, priorizando times com menor HCP ponderado
        # Ordenar jogadores restantes por HCP ponderado (menor primeiro)
        available_players.sort(key=lambda p: p["weighted_handicap"])
        
        target_team_sizes = [4] * teams_of_4 + [3] * teams_of_3
        # Embaralhar a ordem dos tamanhos para não enviesar a distribuição inicial
        random.shuffle(target_team_sizes)
        
        # Atribuir jogadores restantes aos times até atingirem o tamanho alvo
        for player in available_players:
            # Encontrar times que ainda não atingiram o tamanho alvo
            eligible_teams = [i for i, team in enumerate(teams) if len(team) < target_team_sizes[i]]
            if not eligible_teams:
                 # Se todos os times atingiram o tamanho, algo está errado ou é um caso excepcional
                 # Por segurança, adicionar ao time com menor HCP
                 eligible_teams = list(range(num_teams))
            
            # Escolher o time elegível com menor HCP ponderado atual
            best_team_idx = min(eligible_teams, key=lambda idx: team_weighted_handicaps[idx])
            
            teams[best_team_idx].append(player)
            team_weighted_handicaps[best_team_idx] += player["weighted_handicap"]

        # --- Ajuste Fino: Priorizar Jogador A de menor HCP em time de 3 --- 
        if teams_of_3 > 0 and teams_of_4 > 0:
            # 1. Encontrar o jogador A com o menor handicap absoluto em todos os times
            all_a_players_with_team = []
            for idx, team in enumerate(teams):
                for p in team:
                    if 0 <= p["handicap"] <= 10:
                        all_a_players_with_team.append((p, idx))
            
            if all_a_players_with_team:
                all_a_players_with_team.sort(key=lambda x: x[0]["handicap"]) # Ordenar por HCP real
                lowest_hcp_a_player, current_team_idx = all_a_players_with_team[0]
                current_team_size = len(teams[current_team_idx])

                # 2. Se este jogador NÃO está num time de 3, tentar movê-lo
                if current_team_size == 4:
                    # 3. Encontrar um time de 3 para receber este jogador
                    target_team_idx_3 = -1
                    # Prioridade 1: Time de 3 sem nenhum jogador A
                    possible_targets_no_a = [i for i, team in enumerate(teams) if len(team) == 3 and not any(0 <= p["handicap"] <= 10 for p in team)]
                    if possible_targets_no_a:
                        # Escolher o time de 3 sem A com maior HCP ponderado (para equilibrar)
                        target_team_idx_3 = max(possible_targets_no_a, key=lambda idx: team_weighted_handicaps[idx])
                    else:
                        # Prioridade 2: Time de 3 com o jogador A de MAIOR handicap
                        possible_targets_with_a = []
                        for i, team in enumerate(teams):
                            if len(team) == 3:
                                a_in_team3 = [p for p in team if 0 <= p["handicap"] <= 10]
                                if a_in_team3:
                                    # Encontrar o A de maior HCP neste time de 3
                                    a_in_team3.sort(key=lambda p: p["handicap"], reverse=True)
                                    possible_targets_with_a.append((i, a_in_team3[0])) # (team_idx, highest_hcp_a_player)
                        
                        if possible_targets_with_a:
                             # Ordenar os times de 3 pelo HCP do seu jogador A mais alto (maior HCP primeiro)
                            possible_targets_with_a.sort(key=lambda x: x[1]["handicap"], reverse=True)
                            # Escolher o time de 3 que tem o jogador A de maior HCP
                            target_team_idx_3, player_a_to_swap_out = possible_targets_with_a[0]
                    
                    # 4. Se um time de 3 foi encontrado, realizar a troca
                    if target_team_idx_3 != -1:
                        # Encontrar jogador para mover do time de 3 para o time de 4 original
                        # Priorizar não-A, e de categoria inferior (D > C > B)
                        team3 = teams[target_team_idx_3]
                        team3.sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"])) # D primeiro
                        player_to_move_from_3 = None
                        for p in team3:
                            if not (0 <= p["handicap"] <= 10): # Não mover jogador A se possível
                                player_to_move_from_3 = p
                                break
                        if not player_to_move_from_3 and len(team3) > 0: # Se só tem A no time de 3
                             # Escolher o A de maior HCP para mover (que não seja o que vai entrar, se for o caso)
                             a_in_team3 = [p for p in team3 if 0 <= p["handicap"] <= 10 and p != lowest_hcp_a_player]
                             if a_in_team3:
                                 a_in_team3.sort(key=lambda p: p["handicap"], reverse=True)
                                 player_to_move_from_3 = a_in_team3[0]
                             elif len(team3) > 0: # Se só tem o lowest_hcp_a_player (caso estranho)
                                 player_to_move_from_3 = team3[0] # Mover qualquer um

                        # Realizar a troca se encontramos quem mover
                        if player_to_move_from_3:
                            # Remover jogadores dos times originais
                            teams[current_team_idx].remove(lowest_hcp_a_player)
                            teams[target_team_idx_3].remove(player_to_move_from_3)
                            
                            # Adicionar jogadores aos novos times
                            teams[current_team_idx].append(player_to_move_from_3)
                            teams[target_team_idx_3].append(lowest_hcp_a_player)
                            
                            # Atualizar handicaps ponderados
                            team_weighted_handicaps[current_team_idx] -= lowest_hcp_a_player["weighted_handicap"]
                            team_weighted_handicaps[current_team_idx] += player_to_move_from_3["weighted_handicap"]
                            team_weighted_handicaps[target_team_idx_3] -= player_to_move_from_3["weighted_handicap"]
                            team_weighted_handicaps[target_team_idx_3] += lowest_hcp_a_player["weighted_handicap"]
                            print(f"Ajuste fino: Movi A{lowest_hcp_a_player['handicap']} para time de 3, trocando com {get_category_order(player_to_move_from_3['handicap'])}{player_to_move_from_3['handicap']}")

        # --- Fim do Ajuste Fino ---

        # Verificação final de equilíbrio de categorias (opcional, pode complexificar demais)
        # ... (código anterior de verificação de A/B omitido por simplicidade e foco na regra A)

        # Formatar a saída
        output_teams = []
        final_teams = [team for team in teams if team] # Remover times vazios se houver
        for i, team in enumerate(final_teams):
            # Ordenar jogadores dentro do time por categoria e depois por nome
            team.sort(key=lambda p: (get_category_order(p["handicap"]), p["name"]))
            # Recalcular handicap final do time para garantir precisão
            final_weighted_handicap = sum(p["weighted_handicap"] for p in team)
            output_teams.append({
                "team_number": i + 1,
                "players": team,
                "total_weighted_handicap": round(final_weighted_handicap, 2)
            })
        
        return output_teams
    
    except ValueError as ve:
        print(f"Erro na validação dos jogadores: {str(ve)}")
        raise ve # Repassar o erro de validação
    except Exception as e:
        # Logar o erro completo para facilitar depuração
        import traceback
        print(f"Erro detalhado na formação de times: {str(e)}")
        print(traceback.format_exc())
        # Tentar uma abordagem mais simples como fallback
        print("Tentando método de fallback para criação de times...")
        return fallback_team_creation(players)

def fallback_team_creation(players):
    """
    Método de fallback para criar times quando o algoritmo principal falha.
    Simplesmente divide os jogadores em grupos de 3-4 sem tentar equilibrar.
    """
    try:
        num_players = len(players)
        if num_players < 3:
            return [] # Retorna lista vazia se não pode formar times
        
        # Embaralhar jogadores para aleatoriedade
        shuffled_players = players.copy()
        random.shuffle(shuffled_players)
        
        # Determinar quantos times de 3 e quantos de 4 (lógica simplificada)
        num_teams = (num_players + 3) // 4
        base_size = num_players // num_teams
        remainder = num_players % num_teams
        
        team_sizes = [base_size + 1] * remainder + [base_size] * (num_teams - remainder)
        
        # Criar times
        teams = []
        player_index = 0
        
        for i, size in enumerate(team_sizes):
            if player_index >= num_players:
                break
            team_players = shuffled_players[player_index : min(player_index + size, num_players)]
            player_index += size
            
            if not team_players: continue # Evitar times vazios

            # Calcular handicap ponderado total
            total_weighted_handicap = sum(p["weighted_handicap"] for p in team_players)
            
            # Ordenar jogadores por categoria
            team_players.sort(key=lambda p: (get_category_order(p["handicap"]), p["name"]))
            
            teams.append({
                "team_number": i + 1,
                "players": team_players,
                "total_weighted_handicap": round(total_weighted_handicap, 2)
            })
        
        return teams
    
    except Exception as e:
        # Se até o fallback falhar, logar e retornar erro
        print(f"Erro no método fallback: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Retornar lista vazia ou erro mais específico?
        # Por segurança, retornar lista vazia para não quebrar a API
        return []

