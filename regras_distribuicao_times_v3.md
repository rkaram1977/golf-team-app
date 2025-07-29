# Regras de Distribuição de Times Implementadas (Revisão 3 - Final)

Olá! Incorporei sua última sugestão sobre a preferência por times de 3 em vez de múltiplos jogadores A no mesmo time. Por favor, revise esta versão final das regras:

**Objetivo Principal:**
*   Criar times o mais equilibrados possível com base na **soma dos handicaps ponderados** de seus jogadores, minimizando a diferença entre o time de maior e menor HCP ponderado.
*   Evitar ao máximo a **repetição de jogadores** nos mesmos times em sorteios consecutivos (requer informação de times anteriores).

**Ordem de Execução Prioritária:**
1.  **Cálculo do Handicap Ponderado Individual:**
    *   Categoria A (HCP 0-10): Soma 25% do handicap.
    *   Categoria B (HCP 11-18): Soma 20% do handicap.
    *   Categoria C (HCP 19-27): Soma 15% do handicap.
    *   Categoria D (HCP 28+): Soma 10% do handicap.

2.  **Definição do Tamanho Inicial dos Times:**
    *   Calcula a combinação de times de **3 e 4 jogadores** que acomoda todos os participantes, **minimizando inicialmente o número de times de 3**.

3.  **Ajuste Fino - Prioridade Jogador A (Menor HCP) em Times de 3:**
    *   **Condição:** Apenas se houver times de tamanhos mistos (3 e 4) após o cálculo inicial.
    *   **Ação:** O jogador da **categoria A** com o **menor handicap absoluto** é identificado.
    *   Se ele estiver em um time de 4, o algoritmo tenta movê-lo para um time de 3 (priorizando times de 3 sem nenhum jogador A, ou o time de 3 com o jogador A de maior HCP).
    *   Uma troca é realizada com um jogador de categoria inferior (D > C > B) do time de 3 para o time de 4 original, mantendo os tamanhos dos times e buscando equilibrar o HCP ponderado na troca.

4.  **Distribuição Inicial e Balanceamento:**
    *   Os jogadores (incluindo os que podem ter sido trocados no passo anterior) são distribuídos aos times.
    *   A distribuição inicial tenta alocar jogadores de diferentes categorias (A, B, C, D) entre os times.
    *   Jogadores restantes são adicionados aos times com **menor soma de handicap ponderado** atual para atingir o tamanho alvo (3 ou 4) e promover o equilíbrio.

5.  **Verificação Final - Limite de Jogadores Categoria A (Regra Refinada):**
    *   Após a formação inicial, o algoritmo verifica se algum time possui **mais de um jogador da Categoria A**.
    *   **Prioridade:** É **preferível ter mais times de 3 jogadores do que ter dois jogadores da Categoria A no mesmo time**.
    *   **Ação:** Se um time tem mais de um jogador A, o algoritmo tentará mover o(s) jogador(es) A excedente(s) (começando pelo de maior HCP) para outro(s) time(s) que não tenha(m) jogador A.
    *   Se a única forma de evitar dois jogadores A no mesmo time for **reestruturar os times** (ex: transformar um time de 4 em um de 3 para receber o jogador A excedente), o algoritmo **considerará essa opção**, desde que mantenha um equilíbrio razoável no HCP ponderado.
    *   Se, mesmo após tentativas de reestruturação, não for possível evitar mais de um A por time (ex: número muito alto de jogadores A para o número de times), a configuração com múltiplos A será mantida, focando no melhor equilíbrio de HCP ponderado possível nessa situação.

6.  **Regra Específica - Categoria B (Mantida):**
    *   Se houver exatamente **3 jogadores da categoria B** e forem formados **3 times**, o algoritmo garante que cada time receba exatamente um jogador da categoria B (aplicada durante a distribuição).

7.  **Ordenação Final:**
    *   Dentro de cada time, os jogadores são listados por categoria (A, B, C, D) e depois por nome.

**Observação sobre Repetição:** A lógica para evitar repetição de jogadores será implementada considerando os dados de times anteriores, se fornecidos. A prioridade será o equilíbrio do HCP ponderado e as regras de categoria/limite de A, mas o algoritmo tentará minimizar repetições conhecidas.

Esta é a versão final das regras, incorporando todas as suas sugestões. Por favor, confirme se está tudo correto para que eu possa prosseguir com a implementação no código.

Enquanto aguardo, farei o ajuste no layout do rodapé do PDF.
