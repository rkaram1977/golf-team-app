import sys
import os
# Add the project root to the Python path to allow importing src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.team_logic import create_balanced_teams, get_category_order

def calculate_weighted_handicap(handicap):
    if 0 <= handicap <= 10: # Cat A
        return handicap * 0.25
    elif 11 <= handicap <= 18: # Cat B
        return handicap * 0.20
    elif 19 <= handicap <= 27: # Cat C
        return handicap * 0.15
    else: # Cat D (28+)
        return handicap * 0.10

def run_test(test_name, players_data):
    print(f"--- Executando Teste: {test_name} ---")
    players = []
    for i, p_data in enumerate(players_data):
        hcp = p_data['handicap']
        player = {
            'id': i + 1,
            'name': p_data['name'],
            'handicap': hcp,
            'weighted_handicap': calculate_weighted_handicap(hcp)
        }
        players.append(player)
        
    print(f"Jogadores ({len(players)}): {[p['name']+'(A'+str(p['handicap'])+')' if get_category_order(p['handicap']) == 0 else p['name']+'('+chr(ord('A') + get_category_order(p['handicap']))+str(p['handicap'])+')' for p in players]}")

    try:
        teams = create_balanced_teams(players)
        
        print("Times Formados:")
        teams_of_3 = []
        teams_of_4 = []
        lowest_hcp_a_player = min([p for p in players if get_category_order(p['handicap']) == 0], key=lambda p: p['handicap'], default=None)
        
        if not lowest_hcp_a_player:
            print("  Nenhum jogador Categoria A no teste.")
            for team in teams:
                print(f"  Time {team['team_number']} ({len(team['players'])} jogadores): {[p['name'] for p in team['players']]}")
            print(f"Resultado {test_name}: SUCESSO (sem jogador A para verificar prioridade)")
            return True

        lowest_a_in_team_3 = False
        for team in teams:
            team_size = len(team['players'])
            player_names = [p['name'] for p in team['players']]
            print(f"  Time {team['team_number']} ({team_size} jogadores): {player_names} (HCP Pond: {team['total_weighted_handicap']})")
            if team_size == 3:
                teams_of_3.append(team)
                if lowest_hcp_a_player in team['players']:
                    lowest_a_in_team_3 = True
            elif team_size == 4:
                teams_of_4.append(team)

        # Verificação da regra
        if teams_of_3 and teams_of_4: # Apenas verificar se há times mistos
            if lowest_a_in_team_3:
                print(f"VERIFICAÇÃO: Jogador A de menor HCP ({lowest_hcp_a_player['name']} HCP {lowest_hcp_a_player['handicap']}) está em um time de 3. CORRETO.")
                print(f"Resultado {test_name}: SUCESSO")
                return True
            else:
                print(f"VERIFICAÇÃO: Jogador A de menor HCP ({lowest_hcp_a_player['name']} HCP {lowest_hcp_a_player['handicap']}) NÃO está em um time de 3. INCORRETO.")
                print(f"Resultado {test_name}: FALHA")
                return False
        else:
            print("VERIFICAÇÃO: Não há times mistos de 3 e 4 jogadores. Regra de prioridade não aplicável neste caso.")
            print(f"Resultado {test_name}: SUCESSO (não aplicável)")
            return True
            
    except Exception as e:
        print(f"Erro ao formar times: {e}")
        print(f"Resultado {test_name}: ERRO")
        return False

# --- Cenários de Teste --- 

# Teste 1: 7 Jogadores (1x4, 1x3) - A(2) vs A(5)
players_7 = [
    {'name': 'Player A2', 'handicap': 2}, # Menor A
    {'name': 'Player A5', 'handicap': 5},
    {'name': 'Player B15', 'handicap': 15},
    {'name': 'Player C20', 'handicap': 20},
    {'name': 'Player C25', 'handicap': 25},
    {'name': 'Player D30', 'handicap': 30},
    {'name': 'Player D35', 'handicap': 35}
]

# Teste 2: 11 Jogadores (2x4, 1x3) - A(2) vs A(5) vs A(8)
players_11 = [
    {'name': 'Player A2', 'handicap': 2}, # Menor A
    {'name': 'Player A5', 'handicap': 5},
    {'name': 'Player A8', 'handicap': 8},
    {'name': 'Player B12', 'handicap': 12},
    {'name': 'Player B18', 'handicap': 18},
    {'name': 'Player C20', 'handicap': 20},
    {'name': 'Player C22', 'handicap': 22},
    {'name': 'Player C26', 'handicap': 26},
    {'name': 'Player D28', 'handicap': 28},
    {'name': 'Player D32', 'handicap': 32},
    {'name': 'Player D36', 'handicap': 36}
]

# Teste 3: 10 Jogadores (1x4, 2x3) - A(2) vs A(5)
players_10 = [
    {'name': 'Player A2', 'handicap': 2}, # Menor A
    {'name': 'Player A5', 'handicap': 5},
    {'name': 'Player B11', 'handicap': 11},
    {'name': 'Player B16', 'handicap': 16},
    {'name': 'Player C19', 'handicap': 19},
    {'name': 'Player C21', 'handicap': 21},
    {'name': 'Player C25', 'handicap': 25},
    {'name': 'Player D29', 'handicap': 29},
    {'name': 'Player D31', 'handicap': 31},
    {'name': 'Player D34', 'handicap': 34}
]

# Teste 4: 8 Jogadores (2x4) - Regra não aplicável
players_8 = [
    {'name': 'Player A2', 'handicap': 2},
    {'name': 'Player A5', 'handicap': 5},
    {'name': 'Player B11', 'handicap': 11},
    {'name': 'Player B16', 'handicap': 16},
    {'name': 'Player C19', 'handicap': 19},
    {'name': 'Player C21', 'handicap': 21},
    {'name': 'Player D29', 'handicap': 29},
    {'name': 'Player D31', 'handicap': 31}
]

# Teste 5: 6 Jogadores (2x3) - Regra não aplicável
players_6 = [
    {'name': 'Player A2', 'handicap': 2},
    {'name': 'Player A5', 'handicap': 5},
    {'name': 'Player B11', 'handicap': 11},
    {'name': 'Player C19', 'handicap': 19},
    {'name': 'Player D29', 'handicap': 29},
    {'name': 'Player D31', 'handicap': 31}
]


# Executar testes
results = []
results.append(run_test("7 Jogadores (1x4, 1x3)", players_7))
print("\n")
results.append(run_test("11 Jogadores (2x4, 1x3)", players_11))
print("\n")
results.append(run_test("10 Jogadores (1x4, 2x3)", players_10))
print("\n")
results.append(run_test("8 Jogadores (2x4)", players_8))
print("\n")
results.append(run_test("6 Jogadores (2x3)", players_6))
print("\n")

print("--- Resumo dos Testes ---")
if all(results):
    print("TODOS OS TESTES PASSARAM!")
else:
    print("ALGUNS TESTES FALHARAM.")

