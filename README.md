# Leroy Merlin Smart Hub — AI Logistics Extension

Enterprise Challenge — Atividade 4 (FIAP)

> Produto acadêmico-profissional que centraliza o estoque das lojas Leroy Merlin
> e adiciona uma camada de Inteligência Artificial para logística: previsão de
> demanda por SKU/loja e roteirização otimizada de entregas a partir do Centro
> de Distribuição.

## Autor

| Nome completo         | RM     | Turma |
|------------------------|--------|-------|
| Leonardo Marsiarelli   | 555366 | 3SIOA |

## O problema

Redes de lojas físicas de materiais de construção como a Leroy Merlin convivem
com dois problemas logísticos recorrentes:

1. **Ruptura de estoque** — quando a demanda de um produto varia (sazonalidade,
   fim de semana, obras na região), a loja só percebe o problema quando o
   produto já acabou na prateleira.
2. **Entregas de reposição ineficientes** — quando várias lojas precisam de
   reposição ao mesmo tempo, decidir a ordem de entrega "no olho" gera rotas
   maiores, mais combustível e mais tempo de caminhão parado.

## A solução: Smart Hub + AI Logistics Extension

O **Smart Hub** é o núcleo do produto: um painel único que consolida estoque,
lojas, produtos e histórico de vendas de toda a rede.

A **AI Logistics Extension** é a camada de inteligência aplicada sobre esse
núcleo, com dois módulos:

- **Previsão de demanda** (`backend/app/ai/demand_forecast.py`) — usa
  suavização exponencial dupla (método de Holt) sobre o histórico de vendas
  diárias de cada produto em cada loja para projetar a demanda dos próximos
  dias e sugerir a quantidade de reposição, considerando o estoque de
  segurança de cada SKU.
- **Roteirização de entregas** (`backend/app/ai/route_optimizer.py`) — a
  partir das lojas com estoque crítico, monta a rota de entrega do Centro de
  Distribuição usando a heurística do vizinho mais próximo com refinamento
  2-opt, reduzindo a distância total percorrida em relação a uma rota ingênua
  (ordem arbitrária das paradas).

Na demonstração com os dados de exemplo, a roteirização otimizada reduz a
distância total em cerca de **29%** em relação à rota não otimizada.

## Arquitetura

```
challenge-leroy/
├── backend/
│   ├── app/
│   │   ├── main.py          # API FastAPI (endpoints REST)
│   │   ├── models.py        # Store, Product, Inventory, SalesHistory
│   │   ├── schemas.py       # Contratos de entrada/saída (Pydantic)
│   │   ├── seed.py          # Popula o banco com dados de demonstração
│   │   └── ai/
│   │       ├── demand_forecast.py   # AI Logistics Extension — previsão
│   │       └── route_optimizer.py   # AI Logistics Extension — roteirização
│   └── tests/
│       └── test_ai.py       # Testes automatizados dos módulos de IA
├── frontend/
│   ├── index.html           # Dashboard (KPIs, previsão, rota, estoque)
│   ├── app.js
│   └── styles.css
└── docs/
    ├── pitch-script.md          # Roteiro do vídeo pitch (até 5 min)
    └── apresentacao-resumo.md   # Conteúdo de apoio para os slides
```

**Stack:** Python 3.11, FastAPI, SQLAlchemy, SQLite, pytest no back-end;
HTML/CSS/JavaScript puro (sem dependências externas de CDN) no front-end.

## Como executar

```bash
git clone https://github.com/LeoMarsiarelli/Challenge-Leroy.git
cd Challenge-Leroy/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows (PowerShell/CMD): .venv\Scripts\activate
                                  # Windows (Git Bash/MINGW64): source .venv/Scripts/activate
pip install -r requirements.txt

python -m app.seed               # cria e popula o banco de demonstração
uvicorn app.main:app --reload    # sobe a API + serve o dashboard
```

> No prompt, confirme que a venv está ativa: o terminal deve mostrar `(.venv)`
> no início da linha antes de rodar `pip install`. Sem isso, o pip instala no
> Python global da máquina em vez do ambiente isolado do projeto.

Acesse `http://localhost:8000` para o dashboard e `http://localhost:8000/docs`
para a documentação interativa (Swagger) da API.

### Rodando os testes

```bash
cd backend
pytest tests/ -v
```

## Principais endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/stores` | Lista lojas e o Centro de Distribuição |
| GET | `/api/products` | Lista os SKUs cadastrados |
| GET | `/api/inventory` | Estoque consolidado (filtrável por loja) |
| GET | `/api/forecast/{store_id}/{product_id}` | Previsão de demanda + reposição sugerida |
| GET | `/api/logistics/route-plan` | Rota otimizada de entrega para lojas críticas |
| GET | `/api/dashboard/summary` | KPIs gerais da rede |

## Escopo do produto

Este projeto cobre o escopo que defini para o Enterprise Challenge:
gestão de estoque multi-loja, previsão de demanda por IA e roteirização
inteligente de entregas. Não inclui integração com sistemas legados reais da
Leroy Merlin nem processamento de pagamentos — esses pontos ficam fora do
escopo acadêmico definido para esta entrega.

## Entrega da Atividade 4

- Vídeo pitch (YouTube): `[[link a ser adicionado após a gravação]](https://youtu.be/QsYAtsIdOeg)`
- Repositório: `[[link deste repositório no GitHub]](https://github.com/LeoMarsiarelli/Challenge-Leroy)`
- Roteiro do vídeo: [`docs/pitch-script.md`](docs/pitch-script.md)
- Conteúdo de apoio para os slides: [`docs/apresentacao-resumo.md`](docs/apresentacao-resumo.md)
