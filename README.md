```markdown
# NimurAPI

NimurAPI é uma API avançada para indexação e busca de documentos, construída com FastAPI e Whoosh. Este projeto permite indexar documentos em diversos formatos e realizar buscas eficientes com suporte a destaque de texto.

## Funcionalidades

- **Indexação de Documentos**: Suporte para formatos `.txt`, `.pdf`, `.docx` e `.md`.
- **Busca Avançada**: Realiza buscas com destaque de texto e paginação configurável.
- **Estatísticas do Índice**: Informações como total de documentos, tamanho do índice e formatos suportados.
- **Configuração Flexível**: Paginação personalizável e diretórios de dados personalizados.

## Tecnologias Utilizadas

- 🚀 **FastAPI**: Framework para APIs modernas
- 🔍 **Whoosh**: Biblioteca de indexação e busca textual
- 📄 **PyPDF2** / **docx** / **BeautifulSoup**: Parsers para PDF, Word e Markdown
- ⚙️ **Pydantic**: Validação de dados e modelos

## Configuração Rápida

### Variáveis de Ambiente

Crie um arquivo `.env` com:

```ini
APP_NAME=NimurAPI
DATA_DIRECTORY=/caminho/para/dados  # Altere para seu diretório
INDEX_DIR=nimur_index
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
```

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/nimur-api.git
   cd nimur-api
   ```

2. Configure ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints Principais

| Método | Endpoint           | Descrição                     |
|--------|--------------------|-------------------------------|
| `GET`  | `/`                | Verificação do status da API  |
| `POST` | `/index`           | Indexar documentos            |
| `GET`  | `/search`          | Realizar buscas               |
| `GET`  | `/index/stats`     | Obter estatísticas do índice  |

## Exemplos de Uso

### Indexação de Documentos
```bash
curl -X POST "http://localhost:8000/index?directory_path=/seus/documentos"
```

### Busca com Destaque
```bash
curl "http://localhost:8000/search?query=python&limit=5"
```

Resposta exemplo:
```json
{
  "results": [
    {
      "path": "/docs/python.md",
      "highlight": "Guia de <b>Python</b> para iniciantes...",
      "score": 4.21
    }
  ],
  "total": 15
}
```

## Estrutura do Projeto

```
nimur-api/
├── app/
│   ├── core/
│   │   └── indexer.py       # Gerenciamento de índices
│   ├── services/
│   │   └── file_parser.py   # Parsers de arquivo
│   ├── models/
│   │   └── schema.py        # Modelos Pydantic
│   └── main.py              # Ponto de entrada
├── .env.example
└── requirements.txt
```

## Contribuição

1. Faça um fork do projeto
2. Crie sua branch:
   ```bash
   git checkout -b feature/incrivel
   ```
3. Envie suas alterações:
   ```bash
   git push origin feature/incrivel
   ```
4. Abra um Pull Request

## Licença

Distribuído sob licença MIT. Veja `LICENSE` para mais detalhes.

---

**Nota**: Configure corretamente o `DATA_DIRECTORY` no `.env` antes de iniciar a API.
```