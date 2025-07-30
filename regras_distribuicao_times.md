# Regras de Distribuição de Times Implementadas

Olá! Conforme solicitado, compilei uma lista detalhada de todas as regras e critérios que o algoritmo utiliza atualmente para formar os times de golfe. Por favor, revise esta lista para garantir que todas as suas expectativas estão contempladas ou se precisamos ajustar alguma prioridade:

1.  **Objetivo Principal:** Criar times o mais equilibrados possível com base na **soma dos handicaps ponderados** de seus jogadores.

2.  **Cálculo do Handicap Ponderado:**
    *   Categoria A (HCP 0-10): Soma 25% do handicap individual.
    *   Categoria B (HCP 11-18): Soma 20% do handicap individual.
    *   Categoria C (HCP 19-27): Soma 15% do handicap individual.
    *   Categoria D (HCP 28+): Soma 10% do handicap individual.

3.  **Tamanho dos Times:**
    *   O sistema prioriza a formação de times com **4 jogadores**.
    *   Quando o número total de jogadores não é múltiplo de 4, o sistema forma times de **3 e 4 jogadores** para incluir todos, calculando a combinação que minimiza o número de times de 3 (Ex: 7 jogadores -> 1x4, 1x3; 10 jogadores -> 1x4, 2x3; 11 jogadores -> 2x4, 1x3).
    *   Times com menos de 3 ou mais de 4 jogadores são evitados (exceto em situações de fallback extremo).

4.  **Distribuição Inicial por Categoria:**
    *   O algoritmo tenta distribuir inicialmente os jogadores das categorias A, B, C e D de forma relativamente uniforme entre os times disponíveis para evitar concentração excessiva de uma categoria em um único time.

5.  **Balanceamento do Handicap Ponderado:**
    *   Após a distribuição inicial, os jogadores restantes são adicionados aos times que possuem a **menor soma de handicap ponderado** no momento, visando equalizar o total entre os times.

6.  **Regra Específica - Categoria B:**
    *   Se houver exatamente **3 jogadores da categoria B** e forem formados **3 times**, o algoritmo garante que cada time receba exatamente um jogador da categoria B.

7.  **Regra Específica - Evitar Concentração A/B vs C/D:**
    *   O algoritmo inclui lógicas para tentar evitar que um time fique composto apenas por jogadores das categorias C e D enquanto outro time concentra jogadores das categorias A e B. Isso é feito através da distribuição inicial e ajustes posteriores, se necessário.

8.  **Regra Específica - Prioridade Jogador A em Times de 3 (Última Implementação):**
    *   Quando são formados times de **tamanhos mistos (3 e 4 jogadores)**:
        *   O jogador da **categoria A** com o **menor handicap absoluto** (ex: HCP 2 é menor que HCP 5) é **prioritariamente alocado em um time de 3 jogadores**.
        *   Para isso, ele é trocado com um jogador de categoria inferior (preferencialmente D ou C) que estava originalmente em um time de 3.

9.  **Ordenação Final:**
    *   Dentro de cada time formado, os jogadores são listados em ordem de categoria (A, B, C, D) e, dentro de cada categoria, por ordem alfabética de nome.

Por favor, verifique se esta lista reflete todas as regras desejadas e se a ordem de prioridade (especialmente entre o balanceamento geral do HCP ponderado e a regra específica do jogador A em times de 3) está como você espera. Com seu feedback, posso fazer os ajustes finos necessários no algoritmo.

Enquanto você revisa, já vou trabalhar no ajuste do layout do rodapé do PDF.
