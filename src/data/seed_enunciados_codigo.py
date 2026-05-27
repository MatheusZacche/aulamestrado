"""Reescreve enunciados de questões oficiais com BLOCOS DE CÓDIGO C,
preservando indentação correta e usando aspas retas (necessárias em C).

Motivo: o parser PDF (pdfplumber) extrai texto linha-a-linha SEM preservar
indentação, e o PDF original usa aspas curvas tipográficas (" ") que não
são válidas em C. Resultado: código sai chapado à esquerda e com aspas que
o leitor não reconhece como código compilável.

Rodar: python -m src.data.seed_enunciados_codigo

Idempotente. Roda depois de parse_exam e seed_oficiais_explicacoes.
"""
from __future__ import annotations

from .load import load_bank, save_bank


# Mapa de id → (enunciado_reescrito). O enunciado segue o estilo:
#   1. Parágrafo introdutório em português
#   2. Bloco de código em ```c ... ``` com indentação correta
#   3. Pergunta final, se houver
ENUNCIADOS: dict[str, str] = {
    # ============================================================
    # Prova 2026/1
    # ============================================================
    "oficial_2026-1_q10": """\
Analise o seguinte trecho de código escrito em C:

```c
int valor;

int soma(int x, int *y) {
    int z = x + *y;
    return z;
}

int main() {
    valor = 10;
    int a = 20;
    soma(valor, &a);
    return 0;
}
```

Avalie as seguintes afirmativas:

I. A variável `valor` é alocada na memória heap e possui escopo global.
II. A variável `z` é alocada na pilha (stack) e será liberada da memória assim que a função `soma` encerrar a sua execução.
III. Na função `soma`, um parâmetro é passado por cópia e outro por referência de memória.

É correto afirmar que:""",

    "oficial_2026-1_q15": """\
Considere o trecho de código a seguir, escrito em linguagem C:

```c
int partition(Item *a, int lo, int hi) {
    int i = lo, j = hi + 1;
    Item aux, v = a[lo];
    while (1) {
        while (less(a[++i], v))
            if (i == hi) break;
        while (less(v, a[--j]))
            if (j == lo) break;
        if (i >= j) break;
        swap(&a[i], &a[j]);
    }
    swap(&a[lo], &a[j]);
    return j;
}
```

Considere que:
- A função `less(x, y)` retorna verdadeiro se `x` for menor que `y`.
- A função `swap(x, y)` realiza a troca dos valores de duas variáveis do tipo `Item`.

Analise as alternativas a seguir:

I. A função `partition` é referente à partição do algoritmo Quick Sort, em que a cada execução o pivô é escolhido (`a[lo]`), todos os elementos menores e maiores são reposicionados no vetor e o pivô é colocado na posição final correta na ordenação.
II. A função `partition` tem comportamento linear, varrendo todo o vetor de entrada a cada vez que é executada.
III. Nesta implementação, a função `partition` continua as varreduras da esquerda para a direita (variável `i`) e da direita para a esquerda (variável `j`) enquanto as chaves são iguais a `a[lo]`.

É correto afirmar que:""",

    "oficial_2026-1_q17": """\
Considere o trecho de código a seguir escrito em C:

```c
#include <stdio.h>

struct P {
    int x;
    int y;
};

int main() {
    struct P v[3] = { {1, 2}, {3, 4}, {5, 6} };
    int soma = 0;
    for (int i = 0; i < 3; i++)
        soma += v[i].x + v[2 - i].y;
    printf("%d", soma);
    return 0;
}
```

Qual será a saída produzida por este programa?""",

    "oficial_2026-1_q18": """\
Considere a equação `y_i = sign(b + Σⱼ Wⱼ · X[i][j])` (perceptron forward pass).

Deseja-se implementar a função:

```c
void forward(int m, int n, double X[m][n], double W[n], double b, int y[m]);
```

Qual das alternativas a seguir contém a implementação correta dessa função?""",

    # ============================================================
    # Prova 2025/2
    # ============================================================
    "oficial_2025-2_q06": """\
Considere o seguinte trecho de código em C-like:

```c
int i, j, c;
c = 1;
for (i = 1; i < n; i++) {
    for (j = 1; j <= n; j++) {
        c = c + 1;
    }
}
```

Assumindo que a instrução `c = c + 1` é O(1), qual a expressão que melhor define a ordem de complexidade do trecho de código acima?""",

    "oficial_2025-2_q12": """\
Considere o seguinte trecho de código, implementado em C, representando um método de um Tipo Abstrato de Dados chamado `tPartida`:

```c
void obtemDadosPartida(tPartida *p, char *nomeTimeFora, char *nomeTimeCasa,
                       int *pontosTimeFora, int *pontosTimeCasa) {
    strcpy(nomeTimeFora, p->nomeTimeFora);
    strcpy(nomeTimeCasa, p->nomeTimeCasa);
    *pontosTimeFora = p->pontosTimeFora;
    *pontosTimeCasa = p->pontosTimeCasa;
}
```

Assinale a alternativa correta.""",

    "oficial_2025-2_q15": """\
Considere o trecho de código em linguagem de programação C a seguir:

```c
void sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}
```

Assinale a alternativa que apresenta, corretamente, o que esse trecho de código fará ao ser executado.""",

    "oficial_2025-2_q16": """\
Sobre o algoritmo apresentado a seguir:

```c
int busca(int arr[], int tamanho, int valor) {
    for (int i = 0; i < tamanho; i++) {
        if (arr[i] == valor) {
            return i;
        }
    }
    return -1;  // Retorna -1 se o valor não for encontrado
}
```

Assinale a alternativa correta sobre o funcionamento do algoritmo:""",

    # ============================================================
    # Prova 2025/1
    # ============================================================
    "oficial_2025-1_q06": """\
Considere o seguinte trecho de código em C-like:

```c
int i, j, c;
c = 1;
for (i = 1; i < n; i = i * 2) {
    for (j = 1; j <= n; j++) {
        c = c + 1;
    }
}
```

Assumindo que a instrução `c = c + 1` é O(1), qual a expressão que melhor define a ordem de complexidade do trecho de código acima?""",

    "oficial_2025-1_q11": """\
Considere o trecho de código em linguagem de programação C a seguir:

```c
int myCount = 0;
while (myCount < 10) {
    printf("%d", myCount + 1);
}
printf("Fim: %d", myCount + 1);
```

Assinale a alternativa que apresenta, corretamente, o que esse trecho de código fará ao ser executado.""",

    "oficial_2025-1_q12": """\
Considere o trecho de código em linguagem de programação C a seguir:

```c
void sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        int temp = arr[i];
        arr[i] = arr[min_idx];
        arr[min_idx] = temp;
    }
}
```

Assinale a alternativa que apresenta, corretamente, o que esse trecho de código fará ao ser executado.""",

    "oficial_2025-1_q15": """\
Sobre o algoritmo de ordenação MergeSort, descrito no trecho de código a seguir:

```c
void merge(int *arr, int lo, int mid, int hi) {
    int i = lo;
    int j = mid + 1;
    while (i <= mid && j <= hi) {
        if (arr[i] <= arr[j]) {
            i++;
        } else {
            int value = arr[j];
            int index = j;
            while (index != i) {
                arr[index] = arr[index - 1];
                index--;
            }
            arr[i] = value;
            i++;
            mid++;
            j++;
        }
    }
}

void merge_sort(Item *a, Item *aux, int lo, int hi) {
    if (hi <= lo) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort(a, aux, lo, mid);
    merge_sort(a, aux, mid + 1, hi);
    merge(a, aux, lo, mid, hi);
}
```

Assinale a alternativa correta sobre este algoritmo de ordenação:""",

    "oficial_2025-1_q16": """\
Sobre o algoritmo apresentado a seguir:

```c
int funcao(int x, int n, int v[]) {
    int k;
    k = n - 1;
    while (k >= 0 && v[k] != x)
        k -= 1;
    return k;
}
```

Assinale a alternativa correta sobre o funcionamento do algoritmo:""",
}


def main() -> None:
    bank = load_bank()
    aplicadas = 0
    nao_encontradas: list[str] = []
    for qid, enunciado in ENUNCIADOS.items():
        found = False
        for i, q in enumerate(bank.questions):
            if q.id == qid:
                q.enunciado = enunciado.rstrip()
                bank.questions[i] = q
                aplicadas += 1
                found = True
                break
        if not found:
            nao_encontradas.append(qid)
    save_bank(bank)
    print(f"Enunciados reescritos: {aplicadas} / {len(ENUNCIADOS)}")
    if nao_encontradas:
        print("Não encontradas:")
        for q in nao_encontradas:
            print(f"  - {q}")


if __name__ == "__main__":
    main()
