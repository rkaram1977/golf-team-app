import random
import math

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

def calculate_team_sizes(num_players):
    """Calcula a combinação inicial de times de 3 e 4, minimizando times de 3."""
    if num_players < 3:
        return 0, 0, 0 # num_teams, teams_of_3, teams_of_4

    if num_players % 4 == 0:
        teams_of_4 = num_players // 4
        teams_of_3 = 0
    elif num_players % 4 == 1:
        # Precisa de 3 times de 3. Ex: 5->Inválido; 9->3x3; 13->1x4, 3x3; 17->2x4, 3x3
        if num_players == 5:
             raise ValueError("Não é possível formar times de 3 ou 4 com 5 jogadores.")
        teams_of_3 = 3
        teams_of_4 = (num_players - 9) // 4
    elif num_players % 4 == 2:
        # Precisa de 2 times de 3. Ex: 6->2x3; 10->1x4, 2x3; 14->2x4, 2x3
        teams_of_3 = 2
        teams_of_4 = (num_players - 6) // 4
    else: # num_players % 4 == 3
        # Precisa de 1 time de 3. Ex: 7->1x4, 1x3; 11->2x4, 1x3; 15->3x4, 1x3
        teams_of_3 = 1
        teams_of_4 = (num_players - 3) // 4
        
    num_teams = teams_of_4 + teams_of_3
    return num_teams, teams_of_3, teams_of_4

def create_balanced_teams(players, team_size=4, previous_teams=None):
    """
    Cria times equilibrados seguindo as regras v3.
    """
    try:
        num_players = len(players)
        num_teams, teams_of_3_initial, teams_of_4_initial = calculate_team_sizes(num_players)
        
        if num_teams == 0:
             raise ValueError("Número insuficiente de jogadores para formar um time (mínimo 3).")

        # Inicializar times vazios
        teams = [[] for _ in range(num_teams)]
        team_weighted_handicaps = [0.0] * num_teams
        target_team_sizes = [4] * teams_of_4_initial + [3] * teams_of_3_initial
        # Embaralhar a ordem dos tamanhos alvo para distribuição inicial
        # random.shuffle(target_team_sizes) # -> Não embaralhar aqui, faremos a atribuição direcionada
        
        # Criar uma cópia da lista de jogadores
        available_players = players.copy()
        
        # Separar e ordenar jogadores por categoria (HCP ponderado)
        players_by_category = {
            cat: sorted([p for p in available_players if get_category_order(p["handicap"]) == order], key=lambda p: p["weighted_handicap"])
            for order, cat in enumerate(["A", "B", "C", "D"])
        }

        # --- 1. Ajuste Fino: Prioridade Jogador A (Menor HCP) em Times de 3 --- 
        # Este ajuste precisa ser feito *após* uma distribuição inicial ou *durante* ela.
        # Vamos tentar fazer a distribuição inicial e depois os ajustes.

        # --- 2. Distribuição Inicial e Balanceamento --- 
        # Distribuir um jogador de cada categoria A, B, C, D sequencialmente
        categories_to_distribute = ["A", "B", "C", "D"]
        current_team_idx = 0
        for category in categories_to_distribute:
            players_in_category = players_by_category[category]
            # Distribuir um por time enquanto houver jogadores
            while players_in_category:
                player = players_in_category.pop(0)
                # Encontrar o próximo time que ainda não atingiu o tamanho alvo
                # e que tenha o menor HCP ponderado atual
                eligible_teams = []
                for i in range(num_teams):
                    if len(teams[i]) < target_team_sizes[i]:
                        eligible_teams.append(i)
                
                if not eligible_teams:
                    # Todos os times cheios? Improvável nesta fase.
                    # Adicionar ao time com menor HCP como fallback
                    best_team_idx = min(range(num_teams), key=lambda idx: team_weighted_handicaps[idx])
                else:
                    # Escolher o time elegível com menor HCP ponderado
                    best_team_idx = min(eligible_teams, key=lambda idx: team_weighted_handicaps[idx])

                teams[best_team_idx].append(player)
                team_weighted_handicaps[best_team_idx] += player["weighted_handicap"]
                available_players.remove(player)
                # current_team_idx = (current_team_idx + 1) % num_teams # Avança para o próximo time

        # Distribuir jogadores restantes (se houver)
        available_players.sort(key=lambda p: p["weighted_handicap"]) # Ordenar por HCP ponderado
        for player in available_players:
            eligible_teams = [i for i, team in enumerate(teams) if len(team) < target_team_sizes[i]]
            if not eligible_teams:
                best_team_idx = min(range(num_teams), key=lambda idx: team_weighted_handicaps[idx])
            else:
                best_team_idx = min(eligible_teams, key=lambda idx: team_weighted_handicaps[idx])
            
            teams[best_team_idx].append(player)
            team_weighted_handicaps[best_team_idx] += player["weighted_handicap"]

        # --- 3. Ajuste Fino Pós-Distribuição: Prioridade A em Times de 3 --- 
        teams_with_3 = [i for i, team in enumerate(teams) if len(team) == 3]
        teams_with_4 = [i for i, team in enumerate(teams) if len(team) == 4]
        
        if teams_with_3 and teams_with_4:
            all_a_players_with_team = []
            for idx, team in enumerate(teams):
                for p in team:
                    if get_category_order(p["handicap"]) == 0: # Categoria A
                        all_a_players_with_team.append((p, idx))
            
            if all_a_players_with_team:
                all_a_players_with_team.sort(key=lambda x: x[0]["handicap"]) # Ordenar por HCP real
                lowest_hcp_a_player, current_team_idx = all_a_players_with_team[0]
                
                # Se o jogador A de menor HCP está num time de 4, tentar mover
                if len(teams[current_team_idx]) == 4:
                    target_team_idx_3 = -1
                    # Prioridade 1: Time de 3 sem nenhum jogador A
                    possible_targets_no_a = [i for i in teams_with_3 if not any(get_category_order(p["handicap"]) == 0 for p in teams[i])]
                    if possible_targets_no_a:
                        target_team_idx_3 = max(possible_targets_no_a, key=lambda idx: team_weighted_handicaps[idx])
                    else:
                        # Prioridade 2: Time de 3 com o jogador A de MAIOR handicap
                        possible_targets_with_a = []
                        for i in teams_with_3:
                            a_in_team3 = [p for p in teams[i] if get_category_order(p["handicap"]) == 0]
                            if a_in_team3:
                                a_in_team3.sort(key=lambda p: p["handicap"], reverse=True)
                                possible_targets_with_a.append((i, a_in_team3[0]))
                        if possible_targets_with_a:
                            possible_targets_with_a.sort(key=lambda x: x[1]["handicap"], reverse=True)
                            target_team_idx_3, _ = possible_targets_with_a[0]
                    
                    # Se um time de 3 foi encontrado, realizar a troca
                    if target_team_idx_3 != -1:
                        team3 = teams[target_team_idx_3]
                        # Encontrar jogador para mover do time de 3 (Priorizar não-A, D > C > B)
                        team3.sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"])) 
                        player_to_move_from_3 = next((p for p in team3 if get_category_order(p["handicap"]) != 0), None)
                        if not player_to_move_from_3 and len(team3) > 0: # Se só tem A
                             a_in_team3 = [p for p in team3 if p != lowest_hcp_a_player]
                             if a_in_team3:
                                 a_in_team3.sort(key=lambda p: p["handicap"], reverse=True)
                                 player_to_move_from_3 = a_in_team3[0]
                             else: # Só tem o lowest_hcp_a_player (não deveria acontecer aqui)
                                 player_to_move_from_3 = team3[0] # Fallback

                        if player_to_move_from_3:
                            # Realizar a troca
                            teams[current_team_idx].remove(lowest_hcp_a_player)
                            teams[target_team_idx_3].remove(player_to_move_from_3)
                            teams[current_team_idx].append(player_to_move_from_3)
                            teams[target_team_idx_3].append(lowest_hcp_a_player)
                            # Atualizar handicaps ponderados
                            hcp_diff = player_to_move_from_3["weighted_handicap"] - lowest_hcp_a_player["weighted_handicap"]
                            team_weighted_handicaps[current_team_idx] += hcp_diff
                            team_weighted_handicaps[target_team_idx_3] -= hcp_diff
                            print(f"Ajuste Prioridade A: Movi A{lowest_hcp_a_player['handicap']} para time de 3, trocando com {chr(ord('A')+get_category_order(player_to_move_from_3['handicap']))}{player_to_move_from_3['handicap']}")
                            # Atualizar listas de times de 3 e 4 se necessário (embora os tamanhos não mudem aqui)
                            teams_with_3 = [i for i, team in enumerate(teams) if len(team) == 3]
                            teams_with_4 = [i for i, team in enumerate(teams) if len(team) == 4]

        # --- 4. Verificação Final - Limite de Jogadores Categoria A --- 
        made_adjustment_for_A_limit = True # Flag para loop
        max_iterations = num_teams # Evitar loop infinito
        current_iteration = 0
        while made_adjustment_for_A_limit and current_iteration < max_iterations:
            made_adjustment_for_A_limit = False
            current_iteration += 1
            teams_with_multiple_A = []
            for i, team in enumerate(teams):
                a_players = [p for p in team if get_category_order(p["handicap"]) == 0]
                if len(a_players) > 1:
                    a_players.sort(key=lambda p: p["handicap"], reverse=True) # Ordenar A por HCP (maior primeiro)
                    teams_with_multiple_A.append((i, a_players))
            
            if not teams_with_multiple_A:
                break # Sai do while se nenhum time tem mais de 1 A

            # Ordenar times com múltiplos A pelo HCP do segundo jogador A (maior primeiro)
            # Isso prioriza resolver os casos mais "problemáticos" primeiro
            teams_with_multiple_A.sort(key=lambda x: x[1][1]["handicap"], reverse=True)
            
            source_team_idx, a_players_list = teams_with_multiple_A[0]
            player_A_to_move = a_players_list[0] # Tentar mover o A de maior HCP

            # Encontrar um time destino: Prioridade 1: Time sem A
            possible_target_teams = []
            for target_idx, target_team in enumerate(teams):
                if target_idx != source_team_idx and not any(get_category_order(p["handicap"]) == 0 for p in target_team):
                    possible_target_teams.append(target_idx)
            
            best_target_idx = -1
            player_to_swap_from_target = None

            if possible_target_teams:
                # Encontrar o melhor time destino (sem A) e jogador para troca
                # Queremos trocar o A de maior HCP por um não-A que minimize o desequilíbrio
                min_hcp_diff = float("inf")
                for target_idx in possible_target_teams:
                    target_team = teams[target_idx]
                    target_team.sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"])) # Priorizar D, C, B
                    for p_target in target_team:
                        # Calcular diferença de HCP ponderado da troca
                        hcp_diff = abs((team_weighted_handicaps[source_team_idx] - player_A_to_move["weighted_handicap"] + p_target["weighted_handicap"]) - 
                                       (team_weighted_handicaps[target_idx] - p_target["weighted_handicap"] + player_A_to_move["weighted_handicap"]))
                        # Idealmente, queremos que a troca melhore o equilíbrio geral (difícil de medir simples)
                        # Vamos simplificar: trocar pelo não-A que resulta na menor diferença de HCP ponderado *entre os dois times*
                        current_diff_teams = abs(team_weighted_handicaps[source_team_idx] - team_weighted_handicaps[target_idx])
                        new_diff_teams = abs((team_weighted_handicaps[source_team_idx] - player_A_to_move["weighted_handicap"] + p_target["weighted_handicap"]) - 
                                           (team_weighted_handicaps[target_idx] - p_target["weighted_handicap"] + player_A_to_move["weighted_handicap"]))

                        # Se a nova diferença for menor ou igual (para permitir alguma troca)
                        # E o jogador alvo não é A
                        if new_diff_teams <= current_diff_teams + 0.5: # Adiciona pequena tolerância
                            best_target_idx = target_idx
                            player_to_swap_from_target = p_target
                            # Não precisa ser o mínimo absoluto, a primeira troca razoável serve
                            break 
                    if best_target_idx != -1:
                        break # Sai do loop de times alvo se achou uma troca
            
            # Se encontramos uma troca válida com um time sem A
            if best_target_idx != -1 and player_to_swap_from_target:
                # Realizar a troca
                teams[source_team_idx].remove(player_A_to_move)
                teams[best_target_idx].remove(player_to_swap_from_target)
                teams[source_team_idx].append(player_to_swap_from_target)
                teams[best_target_idx].append(player_A_to_move)
                # Atualizar handicaps
                hcp_diff = player_to_swap_from_target["weighted_handicap"] - player_A_to_move["weighted_handicap"]
                team_weighted_handicaps[source_team_idx] += hcp_diff
                team_weighted_handicaps[best_target_idx] -= hcp_diff
                print(f"Ajuste Limite A: Movi A{player_A_to_move['handicap']} do time {source_team_idx+1} para time {best_target_idx+1}, trocando com {chr(ord('A')+get_category_order(player_to_swap_from_target['handicap']))}{player_to_swap_from_target['handicap']}")
                made_adjustment_for_A_limit = True # Indica que fizemos ajuste, continua o while
            else:
                # Não foi possível trocar com time sem A. 
                # PRIORIDADE: Evitar 2 A no mesmo time, mesmo que crie mais times de 3.
                # Tentar mover o A excedente para um time existente (mesmo que já tenha A? Não, regra é 1 A)
                # OU Criar um novo time de 3? -> Isso muda a estrutura de times_of_3/4
                # Por simplicidade inicial, vamos manter a estrutura e aceitar >1 A se a troca não for possível.
                # A reestruturação para criar mais times de 3 adiciona muita complexidade aqui.
                # Vamos documentar essa limitação por enquanto.
                print(f"Ajuste Limite A: Não foi possível mover A{player_A_to_move['handicap']} do time {source_team_idx+1} sem piorar significativamente o equilíbrio ou violar outras regras.")
                # Não setar made_adjustment_for_A_limit = True se não conseguiu mover este A específico
                # Mas o loop while continua se houver *outros* times com múltiplos A para tentar resolver.
                # Se este era o único time com múltiplos A e não conseguimos ajustar, o loop while terminará.
                pass # Não faz nada se não achou troca boa

        # --- 5. Regra Específica - Categoria B (Verificação Pós-Ajustes) ---
        # Re-verificar se a regra dos 3 times com 1 B cada foi mantida, se aplicável
        if num_teams == 3 and len(players_by_category["B"]) == 3:
            b_distribution = [sum(1 for p in team if get_category_order(p["handicap"]) == 1) for team in teams]
            if b_distribution != [1, 1, 1]:
                print("Aviso: Ajustes posteriores podem ter desfeito a distribuição ideal de jogadores B.")
                # Poderia tentar reajustar aqui, mas aumenta complexidade.

        # --- 6. Formatar Saída --- 
        output_teams = []
        final_teams = [team for team in teams if team] # Remover times vazios
        for i, team in enumerate(final_teams):
            team.sort(key=lambda p: (get_category_order(p["handicap"]), p["name"]))
            final_weighted_handicap = sum(p["weighted_handicap"] for p in team)
            output_teams.append({
                "team_number": i + 1,
                "players": team,
                "total_weighted_handicap": round(final_weighted_handicap, 2)
            })
        
        return output_teams
    
    except ValueError as ve:
        print(f"Erro na validação dos jogadores: {str(ve)}")
        raise ve
    except Exception as e:
        import traceback
        print(f"Erro detalhado na formação de times: {str(e)}")
        print(traceback.format_exc())
        print("Tentando método de fallback para criação de times...")
        return fallback_team_creation(players)

def fallback_team_creation(players):
    """
    Método de fallback simplificado.
    """
    try:
        num_players = len(players)
        if num_players < 3:
            return []
        
        shuffled_players = players.copy()
        random.shuffle(shuffled_players)
        
        num_teams, _, _ = calculate_team_sizes(num_players)
        if num_teams == 0: return [] # Caso de 5 jogadores, por exemplo

        base_size = num_players // num_teams
        remainder = num_players % num_teams
        team_sizes = [base_size + 1] * remainder + [base_size] * (num_teams - remainder)
        
        teams_out = []
        player_index = 0
        for i, size in enumerate(team_sizes):
            if player_index >= num_players: break
            team_players = shuffled_players[player_index : min(player_index + size, num_players)]
            player_index += size
            if not team_players: continue

            total_weighted_handicap = sum(p["weighted_handicap"] for p in team_players)
            team_players.sort(key=lambda p: (get_category_order(p["handicap"]), p["name"]))
            
            teams_out.append({
                "team_number": i + 1,
                "players": team_players,
                "total_weighted_handicap": round(total_weighted_handicap, 2)
            })
        return teams_out
    except Exception as e:
        print(f"Erro no método fallback: {str(e)}")
        return []

