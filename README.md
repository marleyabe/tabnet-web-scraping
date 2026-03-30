# TabNet DATASUS — Web Scraping

Web scraping do [TabNet DATASUS](http://tabnet.datasus.gov.br) para coleta automatizada de dados do Sistema de Informações Hospitalares (SIH).

## Apresentação

Para visualizar a apresentação do projeto:

```bash
uv run python -m http.server 8000
```

Acesse no navegador: [http://localhost:8000/apresentacao.html](http://localhost:8000/apresentacao.html)

## Instalação

```bash
git clone git@github.com:marleyabe/tabnet-web-scraping.git
cd tabnet-web-scraping
uv sync
```

## Uso

```bash
uv run get_data.py
```

Os arquivos CSV gerados são salvos na pasta `baixados/`.
