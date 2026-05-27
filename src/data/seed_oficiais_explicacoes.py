"""Aplica explicações por alternativa, eixo, subtópicos e dificuldade
em questões oficiais já parseadas no banco.

Idempotente: pode rodar várias vezes. Cada execução atualiza os campos
sem duplicar questões.

Cada questão coberta aqui é marcada com:
- validacao.validado = True
- validacao.confianca = 0.9
- validacao.modelo = "curadoria_manual"

Rodar: python -m src.data.seed_oficiais_explicacoes
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict

from .load import load_bank, save_bank
from .schema import Alternativa, Dificuldade, ValidacaoResult

NOW = datetime.now(timezone.utc).isoformat()


class ExplicacaoQuestao(TypedDict):
    eixo: str
    subtopicos: list[str]
    dificuldade: str
    explicacoes: dict[str, str]  # "a" -> texto


# =========================================================================
# Prova 2026/1
# =========================================================================
EXPL_2026_1: dict[str, ExplicacaoQuestao] = {
    "oficial_2026-1_q01": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["argumentos_validade", "proposicoes_conectivos"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "ERRADA. 'Luc reside na fazenda' não é dedutível como verdade absoluta a partir das premissas — a premissa II diz que SE algo acontece então ele reside, não que ele resida.",
            "b": "ERRADA. Mais forte que (a): exige tanto residir na fazenda quanto não treinar com cavalos, nenhum dos dois é dedutível como fato absoluto.",
            "c": "CORRETA. Pela contrapositiva: ¬fazenda → (pela II) ¬concurso ∧ ¬banco → (pela I) ¬termina_graduacao → (pela IV) trabalha_Haras → (pela III) participa_campeonato → (pela V, contrapositiva) treina com cavalos.",
            "d": "ERRADA. Combina dois fatos não dedutíveis como verdade absoluta; as premissas não forçam essa conclusão sem hipótese adicional.",
            "e": "ERRADA. A alternativa (c) é uma consequência lógica válida.",
        },
    },
    "oficial_2026-1_q02": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["silogismos", "argumentos_validade"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. Helena gosta de Liam e gosta apenas de educados, logo Liam é educado.",
            "b": "ERRADA. Não há premissa sobre o que Gil sente por Liam; nada se deduz nessa direção.",
            "c": "ERRADA. Helena gosta de Liam, e quem gosta de Liam gosta de Gil, então Helena gosta de Gil.",
            "d": "CORRETA. Helena gosta de Gil (transitividade pela 2ª premissa) e Helena só gosta de educados (3ª premissa), portanto Gil é educado.",
            "e": "ERRADA. A alternativa (d) é dedutível.",
        },
    },
    "oficial_2026-1_q03": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["quantificadores", "equivalencia_negacao"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. 'Alguns gostam de pelo menos uma' não nega a afirmação original; ambas podem coexistir.",
            "b": "ERRADA. É o oposto da original, não uma reformulação equivalente.",
            "c": "CORRETA. ¬∃x(ator(x) ∧ ∀y(novela(y) → gosta(x,y))) equivale a ∀x(ator(x) → ∃y(novela(y) ∧ ¬gosta(x,y))). Em português: para todo ator, há ao menos uma novela da qual ele não gosta.",
            "d": "ERRADA. 'Não é o caso que, para todo ator, há ao menos uma novela da qual ele gosta' equivale a 'existe ator que não gosta de novela alguma' — afirmação diferente.",
            "e": "ERRADA. A alternativa (c) é a equivalência correta.",
        },
    },
    "oficial_2026-1_q04": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["equivalencia_negacao", "quantificadores"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Essa é a própria afirmação original ('nem todo é eficiente' = 'existe um não eficiente'), não a negação.",
            "b": "ERRADA. 'Nenhum computador é eficiente' é mais forte que a negação; a negação correta é 'todos são eficientes'.",
            "c": "ERRADA. 'Existem computadores eficientes' não nega a original — ambas podem ser verdadeiras simultaneamente.",
            "d": "ERRADA. 'Nem todos não são eficientes' = 'existe algum eficiente', insuficiente para negar a original.",
            "e": "CORRETA. 'Não existe computador não eficiente' = ∀x: eficiente(x) = 'todo computador é eficiente', que é exatamente a negação de 'nem todo é eficiente'.",
        },
    },
    "oficial_2026-1_q05": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["argumentos_validade", "proposicoes_conectivos"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "ERRADA. Adicionar 'q' não permite deduzir 'p' por modus ponens em 'p→(q∨r)' — seria afirmação do consequente.",
            "b": "CORRETA. Premissa 5 = ¬r. Por (2): ¬s. Por (3): ¬t. Por (4): ¬q. Por contrapositiva de (1): ¬(q∨r) → ¬p. Como temos ¬q e ¬r, concluímos ¬p. Argumento válido.",
            "c": "ERRADA. ¬p torna (1) trivialmente satisfeita, mas não há cadeia que conclua 's' a partir do restante.",
            "d": "ERRADA. Com t, por (3) deduz s, por contrapositiva de (2) deduz r, e por (1) só temos q∨r — não força q.",
            "e": "ERRADA. A alternativa (b) é uma combinação válida.",
        },
    },
    "oficial_2026-1_q06": {
        "eixo": "estruturas_dados",
        "subtopicos": ["pilha_fila"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Cálculo passo a passo não chega em 46.",
            "b": "ERRADA. A pilha não fica vazia ao final.",
            "c": "ERRADA. 42 não é o resultado.",
            "d": "CORRETA. Trace: [2,3]→mul→[6]; ,2→[6,2]→add→[8]; ,1→[8,1]→pop→[8]; ,1→[8,1]→pop→[8]; ,3→[8,3]→add→[11]; ,2→[11,2]→mul→[22]; ,3,4→[22,3,4]→add→[22,7]; ,3,4→[22,7,3,4]→pop→[22,7,3]→mul→[22,21]→add→[43].",
            "e": "ERRADA. Os últimos operadores consolidam o resultado em uma única posição.",
        },
    },
    "oficial_2026-1_q07": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "heranca_polimorfismo", "principios_solid"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "CORRETA. Apenas I e II estão corretas. I: descrição precisa do diamond inheritance em C++. II: descrição correta de LSP (pré-condições não restritas, pós-condições não ampliadas).",
            "b": "ERRADA. Inclui III, que confunde coesão (interna ao módulo) com acoplamento (entre módulos). Módulos coesos NÃO exigem alto acoplamento — pelo contrário, alta coesão é compatível com baixo acoplamento.",
            "c": "ERRADA. IV afirma que polimorfismo paramétrico (templates/generics) tem verificação SEMPRE em tempo de execução. Falso: templates C++ são verificados em tempo de COMPILAÇÃO; Java generics também (apesar de type erasure no runtime).",
            "d": "ERRADA. III está incorreta (ver explicação de b).",
            "e": "ERRADA. III e IV estão incorretas.",
        },
    },
    "oficial_2026-1_q08": {
        "eixo": "estruturas_dados",
        "subtopicos": ["listas_encadeadas", "pilha_fila"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. II e IV estão incorretas (ver d e b).",
            "b": "ERRADA. IV afirma acesso direto por índice em pilha em O(1) — pilha só permite acesso ao topo, não a elementos arbitrários.",
            "c": "CORRETA. Apenas I está correta — descrição precisa de lista duplamente encadeada com referências next e prev em cada nó.",
            "d": "ERRADA. II descreve o comportamento LIFO (pilha), não FIFO (fila). Recursão usa pilha de chamadas, não fila.",
            "e": "ERRADA. I está correta.",
        },
    },
    "oficial_2026-1_q09": {
        "eixo": "estruturas_dados",
        "subtopicos": ["hash_tables", "complexidade_assintotica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "CORRETA. I e II estão corretas: hash bem distribuído tem busca O(1) média, e pior caso (todas as chaves colidem) é O(n).",
            "b": "ERRADA. III afirma que endereçamento aberto garante pior caso O(log n) — não há tal garantia teórica; pior caso continua O(n).",
            "c": "ERRADA. IV é falsa: aumentar load factor aumenta colisões e PIORA o desempenho, especialmente em endereçamento aberto.",
            "d": "ERRADA. IV é falsa (ver c).",
            "e": "ERRADA. III e IV são falsas.",
        },
    },
    "oficial_2026-1_q10": {
        "eixo": "programacao",
        "subtopicos": ["memoria_stack_heap", "passagem_parametros", "escopo_visibilidade"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. I diz que 'valor' é alocada no heap — falso. Variáveis globais ficam no segmento de dados estáticos, não no heap (heap é para alocação dinâmica via malloc).",
            "b": "ERRADA. II e III estão corretas (ver d).",
            "c": "ERRADA. I é falsa (escopo global está certo, mas alocação NÃO é heap).",
            "d": "CORRETA. II é verdadeira: 'z' é local em 'soma', vive na stack e é liberada ao retornar. III é verdadeira: 'x' é passado por valor (cópia) e 'y' é ponteiro para 'a' (passagem por referência).",
            "e": "ERRADA. I é falsa (ver a).",
        },
    },
    "oficial_2026-1_q11": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "heranca_polimorfismo", "encapsulamento_abstracao"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. V está incorreta: nem toda linguagem OO suporta herança múltipla (Java não, por exemplo).",
            "b": "ERRADA. I a IV estão corretas.",
            "c": "CORRETA. Apenas V está incorreta — em linguagens como Java, herança múltipla de classes não é permitida; só de interfaces.",
            "d": "ERRADA. Existem 4 corretas (I, II, III, IV), não apenas 1.",
            "e": "ERRADA. São 4 corretas e 1 incorreta, não 3 e 2.",
        },
    },
    "oficial_2026-1_q12": {
        "eixo": "estruturas_dados",
        "subtopicos": ["grafos", "bfs_dfs"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. BFS não vai direto B→C antes de visitar D (D está no mesmo nível de B).",
            "b": "ERRADA. Essa seria DFS começando por D, não BFS alfabético.",
            "c": "CORRETA. BFS partindo de A, ordem alfabética: visita A; expande para B e D (alfa); visita B (vizinhos novos: C); visita D (vizinhos novos: E); visita C; visita E. Ordem: A, B, D, C, E.",
            "d": "ERRADA. C não é vizinho direto de A — não pode ser visitado segundo.",
            "e": "ERRADA. Esta é a ordem de DFS, não BFS — em BFS C e E são visitados depois de todos os vizinhos da raiz.",
        },
    },
    "oficial_2026-1_q13": {
        "eixo": "estruturas_dados",
        "subtopicos": ["ordenacao", "complexidade_assintotica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Bubble Sort é O(n²) no caso médio e pior caso, ineficiente para grandes volumes. O(n) só ocorre no melhor caso (entrada ordenada, com otimização de early exit).",
            "b": "CORRETA. Selection Sort é in-place (troca elementos no próprio vetor, memória auxiliar O(1)) e tem complexidade O(n²) em todos os casos (sempre faz n × n/2 comparações).",
            "c": "ERRADA. Merge Sort NÃO é in-place: requer memória auxiliar O(n) para o vetor de merge.",
            "d": "ERRADA. Insertion Sort é O(n²) no pior caso (não O(n³)) e É in-place.",
            "e": "ERRADA. Heap Sort NÃO é estável (a construção do heap pode reordenar chaves iguais) e sua complexidade é O(n log n), não O(n).",
        },
    },
    "oficial_2026-1_q14": {
        "eixo": "estruturas_dados",
        "subtopicos": ["complexidade_assintotica"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "CORRETA. (1) loop simples → O(n). (2) loop aninhado → O(n²). (3) instrução única → O(1). (4) loop externo n × loop interno que divide k por 2 (log₂n iterações) → O(n log n).",
            "b": "ERRADA. (4) tem loop externo de tamanho n × interno log n, total O(n log n), não O(log n).",
            "c": "ERRADA. (1) é O(n) e (2) é O(n²), inverteu.",
            "d": "ERRADA. (3) é uma instrução constante, O(1), não O(n²).",
            "e": "ERRADA. (2) é O(n²) e (4) é O(n log n), não O(n).",
        },
    },
    "oficial_2026-1_q15": {
        "eixo": "estruturas_dados",
        "subtopicos": ["ordenacao", "complexidade_assintotica"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "ERRADA. III está incorreta (ver d).",
            "b": "ERRADA. I está correta.",
            "c": "CORRETA. I e II estão corretas. I: descrição precisa do partition do Quick Sort com pivô a[lo]. II: a varredura é linear porque cada elemento é visitado no máximo uma vez pelos índices i e j que se aproximam.",
            "d": "ERRADA. III está errada: o while usa less(...) que é estritamente menor; quando a chave é IGUAL a a[lo], less retorna false e a varredura PARA, não continua.",
            "e": "ERRADA. II também está correta (varredura linear).",
        },
    },
    "oficial_2026-1_q16": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "paradigma_funcional", "paradigma_imperativo"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. II e IV também estão corretas.",
            "b": "ERRADA. I também está correta.",
            "c": "ERRADA. III também está correta.",
            "d": "CORRETA. Todas as 4 afirmações são definições padrão e válidas: I (OO), II (funcional), III (procedural como subtipo de imperativa) e IV (multiparadigma).",
            "e": "ERRADA. Todas estão corretas.",
        },
    },
    "oficial_2026-1_q17": {
        "eixo": "programacao",
        "subtopicos": ["structs_arrays", "trace_de_execucao"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Trace correto dá 21, não 18.",
            "b": "CORRETA. Trace: i=0 → v[0].x + v[2].y = 1 + 6 = 7. i=1 → v[1].x + v[1].y = 3 + 4 = 7. i=2 → v[2].x + v[0].y = 5 + 2 = 7. Soma = 7+7+7 = 21.",
            "c": "ERRADA. Resultado é 21.",
            "d": "ERRADA. Resultado é 21.",
            "e": "ERRADA. Resultado é 21.",
        },
    },
    "oficial_2026-1_q18": {
        "eixo": "programacao",
        "subtopicos": ["leitura_de_codigo", "structs_arrays"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Usa apenas X[i][0] * W[0]; ignora bias b e demais features W[1..n-1].",
            "b": "ERRADA. Soma X[i][j] + W[j] em vez de multiplicar; também esquece o bias b.",
            "c": "CORRETA. Implementação clássica do forward pass: para cada amostra i, inicia z com bias b, soma W[j]*X[i][j] para todas as features, e aplica função degrau (z>=0 → 1, senão 0).",
            "d": "ERRADA. Loop está em j (feature) em vez de i (amostra); produz tamanho errado de saída.",
            "e": "ERRADA. Ignora completamente os pesos e features, retorna o mesmo valor para todas as amostras.",
        },
    },
    "oficial_2026-1_q19": {
        "eixo": "estruturas_dados",
        "subtopicos": ["arvores_bst", "complexidade_assintotica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. I está incorreta (ver d).",
            "b": "CORRETA. II e III corretas. A figura mostra uma BST (árvore binária de busca), não uma árvore B. II: busca/inserção em BST balanceada são O(log n). III: BST degenera para lista (altura n) quando inserções vêm em ordem crescente ou decrescente, perdendo a vantagem logarítmica.",
            "c": "ERRADA. II também está correta.",
            "d": "ERRADA. I afirma que a figura é uma 'árvore B' (estrutura de m chaves por nó, usada em sistemas de arquivos), mas a figura é claramente uma BST (árvore binária comum); além disso, m ≥ 1 não é a definição clássica de árvore B (geralmente m ≥ 2).",
            "e": "ERRADA. II e III estão corretas.",
        },
    },
    "oficial_2026-1_q20": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "heranca_polimorfismo"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "CORRETA. I, III e IV são verdadeiras. I: subclasses herdam atributos públicos/protegidos da superclasse. III: sobrescrita do método falar() é o que o pseudocódigo declara. IV: nome é definido em Animal e herdado, evitando duplicação.",
            "b": "ERRADA. II inverte a relação (LSP diz o contrário) e V inverte hierarquia (Animal é superclasse, não subclasse).",
            "c": "ERRADA. V está incorreta — Animal é superclasse, não subclasse.",
            "d": "ERRADA. II é falsa — pelo princípio de substituição de Liskov, um Cachorro pode substituir um Animal, mas NÃO o contrário.",
            "e": "ERRADA. V inverte a hierarquia de herança.",
        },
    },
}


# =========================================================================
# Prova 2025/2
# =========================================================================
EXPL_2025_2: dict[str, ExplicacaoQuestao] = {
    "oficial_2025-2_q01": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["problemas_associacao", "argumentos_validade"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "CORRETA. Dedução: Jane é noiva de Claudio (almoça em casa, não no refeitório) → não é secretária de Maurício; Ana sobe ao andar de Maurício e almoça com a secretária dele → Ana não é secretária de Maurício; logo a secretária de Maurício é Cecília. Jorge mandou a secretária descer ao arquiteto → Jorge não é advogado (térreo) nem arquiteto. Maurício não pode ser advogado (Ana sobe pra ele), então Maurício = arquiteto, Jorge = médico e Claudio = advogado. Jane (que não é de Maurício nem casaria com chefe) = Jorge; Ana = Claudio.",
            "b": "ERRADA. Maurício é arquiteto, não médico.",
            "c": "ERRADA. Jane é secretária de Jorge, não de Maurício; e Maurício é arquiteto, não advogado.",
            "d": "ERRADA. Jorge é médico (não arquiteto); Cecília é secretária de Maurício (não de Claudio).",
            "e": "ERRADA. A alternativa (a) está integralmente correta.",
        },
    },
    "oficial_2025-2_q02": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["argumentos_validade", "proposicoes_conectivos"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Modus tollens em P1 (Victória não foi à praia) força ¬vôlei ∧ ¬videogame — Ana Paula NÃO jogou vôlei.",
            "b": "CORRETA. De P1 + P2 (modus tollens): ¬(vôlei ∨ videogame) = ¬vôlei ∧ ¬videogame. Por P3, se fosse sábado então vôlei — contradição com ¬vôlei, então ¬sábado.",
            "c": "ERRADA. P1 + P2 negam o antecedente: nem vôlei nem videogame.",
            "d": "ERRADA. ¬sábado e ¬videogame, ambos invertidos.",
            "e": "ERRADA. ¬sábado está certo, mas Ana Paula não jogou vôlei.",
        },
    },
    "oficial_2025-2_q03": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["quantificadores", "equivalencia_negacao"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "CORRETA. Original: ∃u(univ(u) ∧ ∀c(curso(c,u) → alunos(c)≥100)). Negação: ∀u(univ(u) → ∃c(curso(c,u) ∧ alunos(c)<100)). Em PT: 'Em todas as universidades existe pelo menos um curso com no máximo 99 alunos'.",
            "b": "ERRADA. 'No máximo uma universidade' e '101 alunos' distorcem completamente os quantificadores.",
            "c": "ERRADA. 'Há uma universidade' nega apenas existencial, não cobre 'para todas'.",
            "d": "ERRADA. Mantém 'pelo menos 100' — não nega o número.",
            "e": "ERRADA. Construção 'existe nenhuma' é confusa e logicamente diferente da negação correta.",
        },
    },
    "oficial_2025-2_q04": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["equivalencia_negacao", "proposicoes_conectivos"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Cobre apenas um caso da negação; não inclui 'ambos não viajaram'.",
            "b": "ERRADA. Cobre apenas um caso da negação.",
            "c": "ERRADA. 'Marcos ou Heide não viajou' inclui o caso em que apenas um viajou, justamente o que a original afirma.",
            "d": "CORRETA. 'Exatamente um viajou' é XOR: (M ∧ ¬H) ∨ (¬M ∧ H). Negar XOR dá equivalência: M ↔ H = (M ∧ H) ∨ (¬M ∧ ¬H) = 'ambos viajaram ou ambos não viajaram'.",
            "e": "ERRADA. 'Pelo menos um viajou' inclui o caso em que exatamente um viajou (a própria original).",
        },
    },
    "oficial_2025-2_q05": {
        "eixo": "raciocinio_logico",
        "subtopicos": ["argumentos_validade"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "Questão ANULADA pela banca. Não há conclusão única dedutível das premissas: de P3 (Ana saiu) e P2 (contrapositiva) deduz-se cinema, mas P1 com cinema verdadeiro não força lógica nem livros — múltiplas atribuições satisfazem todas as premissas.",
            "b": "Questão ANULADA pela banca (ver explicação em (a)).",
            "c": "Questão ANULADA pela banca (ver explicação em (a)).",
            "d": "Questão ANULADA pela banca (ver explicação em (a)).",
            "e": "Questão ANULADA pela banca (ver explicação em (a)).",
        },
    },
    "oficial_2025-2_q06": {
        "eixo": "estruturas_dados",
        "subtopicos": ["complexidade_assintotica"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. Não há divisão por 2 — nenhum loop é logarítmico.",
            "b": "ERRADA. Há dois loops aninhados sobre n; não é log n.",
            "c": "ERRADA. Há dois loops aninhados, não um.",
            "d": "CORRETA. Loop externo de (n-1) iterações × loop interno de n iterações ≈ n² operações, logo O(n²).",
            "e": "ERRADA. A alternativa (d) é correta.",
        },
    },
    "oficial_2025-2_q07": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "heranca_polimorfismo", "encapsulamento_abstracao"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Apesar de I e IV serem corretas, III também é.",
            "b": "ERRADA. II é falsa (ver e).",
            "c": "ERRADA. II é falsa.",
            "d": "ERRADA. II é falsa.",
            "e": "CORRETA. I, III e IV verdadeiras. II é falsa porque polimorfismo paramétrico (templates/generics) e polimorfismo ad-hoc (sobrecarga) não dependem de herança — apenas o polimorfismo de subtipo depende.",
        },
    },
    "oficial_2025-2_q08": {
        "eixo": "paradigmas",
        "subtopicos": ["tipagem_estatica_dinamica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. IV também é correta no sentido estrito.",
            "b": "ERRADA. I é falsa: tipagem FORTE evita conversões automáticas implícitas (isso é típico de tipagem fraca).",
            "c": "CORRETA. II (tipagem dinâmica permite variável de tipos diferentes), III (estática detecta erros antes da execução) e IV (estática permite otimizações em tempo de compilação; dinâmica só pode otimizar em runtime via JIT, não 'na compilação') estão corretas.",
            "d": "ERRADA. I é falsa.",
            "e": "ERRADA. I é falsa.",
        },
    },
    "oficial_2025-2_q09": {
        "eixo": "estruturas_dados",
        "subtopicos": ["listas_encadeadas", "pilha_fila", "arvores_bst"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "ERRADA. V também é considerada verdadeira pela banca.",
            "b": "ERRADA. III e IV são falsas (ver d e e).",
            "c": "ERRADA. I é falsa: BST insere por valor (mantendo propriedade), não em posição arbitrária.",
            "d": "ERRADA. I e III são falsas (em lista simples não há ponteiro para o anterior; a remoção altera o NEXT do nó anterior).",
            "e": "CORRETA (segundo gabarito oficial). II é claramente verdadeira (LIFO). V é controversa: numa lista circular simples padrão, o primeiro só aponta para o segundo (apenas next); o gabarito interpreta 'aponta para o último' via percurso circular completo. As demais (I, III, IV) são falsas.",
        },
    },
    "oficial_2025-2_q10": {
        "eixo": "estruturas_dados",
        "subtopicos": ["arvores_bst", "complexidade_assintotica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. iv também é correta.",
            "b": "ERRADA. i é falsa: BST é binária (no máximo 2 filhos), não 'qualquer número'.",
            "c": "ERRADA. iii é falsa: BST tradicional NÃO é auto-balanceada (só variantes como AVL e Red-Black são).",
            "d": "CORRETA. ii (propriedade de ordenação: esquerda menor, direita maior) e iv (degeneração em lista com inserções ordenadas, levando à busca O(n)) são as únicas verdadeiras.",
            "e": "ERRADA. i e iii são falsas.",
        },
    },
    "oficial_2025-2_q11": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "encapsulamento_abstracao"],
        "dificuldade": "dificil",
        "explicacoes": {
            "a": "ERRADA. i é falsa: definir a struct no .h EXPÕE seus campos para qualquer cliente, QUEBRANDO o encapsulamento.",
            "b": "ERRADA. iii é falsa: encapsulamento total em C é possível via tipos opacos (forward declaration no .h e definição no .c).",
            "c": "CORRETA. Apenas iv está correta: TADs opacos expõem apenas o ponteiro (tipo incompleto) e exigem que o cliente use funções getter/setter implementadas no .c, garantindo encapsulamento total.",
            "d": "ERRADA. i é falsa (struct no .h quebra encapsulamento).",
            "e": "ERRADA. iv é correta (descreve o padrão de TAD opaco em C).",
        },
    },
    "oficial_2025-2_q12": {
        "eixo": "programacao",
        "subtopicos": ["ponteiros_referencias", "passagem_parametros"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. C permite múltiplos parâmetros por ponteiro sem restrição alguma.",
            "b": "ERRADA. Justamente passar por ponteiro PERMITE atualizar o valor original; é o objetivo.",
            "c": "ERRADA. Ponteiros caracterizam passagem por REFERÊNCIA, não por cópia. Atualizações via *ptr propagam para fora.",
            "d": "CORRETA. char* e int* são ponteiros para os respectivos tipos; o conteúdo apontado pode ser modificado dentro da função e as mudanças permanecem visíveis para o chamador.",
            "e": "ERRADA. Em C, atualizações via ponteiros não dependem de return — modificam diretamente a memória apontada.",
        },
    },
    "oficial_2025-2_q13": {
        "eixo": "estruturas_dados",
        "subtopicos": ["ordenacao", "heaps", "complexidade_assintotica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. heapify é O(log n), não quadrático. A construção inicial do heap é O(n) e a ordenação total é O(n log n).",
            "b": "ERRADA. Heap Sort é O(n log n) em TODOS os casos — nunca cúbico.",
            "c": "ERRADA. Heap Sort não é variação do Bubble Sort; usa heap binário, não comparações adjacentes.",
            "d": "ERRADA. Heap Sort não é variação do Merge Sort; não usa operações de merge.",
            "e": "CORRETA. Descrição precisa: heap binário (fila de prioridades), manutenção da propriedade de heap a cada iteração, extração do extremo para a posição final.",
        },
    },
    "oficial_2025-2_q14": {
        "eixo": "estruturas_dados",
        "subtopicos": ["listas_encadeadas", "complexidade_assintotica"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "CORRETA (esta é a INCORRETA pedida). Busca em lista encadeada é O(n) no pior caso — precisa percorrer nó a nó.",
            "b": "ERRADA (como afirmação é correta; logo não é a 'incorreta' pedida). Busca é de fato O(n).",
            "c": "ERRADA (como afirmação é correta). Cada nó armazena valor + ponteiro pro próximo (encadeamento simples).",
            "d": "ERRADA (como afirmação é correta). Inserção/remoção em posição conhecida (com referência ao nó) é O(1).",
            "e": "ERRADA (como afirmação é correta). Lista encadeada não permite acesso por índice em O(1) — necessário percorrer.",
        },
    },
    "oficial_2025-2_q15": {
        "eixo": "programacao",
        "subtopicos": ["leitura_de_codigo", "trace_de_execucao"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "CORRETA. Loops aninhados com comparação `arr[j] > arr[j+1]` e swap caracterizam Bubble Sort. Como faz n×n iterações no pior caso e ordena ascendente (troca quando o atual é MAIOR), o resultado é ordem crescente em O(n²).",
            "b": "ERRADA. A condição `arr[j] > arr[j+1]` empurra o maior para o final, gerando ordem CRESCENTE, não decrescente.",
            "c": "ERRADA. O código apenas troca elementos; nunca atribui o mesmo valor a posições.",
            "d": "ERRADA. Ambos os loops têm limites finitos baseados em n e i; nenhum loop é infinito.",
            "e": "ERRADA. Não é uma reversão; é uma ordenação que depende dos valores iniciais.",
        },
    },
    "oficial_2025-2_q16": {
        "eixo": "programacao",
        "subtopicos": ["leitura_de_codigo"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. Não há nenhuma operação de troca ou comparação para ordenação.",
            "b": "ERRADA. Retorna na primeira ocorrência; não conta.",
            "c": "CORRETA. Busca linear clássica: itera o vetor, retorna o índice da primeira ocorrência do valor procurado, ou -1 se não encontrar.",
            "d": "ERRADA. Não há atribuição a posições do vetor.",
            "e": "ERRADA. Não há comparação para encontrar máximo.",
        },
    },
    "oficial_2025-2_q17": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "encapsulamento_abstracao", "heranca_polimorfismo"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. II também está correta.",
            "b": "ERRADA. IV é falsa.",
            "c": "CORRETA. I (encapsulamento), II (herança) e III (polimorfismo via override/overload) são definições corretas. IV é falsa: abstração refere-se a expor apenas o essencial de um objeto, escondendo detalhes — NÃO 'múltiplos tipos para um mesmo atributo' (isso seria polimorfismo paramétrico ou union types).",
            "d": "ERRADA. IV é falsa.",
            "e": "ERRADA. IV é falsa.",
        },
    },
    "oficial_2025-2_q18": {
        "eixo": "estruturas_dados",
        "subtopicos": ["ordenacao", "complexidade_assintotica"],
        "dificuldade": "facil",
        "explicacoes": {
            "a": "ERRADA. Merge Sort não é O(n²); é O(n log n) em todos os casos.",
            "b": "CORRETA. Merge Sort tem complexidade O(n log n) em todos os casos (divisão recursiva é log n níveis × n para o merge), e é ESTÁVEL (preserva ordem relativa de elementos iguais quando o merge usa <= ).",
            "c": "ERRADA. Merge Sort é estável, não instável.",
            "d": "ERRADA. Merge Sort não é O(n²).",
            "e": "ERRADA. Merge Sort não é O(log n).",
        },
    },
    "oficial_2025-2_q19": {
        "eixo": "paradigmas",
        "subtopicos": ["paradigma_oo", "encapsulamento_abstracao", "heranca_polimorfismo"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA (como afirmação é correta — encapsulamento promove sim modularidade).",
            "b": "ERRADA (como afirmação é correta — herança permite estender, sobrescrever).",
            "c": "CORRETA (esta é a INCORRETA pedida). Herança AVOIDS duplicação de código, NÃO leva a ela; é justamente seu propósito. A subclasse herda os métodos não precisando reimplementá-los.",
            "d": "ERRADA (como afirmação é correta — private/protected são modificadores de acesso usados para encapsulamento).",
            "e": "ERRADA (como afirmação é correta — encapsulamento isola a lógica interna por trás da interface pública).",
        },
    },
    "oficial_2025-2_q20": {
        "eixo": "estruturas_dados",
        "subtopicos": ["ordenacao", "complexidade_assintotica"],
        "dificuldade": "medio",
        "explicacoes": {
            "a": "ERRADA. Quick Sort tem pior caso O(n²) (não O(n log n)) e NÃO é estável.",
            "b": "ERRADA. Merge Sort é estável e O(n log n), mas NÃO é in-place (requer O(n) de memória auxiliar).",
            "c": "CORRETA. Heap Sort garante O(n log n) no pior caso, é in-place (memória auxiliar O(1)) e é instável (heap reordena chaves iguais arbitrariamente).",
            "d": "ERRADA. Insertion Sort é O(n²) no pior caso, não O(n log n).",
            "e": "ERRADA. Bubble Sort é O(n²) — ineficiente para grandes volumes.",
        },
    },
}


# Mapa consolidado (vai crescendo a cada batch concluído: A1, A2, A3)
EXPLICACOES: dict[str, ExplicacaoQuestao] = {
    **EXPL_2026_1,
    **EXPL_2025_2,
    # **EXPL_2025_1,  # virá na Fase A3
}


def _aplicar(q_id: str, dados: ExplicacaoQuestao, bank) -> bool:
    """Atualiza a questão no banco com os dados fornecidos. Retorna True se aplicou."""
    for i, q in enumerate(bank.questions):
        if q.id == q_id:
            # Atualiza explicações por alternativa, preservando texto original
            novas_alts = [
                Alternativa(
                    chave=a.chave,
                    texto=a.texto,
                    explicacao=dados["explicacoes"].get(a.chave, a.explicacao),
                )
                for a in q.alternativas
            ]
            q.alternativas = novas_alts
            q.eixo = dados["eixo"]  # type: ignore[assignment]
            q.subtopicos = list(dados["subtopicos"])
            q.dificuldade = Dificuldade(dados["dificuldade"])
            q.validacao = ValidacaoResult(
                validado=True,
                confianca=0.9,
                raciocinio="Validada manualmente pelo autor; gabarito conferido e explicações redigidas por alternativa.",
                flags=q.validacao.flags or [],
                modelo="curadoria_manual",
                data=NOW,
            )
            bank.questions[i] = q
            return True
    return False


def main() -> None:
    bank = load_bank()
    aplicadas = 0
    nao_encontradas: list[str] = []
    for qid, dados in EXPLICACOES.items():
        if _aplicar(qid, dados, bank):
            aplicadas += 1
        else:
            nao_encontradas.append(qid)

    save_bank(bank)
    print(f"Explicações aplicadas: {aplicadas} / {len(EXPLICACOES)}")
    if nao_encontradas:
        print("Questões não encontradas no banco:")
        for q in nao_encontradas:
            print(f"  - {q}")
    print(f"\nResumo do banco:")
    print(f"  total: {len(bank.questions)}")
    com_expl = sum(
        1 for q in bank.questions if any(a.explicacao for a in q.alternativas)
    )
    print(f"  com explicações: {com_expl}")
    print(f"  validadas: {sum(1 for q in bank.questions if q.validacao.validado)}")


if __name__ == "__main__":
    main()
