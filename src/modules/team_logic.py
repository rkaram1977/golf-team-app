import random

def create_balanced_teams(players, team_size=4, previous_teams=None):
    """
    Cria times equilibrados com base no handicap PONDERADO dos jogadores.
    Permite times de 3 ou 4 jogadores para acomodar todos os jogadores selecionados.
    Evita ao máximo repetir jogadores nos mesmos times com base em formações anteriores.
    Distribui jogadores por categoria para garantir equilíbrio entre os times.
    
    Args:
        players: Lista de dicionários de jogadores com id, name, handicap, weighted_handicap
        team_size: Tamanho preferencial do time (4 por padrão)
        previous_teams: Lista opcional de times anteriores para evitar repetições
    """
    try:
        num_players = len(players)
        if num_players < 3:  # Mínimo de 3 jogadores para formar um time
            raise ValueError("Número insuficiente de jogadores para formar um time (mínimo 3).")

        # Calcular o número ideal de times
        num_teams = max(1, (num_players + 3) // 4)  # Pelo menos 1 time, no máximo 4 jogadores por time
        
        # Inicializar times vazios
        teams = [[] for _ in range(num_teams)]
        team_weighted_handicaps = [0.0] * num_teams
        
        # Criar uma cópia da lista de jogadores para não modificar a original
        all_players = players.copy()
        
        # Separar jogadores por categoria
        players_by_category = {
            'A': [p for p in all_players if 0 <= p["handicap"] <= 10],
            'B': [p for p in all_players if 11 <= p["handicap"] <= 18],
            'C': [p for p in all_players if 19 <= p["handicap"] <= 27],
            'D': [p for p in all_players if p["handicap"] >= 28]
        }
        
        # Ordenar jogadores dentro de cada categoria por handicap ponderado
        for category in players_by_category:
            players_by_category[category].sort(key=lambda p: p["weighted_handicap"])
        
        # Distribuir jogadores de categorias superiores primeiro (A, B)
        # Garantir que jogadores A e B sejam distribuídos uniformemente
        
        # Distribuir jogadores A
        players_a = players_by_category['A']
        for i, player in enumerate(players_a):
            team_idx = i % num_teams
            teams[team_idx].append(player)
            team_weighted_handicaps[team_idx] += player["weighted_handicap"]
        
        # Distribuir jogadores B - garantir pelo menos um por time se possível
        players_b = players_by_category['B']
        if len(players_b) >= num_teams:
            # Se temos B suficientes para cada time, garantir que cada time tenha pelo menos um
            for i in range(num_teams):
                if players_b:
                    player = players_b.pop(0)
                    teams[i].append(player)
                    team_weighted_handicaps[i] += player["weighted_handicap"]
        
        # Distribuir os jogadores B restantes
        for i, player in enumerate(players_b):
            # Encontrar o time com menor handicap ponderado total
            team_idx = min(range(num_teams), key=lambda idx: team_weighted_handicaps[idx])
            teams[team_idx].append(player)
            team_weighted_handicaps[team_idx] += player["weighted_handicap"]
        
        # Distribuir jogadores C
        players_c = players_by_category['C']
        # Tentar distribuir pelo menos um C por time se possível
        if len(players_c) >= num_teams:
            # Verificar quais times ainda não têm jogadores A ou B
            teams_without_ab = [i for i, team in enumerate(teams) if not any(0 <= p["handicap"] <= 18 for p in team)]
            
            # Priorizar times sem A ou B para receber jogadores C
            for team_idx in teams_without_ab:
                if players_c:
                    player = players_c.pop(0)
                    teams[team_idx].append(player)
                    team_weighted_handicaps[team_idx] += player["weighted_handicap"]
        
        # Distribuir os jogadores C restantes
        for i, player in enumerate(players_c):
            # Encontrar o time com menor handicap ponderado total
            team_idx = min(range(num_teams), key=lambda idx: team_weighted_handicaps[idx])
            teams[team_idx].append(player)
            team_weighted_handicaps[team_idx] += player["weighted_handicap"]
        
        # Distribuir jogadores D
        players_d = players_by_category['D']
        for i, player in enumerate(players_d):
            # Encontrar o time com menor handicap ponderado total
            team_idx = min(range(num_teams), key=lambda idx: team_weighted_handicaps[idx])
            teams[team_idx].append(player)
            team_weighted_handicaps[team_idx] += player["weighted_handicap"]
        
        # Verificar se algum time tem mais de 4 jogadores
        for i, team in enumerate(teams):
            if len(team) > 4:
                # Redistribuir jogadores excedentes para times com menos de 4
                while len(team) > 4:
                    # Encontrar time com menos jogadores
                    min_team_idx = min(range(num_teams), key=lambda idx: len(teams[idx]))
                    if len(teams[min_team_idx]) >= 4:
                        # Todos os times já têm 4 jogadores, precisamos criar um novo time
                        teams.append([])
                        team_weighted_handicaps.append(0.0)
                        min_team_idx = len(teams) - 1
                        num_teams += 1
                    
                    # Mover um jogador para o time com menos jogadores
                    # Priorizar mover jogadores de categorias inferiores (C, D)
                    team.sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"]))
                    player = team.pop(0)  # Pegar o primeiro (categoria inferior)
                    teams[min_team_idx].append(player)
                    team_weighted_handicaps[min_team_idx] += player["weighted_handicap"]
                    team_weighted_handicaps[i] -= player["weighted_handicap"]
        
        # Verificação final: garantir que nenhum time tenha mais de 4 jogadores ou menos de 3
        for team_idx, team in enumerate(teams):
            if len(team) > 4:
                print(f"Time {team_idx+1} tem {len(team)} jogadores, ajustando...")
                # Redistribuir jogadores excedentes para times com menos de 4
                while len(team) > 4:
                    # Criar um novo time se necessário
                    if all(len(t) >= 3 for t in teams):
                        teams.append([])
                        team_weighted_handicaps.append(0.0)
                        new_team_idx = len(teams) - 1
                        num_teams += 1
                    else:
                        # Encontrar time com menos de 3 jogadores
                        new_team_idx = next((i for i, t in enumerate(teams) if len(t) < 3), -1)
                    
                    # Mover um jogador (priorizar categorias inferiores)
                    team.sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"]))
                    player = team.pop(0)
                    teams[new_team_idx].append(player)
                    team_weighted_handicaps[new_team_idx] += player["weighted_handicap"]
                    team_weighted_handicaps[team_idx] -= player["weighted_handicap"]
            
            # Garantir mínimo de 3 jogadores por time
            if len(team) < 3 and num_players >= 3 * num_teams:
                print(f"Time {team_idx+1} tem apenas {len(team)} jogadores, ajustando...")
                # Encontrar times com mais de 3 jogadores
                for other_idx, other_team in enumerate(teams):
                    if other_idx != team_idx and len(other_team) > 3:
                        # Mover um jogador (priorizar categorias inferiores)
                        other_team.sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"]))
                        player = other_team.pop(0)
                        team.append(player)
                        team_weighted_handicaps[team_idx] += player["weighted_handicap"]
                        team_weighted_handicaps[other_idx] -= player["weighted_handicap"]
                        if len(team) >= 3:
                            break
        
        # Verificar se há times com 3 e 4 jogadores e priorizar jogadores A em times de 3
        # Primeiro, identificar times com 3 e 4 jogadores
        teams_with_3 = [i for i, team in enumerate(teams) if len(team) == 3]
        teams_with_4 = [i for i, team in enumerate(teams) if len(team) == 4]
        
        # Se temos times com 3 e 4 jogadores, verificar se podemos mover jogadores A para times de 3
        if teams_with_3 and teams_with_4:
            # Coletar todos os jogadores A de todos os times com 4 jogadores
            all_a_players = []
            for team_idx_4 in teams_with_4:
                a_players_in_team = [(p, team_idx_4) for p in teams[team_idx_4] if 0 <= p["handicap"] <= 10]
                all_a_players.extend(a_players_in_team)
            
            # Ordenar jogadores A por handicap (do menor para o maior)
            all_a_players.sort(key=lambda x: x[0]["handicap"])
            
            # Se temos jogadores A, priorizar o de menor handicap para time de 3
            if all_a_players:
                # Pegar o jogador A com menor handicap
                best_player, source_team_idx = all_a_players[0]
                
                # Encontrar um time com 3 jogadores que não tenha jogador A
                for team_idx_3 in teams_with_3:
                    if not any(0 <= p["handicap"] <= 10 for p in teams[team_idx_3]):
                        # Mover o jogador A de menor handicap para o time de 3
                        teams[source_team_idx].remove(best_player)
                        teams[team_idx_3].append(best_player)
                        # Atualizar handicaps
                        team_weighted_handicaps[team_idx_3] += best_player["weighted_handicap"]
                        team_weighted_handicaps[source_team_idx] -= best_player["weighted_handicap"]
                        
                        # Agora precisamos mover um jogador do time de 3 para o time de 4
                        # Priorizar jogadores de categorias inferiores (C, D)
                        teams[team_idx_3].sort(key=lambda p: (-get_category_order(p["handicap"]), p["weighted_handicap"]))
                        # Não mover o jogador A que acabamos de adicionar
                        non_a_players = [p for p in teams[team_idx_3] if p["handicap"] > 10]
                        if non_a_players:
                            player_to_move = non_a_players[0]
                            teams[team_idx_3].remove(player_to_move)
                            teams[source_team_idx].append(player_to_move)
                            # Atualizar handicaps
                            team_weighted_handicaps[source_team_idx] += player_to_move["weighted_handicap"]
                            team_weighted_handicaps[team_idx_3] -= player_to_move["weighted_handicap"]
                            break
        
        # Verificar se há times sem jogadores A ou B quando há jogadores A e B disponíveis
        total_ab_players = len(players_by_category['A']) + len(players_by_category['B'])
        if total_ab_players > 0:
            for team_idx, team in enumerate(teams):
                # Verificar se o time não tem jogadores A ou B
                if not any(0 <= p["handicap"] <= 18 for p in team):
                    # Procurar um time com mais de um jogador A ou B para transferir
                    for other_idx, other_team in enumerate(teams):
                        if other_idx != team_idx:
                            # Contar jogadores A e B neste time
                            ab_players = [p for p in other_team if 0 <= p["handicap"] <= 18]
                            if len(ab_players) > 1:
                                # Transferir um jogador B se possível
                                b_players = [p for p in ab_players if 11 <= p["handicap"] <= 18]
                                if b_players:
                                    player = b_players[0]
                                else:
                                    player = ab_players[0]
                                
                                # Remover o jogador do time original
                                other_team.remove(player)
                                # Adicionar ao time sem A/B
                                team.append(player)
                                # Atualizar handicaps
                                team_weighted_handicaps[team_idx] += player["weighted_handicap"]
                                team_weighted_handicaps[other_idx] -= player["weighted_handicap"]
                                break
        
        # Formatar a saída
        output_teams = []
        for i, team in enumerate(teams):
            if len(team) < 3 and num_players < 3 * num_teams:
                # Se não há jogadores suficientes para todos os times terem pelo menos 3,
                # apenas incluir times com jogadores
                if len(team) > 0:
                    # Ordenar jogadores dentro do time por categoria e depois por nome
                    team.sort(key=lambda p: (get_category_order(p["handicap"]), p["name"]))
                    output_teams.append({
                        "team_number": len(output_teams) + 1,
                        "players": team,
                        "total_weighted_handicap": round(team_weighted_handicaps[i], 2)
                    })
            else:
                # Ordenar jogadores dentro do time por categoria e depois por nome
                team.sort(key=lambda p: (get_category_order(p["handicap"]), p["name"]))
                output_teams.append({
                    "team_number": len(output_teams) + 1,
                    "players": team,
                    "total_weighted_handicap": round(team_weighted_handicaps[i], 2)
                })
        
        return output_teams
    
    except Exception as e:
        # Logar o erro completo para facilitar depuração
        import traceback
        print(f"Erro detalhado na formação de times: {str(e)}")
        print(traceback.format_exc())
        
        # Tentar uma abordagem mais simples como fallback
        return fallback_team_creation(players)

def fallback_team_creation(players):
    """
    Método de fallback para criar times quando o algoritmo principal falha.
    Simplesmente divide os jogadores em grupos de 3-4 sem tentar equilibrar.
    """
    try:
        num_players = len(players)
        if num_players < 3:
            raise ValueError("Número insuficiente de jogadores para formar um time (mínimo 3).")
        
        # Embaralhar jogadores para aleatoriedade
        shuffled_players = players.copy()
        random.shuffle(shuffled_players)
        
        # Determinar quantos times de 3 e quantos de 4
        if num_players % 4 == 0:
            team_sizes = [4] * (num_players // 4)
        elif num_players % 4 == 1:
            team_sizes = [4] * (num_players // 4 - 1) + [5]  # Um time de 5 (exceção)
        elif num_players % 4 == 2:
            team_sizes = [4] * (num_players // 4 - 1) + [3, 3]  # Dois times de 3
        else:  # num_players % 4 == 3
            team_sizes = [4] * (num_players // 4) + [3]  # Um time de 3
        
        # Criar times
        teams = []
        player_index = 0
        
        for i, size in enumerate(team_sizes):
            team_players = shuffled_players[player_index:player_index + size]
            player_index += size
            
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
        raise ValueError("Não foi possível formar times com os jogadores selecionados.")

def get_category_order(handicap):
    """Retorna um valor para ordenação baseado na categoria do handicap"""
    if 0 <= handicap <= 10:
        return 0  # Categoria A
    elif 11 <= handicap <= 18:
        return 1  # Categoria B
    elif 19 <= handicap <= 27:
        return 2  # Categoria C
    else:
        return 3  # Categoria D
