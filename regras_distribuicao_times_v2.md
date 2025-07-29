# Regras de Distribuição de Times Implementadas (Revisão 2)

Olá! Com base no seu feedback, atualizei a lista de regras e prioridades que o algoritmo seguirá para formar os times. Por favor, revise esta versão atualizada:

**Objetivo Principal:**
*   Criar times o mais equilibrados possível com base na **soma dos handicaps ponderados** de seus jogadores, minimizando a diferença entre o time de maior e menor HCP ponderado.
*   Evitar ao máximo a **repetição de jogadores** nos mesmos times em sorteios consecutivos (requer informação de times anteriores).

**Ordem de Execução Prioritária:**
1.  **Cálculo do Handicap Ponderado Individual:**
    *   Categoria A (HCP 0-10): Soma 25% do handicap.
    *   Categoria B (HCP 11-18): Soma 20% do handicap.
    *   Categoria C (HCP 19-27): Soma 15% do handicap.
    *   Categoria D (HCP 28+): Soma 10% do handicap.

2.  **Definição do Tamanho dos Times:**
    *   Prioriza times de **4 jogadores**.
    *   Forma times de **3 e 4 jogadores** quando necessário, minimizando o número de times de 3.

3.  **Ajuste Fino - Prioridade Jogador A em Times de 3 (Executado Primeiro se Aplicável):**
    *   **Condição:** Apenas se houver times de tamanhos mistos (3 e 4).
    *   **Ação:** O jogador da **categoria A** com o **menor handicap absoluto** é identificado.
    *   Se ele estiver em um time de 4, o algoritmo tenta movê-lo para um time de 3 (priorizando times de 3 sem nenhum jogador A, ou o time de 3 com o jogador A de maior HCP).
    *   Uma troca é realizada com um jogador de categoria inferior (D > C > B) do time de 3 para o time de 4 original, mantendo os tamanhos dos times e buscando equilibrar o HCP ponderado na troca.

4.  **Distribuição Inicial e Balanceamento (Após ajuste fino, se aplicável):**
    *   Os jogadores (incluindo os que podem ter sido trocados no passo anterior) são distribuídos aos times.
    *   A distribuição inicial tenta alocar jogadores de diferentes categorias (A, B, C, D) entre os times.
    *   Jogadores restantes são adicionados aos times com **menor soma de handicap ponderado** atual para atingir o tamanho alvo (3 ou 4) e promover o equilíbrio.

5.  **Verificação Final - Limite de Jogadores Categoria A (Nova Regra):**
    *   Após a formação inicial, o algoritmo verifica se algum time possui **mais de um jogador da Categoria A**.
    *   Se houver, e se for possível (ou seja, se houver times com espaço e sem jogador A), o algoritmo tentará mover o jogador A de **maior handicap** desse time para outro time que não tenha jogador A, priorizando a troca que **minimize o desequilíbrio** no HCP ponderado total dos times envolvidos.
    *   Se não for possível evitar mais de um A por time (ex: poucos times, muitos jogadores A), a configuração é mantida, focando no melhor equilíbrio de HCP ponderado possível.

6.  **Regra Específica - Categoria B (Mantida):**
    *   Se houver exatamente **3 jogadores da categoria B** e forem formados **3 times**, o algoritmo garante que cada time receba exatamente um jogador da categoria B (esta regra é aplicada durante a distribuição).

7.  **Ordenação Final:**
    *   Dentro de cada time, os jogadores são listados por categoria (A, B, C, D) e depois por nome.

**Observação sobre Repetição:** A lógica para evitar repetição de jogadores (item mencionado no seu feedback) será implementada considerando os dados de times anteriores, se fornecidos ao algoritmo. A prioridade será dada ao equilíbrio do HCP ponderado e às regras de categoria, mas o algoritmo tentará minimizar repetições conhecidas.

Por favor, confirme se esta versão atualizada das regras e da ordem de execução está alinhada com suas expectativas. Com sua aprovação, ajustarei o código do algoritmo para seguir exatamente esta lógica.

Enquanto isso, continuo trabalhando no ajuste do layout do rodapé do PDF.
