document.addEventListener("DOMContentLoaded", () => {
    const apiUrl = "/api"; // Base URL for API endpoints
    
    // Armazenar times anteriores para evitar repetições
    let previousTeams = [];
    let currentTeams = []; // Para armazenar os times atuais para exportação PDF

    // Elements
    const addPlayerForm = document.getElementById("add-player-form");
    const playerNameInput = document.getElementById("player-name");
    const playerHandicapInput = document.getElementById("player-handicap");
    const addPlayerMessage = document.getElementById("add-player-message");
    const playerListMessage = document.getElementById("player-list-message");
    const playersList = document.getElementById("players-list");
    const generateTeamsBtn = document.getElementById("generate-teams-btn");
    const teamSizeInput = document.getElementById("team-size");
    const teamsDisplay = document.getElementById("teams-display");
    const generateTeamsMessage = document.getElementById("generate-teams-message");
    const recordWinMessage = document.getElementById("record-win-message");

    // --- Player Management ---

    // Function to determine player category based on handicap
    function getPlayerCategory(handicap) {
        if (handicap === null || handicap === undefined) return '';
        if (handicap <= 10) return 'A';
        if (handicap <= 18) return 'B';
        if (handicap <= 27) return 'C';
        return 'D';
    }

    // Function to fetch and display players
    async function fetchPlayers() {
        try {
            const response = await fetch(`${apiUrl}/players`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const players = await response.json();
            renderPlayers(players);
        } catch (error) {
            console.error("Erro ao buscar jogadores:", error);
            showMessage(playerListMessage, "Erro ao carregar jogadores.", "error");
        }
    }

    // Function to render players in the table with pagination
    function renderPlayers(players) {
        playersList.innerHTML = ""; // Clear existing list
        if (!players || players.length === 0) {
            playersList.innerHTML = '<tr><td colspan="6">Nenhum jogador cadastrado.</td></tr>';
            return;
        }
        
        // Sort by category then name for grouping
        players.sort((a, b) => {
            const catA = getPlayerCategory(a.handicap);
            const catB = getPlayerCategory(b.handicap);
            if (catA < catB) return -1;
            if (catA > catB) return 1;
            return a.name.localeCompare(b.name);
        });

        // Mostrar o número total de jogadores
        const totalPlayersInfo = document.createElement("div");
        totalPlayersInfo.className = "total-players-info";
        totalPlayersInfo.innerHTML = `<p>Total de jogadores cadastrados: <strong>${players.length}</strong></p>`;
        
        // Inserir antes da tabela
        const playersTable = document.getElementById("players-table");
        const existingInfo = document.querySelector(".total-players-info");
        if (existingInfo) {
            existingInfo.remove();
        }
        playersTable.parentNode.insertBefore(totalPlayersInfo, playersTable);

        let currentCategory = null;
        players.forEach(player => {
            const category = getPlayerCategory(player.handicap);
            const categoryClass = `category-${category.toLowerCase()}`;

            // Optional: Add category header row (uncomment if desired)
            if (category !== currentCategory) {
                const headerRow = document.createElement("tr");
                headerRow.innerHTML = `<td colspan="6" class="category-header ${categoryClass}">Categoria ${category}</td>`;
                playersList.appendChild(headerRow);
                currentCategory = category;
            }

            const row = document.createElement("tr");
            row.classList.add(categoryClass); // Add class for styling
            row.innerHTML = `
                <td><input type="checkbox" class="player-select" data-id="${player.id}"></td>
                <td>${player.name}</td>
                <td>${player.handicap} (Cat: ${category})</td>
                <td>${player.score}</td>
                <td>${player.games_played !== undefined ? player.games_played : 0}</td>
                <td>
                    <button class="edit-player-btn" data-id="${player.id}" data-name="${player.name}" data-handicap="${player.handicap}">Editar Jogador</button>
                    <button class="delete-btn" data-id="${player.id}">Excluir</button>
                </td>
            `;
            playersList.appendChild(row);
        });
    }

    // Function to add a player
    async function addPlayer(event) {
        event.preventDefault();
        const name = playerNameInput.value.trim();
        const handicap = parseInt(playerHandicapInput.value, 10);

        if (!name || isNaN(handicap) || handicap < 0 || handicap > 36) {
            showMessage(addPlayerMessage, "Por favor, insira um nome válido e um handicap entre 0 e 36.", "error");
            return;
        }

        try {
            const response = await fetch(`${apiUrl}/players`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name, handicap }),
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            showMessage(addPlayerMessage, `Jogador '${result.player.name}' adicionado com sucesso!`, "success");
            addPlayerForm.reset(); // Clear form
            fetchPlayers(); // Refresh player list
        } catch (error) {
            console.error("Erro ao adicionar jogador:", error);
            showMessage(addPlayerMessage, `Erro: ${error.message}`, "error");
        }
    }

    // Function to delete a player
    async function deletePlayer(playerId) {
        if (!confirm("Tem certeza que deseja excluir este jogador?")) {
            return;
        }
        try {
            const response = await fetch(`${apiUrl}/players/${playerId}`, {
                method: "DELETE",
            });
             const result = await response.json();
            if (!response.ok) {
                 throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            showMessage(playerListMessage, result.message, "success"); // Show delete message near player list
            fetchPlayers(); // Refresh player list
        } catch (error) {
            console.error("Erro ao excluir jogador:", error);
             showMessage(playerListMessage, `Erro ao excluir: ${error.message}`, "error");
        }
    }

    // Function to edit player (name and handicap)
    async function editPlayer(playerId, playerName, currentHandicap) {
        // Criar um formulário personalizado para edição
        const newName = prompt(`Editar nome do jogador (atual: ${playerName})`, playerName);
        
        if (newName === null) {
            return; // User cancelled name edit
        }
        
        const newHandicap = prompt(`Editar handicap de ${newName} (atual: ${currentHandicap})`, currentHandicap);
        
        if (newHandicap === null) {
            return; // User cancelled handicap edit
        }
        
        const handicapValue = parseInt(newHandicap, 10);
        if (isNaN(handicapValue) || handicapValue < 0 || handicapValue > 36) {
            alert("Por favor, insira um handicap válido entre 0 e 36.");
            return;
        }
        
        try {
            const response = await fetch(`${apiUrl}/players/${playerId}/edit`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    name: newName,
                    handicap: handicapValue 
                }),
            });
            
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            
            showMessage(playerListMessage, `Jogador atualizado com sucesso para ${newName} (HCP: ${handicapValue})!`, "success");
            fetchPlayers(); // Refresh player list
        } catch (error) {
            console.error("Erro ao atualizar jogador:", error);
            showMessage(playerListMessage, `Erro: ${error.message}`, "error");
        }
    }

    // Event listener for adding players
    addPlayerForm.addEventListener("submit", addPlayer);

    // Event listener for player actions (using event delegation)
    playersList.addEventListener("click", (event) => {
        if (event.target.classList.contains("delete-btn")) {
            const playerId = event.target.getAttribute("data-id");
            deletePlayer(playerId);
        } else if (event.target.classList.contains("edit-player-btn")) {
            const playerId = event.target.getAttribute("data-id");
            const playerName = event.target.getAttribute("data-name");
            const currentHandicap = event.target.getAttribute("data-handicap");
            editPlayer(playerId, playerName, currentHandicap);
        }
    });

    // --- Reset Functions ---
    
    // Function to reset all wins
    async function resetAllWins() {
        if (!confirm("Tem certeza que deseja zerar as vitórias de TODOS os jogadores? Esta ação não pode ser desfeita.")) {
            return;
        }
        
        try {
            const response = await fetch(`${apiUrl}/players/reset-wins`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                }
            });
            
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            
            showMessage(playerListMessage, result.message, "success");
            fetchPlayers(); // Refresh player list
        } catch (error) {
            console.error("Erro ao zerar vitórias:", error);
            showMessage(playerListMessage, `Erro: ${error.message}`, "error");
        }
    }
    
    // Function to reset all games
    async function resetAllGames() {
        if (!confirm("Tem certeza que deseja zerar o número de jogos de TODOS os jogadores? Esta ação não pode ser desfeita.")) {
            return;
        }
        
        try {
            const response = await fetch(`${apiUrl}/players/reset-games`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                }
            });
            
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            
            showMessage(playerListMessage, result.message, "success");
            fetchPlayers(); // Refresh player list
        } catch (error) {
            console.error("Erro ao zerar número de jogos:", error);
            showMessage(playerListMessage, `Erro: ${error.message}`, "error");
        }
    }
    
    // Event listeners for reset buttons
    document.getElementById("reset-wins-btn").addEventListener("click", resetAllWins);
    document.getElementById("reset-games-btn").addEventListener("click", resetAllGames);
    
    // --- Team Generation ---

    // Function to generate teams
    async function generateTeams() {
        const teamSize = parseInt(teamSizeInput.value, 10);
        if (isNaN(teamSize) || teamSize < 3) {
            showMessage(generateTeamsMessage, "Por favor, insira um tamanho de time válido (mínimo 3).", "error");
            return;
        }

        // Get selected player IDs
        const selectedCheckboxes = playersList.querySelectorAll(".player-select:checked");
        const selectedPlayerIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.getAttribute("data-id"), 10));

        if (selectedPlayerIds.length === 0) {
            showMessage(generateTeamsMessage, "Por favor, selecione pelo menos um jogador para o sorteio.", "error");
            return;
        }
        
        if (selectedPlayerIds.length < 3) {
             showMessage(generateTeamsMessage, `Número insuficiente de jogadores selecionados (${selectedPlayerIds.length}) para formar times (mínimo 3).`, "error");
            return;
        }

        try {
            const response = await fetch(`${apiUrl}/teams/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                 body: JSON.stringify({ 
                     team_size: teamSize, 
                     player_ids: selectedPlayerIds,
                     previous_teams: previousTeams // Enviar times anteriores para evitar repetições
                 }),
            });
            const teams = await response.json();
             if (!response.ok) {
                throw new Error(teams.message || `HTTP error! status: ${response.status}`);
            }
            currentTeams = teams; // Armazenar para exportação PDF
            renderTeams(teams);
            // Armazenar os times gerados para uso futuro
            previousTeams = teams;
            showMessage(generateTeamsMessage, "Times gerados com sucesso!", "success");
            // Atualizar a lista de jogadores para mostrar o novo games_played
            fetchPlayers(); 
        } catch (error) {
            console.error("Erro ao gerar times:", error);
            showMessage(generateTeamsMessage, `Erro: ${error.message}`, "error");
            teamsDisplay.innerHTML = ""; // Clear previous teams on error
        }
    }

    // Function to render generated teams
    function renderTeams(teams) {
        teamsDisplay.innerHTML = ""; // Clear previous display
        recordWinMessage.textContent = ""; // Clear previous win messages
        recordWinMessage.className = "message";
        
        if (!teams || teams.length === 0) {
            teamsDisplay.innerHTML = "<p>Nenhum time gerado.</p>";
            return;
        }

        // Adicionar botão para exportar PDF
        const exportPdfBtn = document.createElement("button");
        exportPdfBtn.id = "export-pdf-btn";
        exportPdfBtn.textContent = "Exportar Times para PDF";
        exportPdfBtn.classList.add("export-pdf-btn");
        exportPdfBtn.addEventListener("click", exportTeamsToPdf);
        teamsDisplay.appendChild(exportPdfBtn);

        teams.forEach(team => {
            const teamCard = document.createElement("div");
            teamCard.classList.add("team-card");
            // Usar handicap original para exibição, mas o ponderado foi usado para balancear
            const playerListItems = team.players.map(p => {
                const category = getPlayerCategory(p.handicap);
                return `<li>${p.name} (HCP: ${p.handicap}, Cat: ${category})</li>`;
            }).join("");
            const playerIds = team.players.map(p => p.id);

            teamCard.innerHTML = `
                <h4>Time ${team.team_number} (HCP Ponderado Total: ${team.total_weighted_handicap})</h4>
                <ul>${playerListItems}</ul>
                <button class="record-win-btn" data-player-ids='${JSON.stringify(playerIds)}'>Registrar Vitória para este Time</button>
            `;
            teamsDisplay.appendChild(teamCard);
        });
    }

    // Function to export teams to PDF
    async function exportTeamsToPdf() {
        if (!currentTeams || currentTeams.length === 0) {
            alert("Nenhum time disponível para exportar. Por favor, gere os times primeiro.");
            return;
        }

        try {
            // Mostrar mensagem de carregamento
            showMessage(generateTeamsMessage, "Gerando PDF, aguarde...", "info");

            const response = await fetch(`${apiUrl}/teams/generate-pdf`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ teams: currentTeams }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            // Obter o blob do PDF
            const blob = await response.blob();
            
            // Criar URL para o blob
            const url = window.URL.createObjectURL(blob);
            
            // Criar link para download
            const a = document.createElement('a');
            a.href = url;
            a.download = 'times_golfe.pdf';
            document.body.appendChild(a);
            a.click();
            
            // Limpar
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showMessage(generateTeamsMessage, "PDF gerado com sucesso!", "success");
        } catch (error) {
            console.error("Erro ao exportar PDF:", error);
            showMessage(generateTeamsMessage, `Erro ao gerar PDF: ${error.message}`, "error");
        }
    }

    // Event listener for generating teams
    generateTeamsBtn.addEventListener("click", generateTeams);

    // --- Record Win ---

    // Function to record a win
    async function recordWin(playerIds) {
         if (!confirm("Confirmar vitória para este time? A pontuação dos jogadores será incrementada.")) {
            return;
        }
        try {
            const response = await fetch(`${apiUrl}/teams/record_win`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ winning_player_ids: playerIds }),
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            showMessage(recordWinMessage, result.message, "success");
            fetchPlayers(); // Refresh player list to show updated scores
            
            // NOVA FUNCIONALIDADE: Limpar times após registrar vitória
            teamsDisplay.innerHTML = '';
            generateTeamsMessage.textContent = '';
            generateTeamsMessage.className = 'message';
            currentTeams = []; // Limpar times atuais
        } catch (error) {
            console.error("Erro ao registrar vitória:", error);
            showMessage(recordWinMessage, `Erro: ${error.message}`, "error");
        }
    }

    // Event listener for recording wins (using event delegation on teamsDisplay)
    teamsDisplay.addEventListener("click", (event) => {
        if (event.target.classList.contains("record-win-btn")) {
            const playerIds = JSON.parse(event.target.getAttribute("data-player-ids"));
            recordWin(playerIds);
        }
    });

    // --- Utility Functions ---

    // Function to display messages
    function showMessage(element, message, type = "info") {
        if (!element) return; // Safety check
        element.textContent = message;
        element.className = `message ${type}`;
        // Clear message after some time
        setTimeout(() => {
            if (element.textContent === message) { // Only clear if the message hasn't changed
                 element.textContent = "";
                 element.className = "message";
            }
        }, 7000); // Clears after 7 seconds
    }

    // Initial load of players
    fetchPlayers();
});
