# Conteúdo de apoio para os slides

Use este resumo como base para montar a apresentação (PowerPoint ou
similar) que acompanha o vídeo pitch. Sugestão de 8 a 10 slides.

## Slide 1 — Capa (links obrigatórios)

- Título: **Leroy Merlin Smart Hub — AI Logistics Extension**
- Subtítulo: Enterprise Challenge — Atividade 4
- **Link do vídeo no YouTube:** `[preencher após publicar]`
- **Link do repositório GitHub:** `[preencher com a URL deste repositório]`
- Autor: Leonardo Marsiarelli — RM 555366 — Turma 3SIOA

## Slide 2 — O problema

- Ruptura de estoque: produtos acabam sem aviso, a loja só percebe tarde.
- Reposição decidida manualmente entre múltiplas lojas gera rotas de entrega
  maiores e mais custosas.
- Consequência direta: venda perdida + custo logístico maior.

## Slide 3 — A proposta de valor

- **Smart Hub**: painel único de estoque para toda a rede de lojas.
- **AI Logistics Extension**: camada de IA que decide, com dados, o que
  repor e qual a melhor rota de entrega.
- Resultado no cenário de demonstração: **~29% de redução na distância**
  percorrida pela rota de reposição.

## Slide 4 — Arquitetura da solução

- Back-end: FastAPI + SQLAlchemy + SQLite (Python).
- Front-end: dashboard web (HTML/CSS/JS), sem dependências externas.
- Dois módulos de IA: `demand_forecast.py` e `route_optimizer.py`.
- Diagrama simples: Lojas → Histórico de vendas → Previsão de demanda →
  Lojas críticas → Otimizador de rota → Plano de entrega.

## Slide 5 — AI Logistics Extension: previsão de demanda

- Técnica: suavização exponencial dupla (Holt) sobre 30 dias de vendas.
- Saída: projeção diária de demanda + quantidade sugerida de reposição,
  considerando estoque de segurança por produto.
- Print do dashboard com o gráfico de previsão.

## Slide 6 — AI Logistics Extension: roteirização de entregas

- Técnica: heurística do vizinho mais próximo + refinamento 2-opt sobre
  distância geográfica real (fórmula de Haversine).
- Entrada: lojas com estoque crítico identificadas automaticamente pela
  previsão de demanda.
- Saída: rota ordenada a partir do Centro de Distribuição, com economia de
  distância comparada a uma rota não otimizada.
- Print do dashboard com o plano de rota.

## Slide 7 — Demonstração (transição para o vídeo)

- "A seguir, veja o produto funcionando de ponta a ponta" — serve de gancho
  para a parte gravada, caso a apresentação seja usada ao vivo.

## Slide 8 — Produto concluído e escopo

- O que está pronto e testado: gestão de estoque, previsão de demanda,
  roteirização de entregas, dashboard funcional, testes automatizados.
- O que está fora do escopo acadêmico definido: integração com sistemas
  legados reais da empresa e processamento de pagamentos.

## Slide 9 — Autor

- Foto, nome completo e RM: Leonardo Marsiarelli — RM 555366 — Turma 3SIOA.
- Indicação se deseja participar do **FIAP NEXT 2026** como expositor
  (24/10, ARCA Spaces, São Paulo).

## Slide 10 — Encerramento

- Retomar o valor central: menos ruptura de estoque, menos quilômetro
  rodado, decisão logística baseada em dados.
- Agradecimento e link do repositório/vídeo novamente, se desejado.
