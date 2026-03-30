# Web Scraping — TabNet DATASUS

---

## 1. Contexto

- **TabNet** é o sistema de tabulação de dados do DATASUS (Ministério da Saúde)
- Permite consultar indicadores de saúde pública, como internações hospitalares (SIH)
- O site **não oferece API** — os dados só são acessíveis via formulário web interativo
- **Solução:** automatizar o navegador para extrair os dados programaticamente

---

## 2. Objetivo

Baixar séries históricas do **Sistema de Informações Hospitalares (SIH)** para os últimos N meses, organizadas por:

- **Coluna:** tipo de agrupamento (ex: procedimento, especialidade)
- **Conteúdo:** métrica selecionada (ex: quantidade aprovada, valor aprovado)

Saída: arquivos `.csv` prontos para análise

---

## 3. Tecnologias

| Ferramenta | Papel |
|---|---|
| `selenium` | Automação do navegador Chrome |
| `pandas` | Leitura e concatenação dos dados |
| `uv` | Gerenciamento de dependências e ambiente virtual |

---

## 4. Como funciona — passo a passo

```
1. Abre o navegador e acessa o formulário do TabNet
2. Desmarca seleções padrão (Conteúdo e Mês)
3. Ativa opções: "Exibir linhas zeradas" e separador ";"
4. Para cada combinação de Coluna × Conteúdo:
   └── Para cada mês (1 a N):
       ├── Seleciona o mês
       ├── Clica em "Mostra"
       ├── Aguarda a nova aba com o CSV
       ├── Lê o conteúdo do <pre>
       ├── Converte para DataFrame e acumula
       └── Fecha a aba e volta ao formulário
5. Salva o DataFrame acumulado em baixados/<coluna>_<conteudo>.csv
```

---

## 5. Desafios técnicos

**Site lento e instável**
- Timeout de 60s para o formulário carregar
- Timeout de 120s para o CSV aparecer na nova aba
- Retry automático (até 3 tentativas) em caso de falha
- Salva o HTML da página para debug quando há erro

**Navegação entre abas**
- O TabNet abre o resultado em uma nova aba
- O script troca de janela, extrai os dados e fecha a aba antes de continuar

**Acumulação dos dados**
- Cada mês vem com cabeçalho e rodapé — apenas as linhas do meio são concatenadas nos meses subsequentes

---

## 6. Estrutura do projeto

```
tabnet/
├── get_data.py       # script principal
├── pyproject.toml    # dependências (uv)
├── uv.lock           # versões exatas
├── .gitignore        # exclui .venv/, baixados/, debug htmls
└── baixados/         # CSVs gerados (não versionado)
```

---

## 7. Como executar

```bash
# Clonar e instalar dependências
git clone <repo>
cd tabnet
uv sync

# Rodar (padrão: últimos 13 meses)
uv run get_data.py

# Para alterar o número de meses, editar a última linha:
get_data(meses=6)
```

---

## 8. Resultado

- Um arquivo `.csv` por combinação de Coluna × Conteúdo
- Separador `;`, com coluna extra `ano` indicando o período
- Prontos para importar no Excel, Power BI, Python, etc.

---

## 9. Possíveis evoluções

- Parametrizar via `argparse` (número de meses, colunas desejadas)
- Rodar em modo headless (sem abrir janela do Chrome)
- Agendar execução mensal automatizada
- Armazenar em banco de dados em vez de CSV
