"""Seed de questões geradas manualmente, cobrindo os 4 eixos do edital PPGI.

Cada questão aqui foi escrita e revisada com cuidado e já vem com:
- gabarito definido
- explicação por alternativa
- subtopicos
- dificuldade
- validacao com confianca 0.9 (foi criada com revisão direta)

Rode: python -m src.data.seed_geradas
"""
from __future__ import annotations

from datetime import datetime, timezone

from .load import add_or_update, load_bank, save_bank
from .schema import Alternativa, Dificuldade, Origem, Question, ValidacaoResult

NOW = datetime.now(timezone.utc).isoformat()
VAL_OK = ValidacaoResult(
    validado=True,
    confianca=0.9,
    raciocinio="Validada na criação (autor revisou gabarito e explicações).",
    flags=[],
    modelo="curadoria_manual",
    data=NOW,
)


def _q(
    n: int,
    eixo: str,
    sub: list[str],
    dif: str,
    enunciado: str,
    alts: list[tuple[str, str, str]],
    gabarito: str,
) -> Question:
    return Question(
        id=f"gerada_{n:04d}",
        origem=Origem.gerada_validada,
        eixo=eixo,  # type: ignore[arg-type]
        subtopicos=sub,
        ano=None,
        numero_na_prova=None,
        enunciado=enunciado.strip(),
        alternativas=[
            Alternativa(chave=k, texto=t.strip(), explicacao=e.strip())  # type: ignore[arg-type]
            for k, t, e in alts
        ],
        gabarito=gabarito,  # type: ignore[arg-type]
        dificuldade=Dificuldade(dif),
        validacao=VAL_OK,
    )


QUESTOES = [
    # === Raciocínio Lógico (3) ===
    _q(
        1, "raciocinio_logico", ["equivalencia_negacao", "quantificadores"], "medio",
        'Considere a proposição: "Todo aluno do PPGI gosta de pelo menos uma disciplina." '
        "Qual das alternativas representa corretamente a NEGAÇÃO desta proposição?",
        [
            ("a", "Nenhum aluno do PPGI gosta de pelo menos uma disciplina.",
             "ERRADA. Essa é mais forte que a negação; afirma a inexistência total."),
            ("b", "Existe um aluno do PPGI que não gosta de nenhuma disciplina.",
             "CORRETA. Negar 'para todo x, existe y P(x,y)' é 'existe x tal que para todo y, ¬P(x,y)'."),
            ("c", "Todo aluno do PPGI gosta de todas as disciplinas.",
             "ERRADA. Essa é uma afirmação distinta, mais forte que a original — não é a negação."),
            ("d", "Existe um aluno do PPGI que gosta de todas as disciplinas.",
             "ERRADA. Refere-se à mesma classe quantificada, mas inverte o quantificador interno errado."),
            ("e", "Nenhuma das alternativas anteriores.",
             "ERRADA. A alternativa (b) corresponde à negação correta."),
        ],
        "b",
    ),
    _q(
        2, "raciocinio_logico", ["argumentos_validade", "proposicoes_conectivos"], "medio",
        "Considere as premissas verdadeiras:\n"
        "I. Se chove, então a rua fica molhada.\n"
        "II. A rua não está molhada.\n"
        "Qual conclusão é logicamente válida?",
        [
            ("a", "Não choveu.",
             "CORRETA. Modus tollens: (p→q) e ¬q implicam ¬p."),
            ("b", "Choveu.",
             "ERRADA. As premissas não permitem afirmar p."),
            ("c", "A rua sempre fica molhada quando chove e em outros casos.",
             "ERRADA. Afirmação não suportada pelas premissas."),
            ("d", "Pode ter chovido, mas não há como saber.",
             "ERRADA. Modus tollens é dedutivo: a conclusão ¬p é certa, não incerta."),
            ("e", "Nenhuma das alternativas anteriores.",
             "ERRADA. (a) é a aplicação direta de modus tollens."),
        ],
        "a",
    ),
    _q(
        3, "raciocinio_logico", ["tabela_verdade"], "facil",
        "Para quais valores de p e q a expressão (p → q) ∧ ¬q é verdadeira?",
        [
            ("a", "p verdadeiro, q verdadeiro.",
             "ERRADA. ¬q é falso, então a conjunção é falsa."),
            ("b", "p verdadeiro, q falso.",
             "ERRADA. p→q é falso quando p=V e q=F, então a conjunção é falsa."),
            ("c", "p falso, q verdadeiro.",
             "ERRADA. ¬q é falso (q=V), então a conjunção é falsa."),
            ("d", "p falso, q falso.",
             "CORRETA. p→q é verdadeiro (premissa falsa), ¬q é verdadeiro, e a conjunção V∧V=V."),
            ("e", "A expressão é uma contradição (sempre falsa).",
             "ERRADA. Como mostrado em (d), existe atribuição que a torna verdadeira."),
        ],
        "d",
    ),
    # === Programação (3) ===
    _q(
        4, "programacao", ["ponteiros_referencias", "passagem_parametros"], "medio",
        "Considere o trecho em C:\n"
        "```c\n"
        "void f(int a, int *b) { a = a + 1; *b = *b + 1; }\n"
        "int main() { int x = 5, y = 5; f(x, &y); printf(\"%d %d\", x, y); }\n"
        "```\n"
        "Qual a saída do programa?",
        [
            ("a", "5 5",
             "ERRADA. y é modificado via ponteiro dentro de f."),
            ("b", "6 6",
             "ERRADA. x é passado por valor — não é modificado fora de f."),
            ("c", "5 6",
             "CORRETA. x passa por cópia (continua 5); y passa por referência via &y e é incrementado para 6."),
            ("d", "6 5",
             "ERRADA. Inverte qual passou por valor e qual por referência."),
            ("e", "Erro de compilação.",
             "ERRADA. O código compila e executa normalmente."),
        ],
        "c",
    ),
    _q(
        5, "programacao", ["trace_de_execucao", "structs_arrays"], "medio",
        "Considere o trecho em C:\n"
        "```c\n"
        "int v[5] = {2, 4, 6, 8, 10};\n"
        "int *p = v + 2;\n"
        "printf(\"%d\", *(p - 1) + p[2]);\n"
        "```\n"
        "Qual a saída?",
        [
            ("a", "8",
             "ERRADA. Conta apenas um dos termos da soma."),
            ("b", "10",
             "ERRADA. Não confere com a aritmética de ponteiros."),
            ("c", "12",
             "ERRADA. Confere v[1]=4 com v[2]=6: 4+6 não dá 12."),
            ("d", "14",
             "CORRETA. p aponta para v[2]=6. *(p-1)=v[1]=4. p[2]=v[4]=10. Soma: 4+10=14."),
            ("e", "16",
             "ERRADA. Confunde p[2] com v[2]+2."),
        ],
        "d",
    ),
    _q(
        6, "programacao", ["memoria_stack_heap", "escopo_visibilidade"], "facil",
        "Sobre alocação de memória em C, assinale a alternativa CORRETA:",
        [
            ("a", "Variáveis locais declaradas dentro de uma função são alocadas no heap.",
             "ERRADA. Variáveis locais (automáticas) vão na pilha (stack), não no heap."),
            ("b", "Memória alocada por malloc() é liberada automaticamente ao final da função.",
             "ERRADA. malloc() vai no heap e precisa de free() explícito."),
            ("c", "Variáveis globais são alocadas em uma área estática e existem durante toda a execução do programa.",
             "CORRETA. Variáveis globais e estáticas ficam no segmento de dados estáticos, com tempo de vida igual ao programa."),
            ("d", "O escopo de uma variável local inclui todas as funções chamadas a partir dela.",
             "ERRADA. Escopo léxico em C: a variável só é visível dentro da função onde foi declarada."),
            ("e", "A pilha (stack) é o local onde são armazenados arquivos abertos com fopen().",
             "ERRADA. fopen() retorna ponteiro para estrutura FILE alocada normalmente no heap."),
        ],
        "c",
    ),
    # === Paradigmas (3) ===
    _q(
        7, "paradigmas", ["paradigma_oo", "heranca_polimorfismo"], "medio",
        "Sobre os pilares da Programação Orientada a Objetos, qual afirmação é FALSA?",
        [
            ("a", "Encapsulamento esconde detalhes internos de uma classe, expondo apenas uma interface controlada.",
             "VERDADEIRA. Definição correta de encapsulamento."),
            ("b", "Polimorfismo permite que um mesmo nome de método tenha comportamentos diferentes em classes distintas.",
             "VERDADEIRA. Definição correta — polimorfismo por sobrescrita ou paramétrico."),
            ("c", "Herança permite reutilização de código ao derivar uma classe a partir de outra.",
             "VERDADEIRA. Definição correta de herança."),
            ("d", "Abstração refere-se à criação de instâncias múltiplas de uma mesma classe.",
             "FALSA — esta é a resposta. Abstração é destacar o essencial e esconder o irrelevante. "
             "Criar instâncias é instanciação, não abstração."),
            ("e", "Em linguagens com herança simples, uma classe herda atributos e métodos de exatamente uma classe-pai.",
             "VERDADEIRA. Definição correta de herança simples (ex: Java, com exceção de interfaces)."),
        ],
        "d",
    ),
    _q(
        8, "paradigmas", ["paradigma_funcional"], "facil",
        "Qual das características abaixo é típica do paradigma FUNCIONAL?",
        [
            ("a", "Uso intenso de variáveis mutáveis para acumular estado.",
             "ERRADA. Funcional EVITA mutação — característica imperativa."),
            ("b", "Funções como cidadãos de primeira classe, podendo ser passadas como argumento.",
             "CORRETA. Funções de primeira ordem são a marca registrada do paradigma funcional."),
            ("c", "Organização do código em torno de classes e objetos.",
             "ERRADA. Característica do paradigma OO, não funcional."),
            ("d", "Uso de fatos e regras para inferir conclusões via unificação.",
             "ERRADA. Característica do paradigma lógico (ex: Prolog)."),
            ("e", "Loops imperativos com mudança de variável de controle.",
             "ERRADA. Funcional prefere recursão e funções de ordem superior (map/filter/fold)."),
        ],
        "b",
    ),
    _q(
        9, "paradigmas", ["principios_solid"], "dificil",
        "O princípio da substituição de Liskov (LSP) afirma que:",
        [
            ("a", "Toda função deve ter uma única responsabilidade.",
             "ERRADA. Esse é o Single Responsibility Principle (SRP)."),
            ("b", "Objetos de uma subclasse devem poder substituir objetos da superclasse sem alterar o "
             "funcionamento correto do programa.",
             "CORRETA. Definição clássica de LSP — subtipos devem honrar o contrato do tipo base."),
            ("c", "Módulos de alto nível não devem depender de módulos de baixo nível, mas ambos de abstrações.",
             "ERRADA. Esse é o Dependency Inversion Principle (DIP)."),
            ("d", "Classes devem estar abertas para extensão e fechadas para modificação.",
             "ERRADA. Esse é o Open/Closed Principle (OCP)."),
            ("e", "Interfaces devem ser específicas e enxutas, em vez de monolíticas.",
             "ERRADA. Esse é o Interface Segregation Principle (ISP)."),
        ],
        "b",
    ),
    # === Estruturas de Dados (3) ===
    _q(
        10, "estruturas_dados", ["pilha_fila"], "facil",
        "Considere uma pilha inicialmente vazia. São aplicadas as operações: "
        "push(1), push(2), push(3), pop(), push(4), pop(), push(5). "
        "Qual o conteúdo da pilha do fundo para o topo?",
        [
            ("a", "[1, 5]",
             "ERRADA. Pula o elemento 2, que nunca é removido pelos pops."),
            ("b", "[1, 2, 5]",
             "CORRETA. Trace passo a passo: push(1)→[1]; push(2)→[1,2]; push(3)→[1,2,3]; "
             "pop()→[1,2]; push(4)→[1,2,4]; pop()→[1,2]; push(5)→[1,2,5]."),
            ("c", "[2, 5]",
             "ERRADA. O elemento 1 está no fundo e nunca é removido."),
            ("d", "[1, 2, 3, 4, 5]",
             "ERRADA. Ignora as duas operações pop()."),
            ("e", "Pilha vazia.",
             "ERRADA. Foram 5 pushes e apenas 2 pops, sobram 3 elementos."),
        ],
        "b",
    ),
    _q(
        11, "estruturas_dados", ["complexidade_assintotica", "ordenacao"], "medio",
        "Sobre algoritmos de ordenação, assinale a alternativa CORRETA:",
        [
            ("a", "Merge Sort tem complexidade O(n²) no pior caso.",
             "ERRADA. Merge Sort é O(n log n) sempre — pior, médio e melhor caso."),
            ("b", "Quick Sort é estável.",
             "ERRADA. A implementação clássica do Quick Sort não é estável."),
            ("c", "Bubble Sort tem complexidade O(n) no melhor caso (entrada já ordenada, com otimização).",
             "CORRETA. Com flag de troca, Bubble Sort detecta entrada ordenada e termina em uma passada O(n)."),
            ("d", "Heap Sort exige memória auxiliar O(n).",
             "ERRADA. Heap Sort é in-place — memória auxiliar O(1)."),
            ("e", "Insertion Sort tem complexidade O(n log n) no pior caso.",
             "ERRADA. Insertion Sort é O(n²) no pior e médio caso; O(n) só no melhor caso."),
        ],
        "c",
    ),
    _q(
        12, "estruturas_dados", ["arvores_bst", "complexidade_assintotica"], "medio",
        "Em uma árvore binária de busca (BST) com n nós, qual a complexidade no PIOR caso para a operação de busca?",
        [
            ("a", "O(1)",
             "ERRADA. Só seria O(1) se o elemento procurado fosse sempre a raiz."),
            ("b", "O(log n)",
             "ERRADA. O(log n) é o caso médio (ou pior caso se a árvore for balanceada). "
             "BST não-balanceada degenera no pior caso."),
            ("c", "O(n)",
             "CORRETA. No pior caso, inserções ordenadas criam uma 'árvore-lista' de altura n, "
             "tornando a busca linear. Por isso existem variantes balanceadas (AVL, Red-Black)."),
            ("d", "O(n log n)",
             "ERRADA. Essa é a complexidade de algoritmos de ordenação eficientes."),
            ("e", "O(n²)",
             "ERRADA. Busca em BST nunca chega a O(n²) — uma única descida na árvore percorre no máximo n nós."),
        ],
        "c",
    ),
]


def main() -> None:
    bank = load_bank()
    added = 0
    for q in QUESTOES:
        before = len(bank.questions)
        bank = add_or_update(bank, q)
        if len(bank.questions) > before:
            added += 1
    save_bank(bank)
    print(f"Seed: {added} novas questões adicionadas, {len(QUESTOES) - added} atualizadas.")
    print(f"Total no banco: {len(bank.questions)}")


if __name__ == "__main__":
    main()
