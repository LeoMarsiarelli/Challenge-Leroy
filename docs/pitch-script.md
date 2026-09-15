# Roteiro do Vídeo Pitch — Atividade 4

Duração alvo: até **5 minutos**. Regra de ouro: pelo menos **3 minutos** de
demonstração funcional do produto rodando.

Antes de gravar: rode `python -m app.seed` para garantir dados frescos e
consistentes, suba o servidor (`uvicorn app.main:app --reload`) e deixe o
dashboard (`http://localhost:8000`) aberto e testado. Grave também um vídeo
de "plano B" do sistema funcionando, para o caso de a demonstração ao vivo
falhar.

---

## 0:00 – 0:45 · Abertura e proposta de valor

**Fala sugerida:**

> "As lojas Leroy Merlin vendem milhares de SKUs diferentes, todos os dias,
> em dezenas de unidades. Quando um produto sai de estoque sem aviso, a loja
> perde venda e o cliente perde confiança. E quando várias lojas precisam de
> reposição ao mesmo tempo, decidir a ordem de entrega manualmente custa tempo
> e quilômetros rodados à toa.
>
> Criamos o **Smart Hub**, um painel único que centraliza o estoque de toda a
> rede, e a **AI Logistics Extension**, uma camada de inteligência artificial
> que prevê a demanda de cada produto por loja e monta automaticamente a rota
> de entrega mais curta para repor o que está crítico. O objetivo é simples:
> menos ruptura de estoque, menos quilômetro rodado, mais eficiência
> logística."

Mostrar rapidamente a tela inicial do dashboard (KPIs) enquanto fala.

---

## 0:45 – 3:45 · Demonstração funcional (o coração do vídeo)

### Bloco 1 — Visão geral da rede (≈30s)

- Mostrar os KPIs no topo do dashboard: lojas monitoradas, SKUs ativos,
  itens em estoque crítico e % da rede em risco de ruptura.
- Falar: "Aqui já vemos, em tempo real, quantos itens estão no ponto crítico
  em toda a rede."

### Bloco 2 — Previsão de demanda com IA (≈1min15s)

- Selecionar uma loja e um produto no painel "Previsão de demanda".
- Clicar em **Gerar previsão** e mostrar o gráfico (histórico em verde,
  previsão em dourado).
- Explicar em termos simples: "O sistema usa os últimos 30 dias de venda
  desse produto nessa loja para calcular uma tendência e projetar quanto
  deve ser vendido nos próximos dias."
- Apontar os cards: demanda média por dia, estoque atual, **reposição
  sugerida pela IA** e dias estimados até a ruptura.
- Trocar de produto/loja uma vez para mostrar que o cálculo é dinâmico e
  reage a padrões diferentes (ex.: produto de giro rápido vs. lento).

### Bloco 3 — Roteirização inteligente de entregas (≈1min15s)

- Clicar em **Gerar rota otimizada**.
- Mostrar o resultado: origem (Centro de Distribuição), lista ordenada de
  paradas com distância entre elas e quantidade a entregar.
- Destacar os três números: distância otimizada, distância sem otimização e
  a **economia de distância** (no cenário de exemplo, cerca de 29%).
- Explicar: "O sistema identifica sozinho quais lojas estão com estoque
  crítico, calcula quanto cada uma precisa repor e decide a ordem de
  entrega que percorre a menor distância possível — sem que ninguém precise
  montar essa rota manualmente."

### Bloco 4 — Estoque consolidado (≈15s)

- Rolar até a tabela de estoque e filtrar por uma loja, mostrando os itens
  em vermelho (crítico) destacados automaticamente.

---

## 3:45 – 4:15 · Onde a AI Logistics Extension entra (reforço)

**Fala sugerida:**

> "Tudo isso que vocês acabaram de ver — a previsão de demanda e a rota
> otimizada — é a AI Logistics Extension funcionando dentro do Smart Hub.
> Ela não substitui a operação da loja: ela dá à equipe de logística uma
> decisão pronta, baseada em dados reais de venda e em geolocalização, em
> vez de uma estimativa manual."

(Pode mostrar rapidamente o código dos dois módulos de IA — `demand_forecast.py`
e `route_optimizer.py` — por 3-5 segundos apenas como evidência técnica, sem
entrar em detalhes de implementação.)

---

## 4:15 – 4:40 · Produto concluído + limitações de escopo

**Fala sugerida:**

> "O que vocês viram é o produto que estamos entregando ao final do
> Enterprise Challenge: previsão de demanda, roteirização e visão de estoque
> funcionando de ponta a ponta. Nosso escopo acadêmico não inclui integração
> com os sistemas internos reais da Leroy Merlin nem processamento de
> pagamentos — isso está fora do que definimos para esta entrega, e o
> restante está completo e testado."

---

## 4:40 – 5:00 · Conclusão + apresentação da equipe

**Fala sugerida:**

> "No fim das contas, o Smart Hub com a AI Logistics Extension resolve um
> problema muito concreto: menos produto faltando na prateleira e menos
> quilômetro rodado à toa para repor estoque. É eficiência que se traduz
> direto em economia e em uma experiência melhor para quem entra na loja."

Depois, cada integrante se apresenta com **foto, nome completo e RM**, por
exemplo:

> "Leonardo Marsiarelli, RM 555366, turma 3SIOA."

E o grupo responde, junto, se deseja participar como expositor no **FIAP NEXT
2026** (24/10, sábado, ARCA Spaces, São Paulo).

---

## Checklist antes de gravar

- [ ] Banco de dados populado (`python -m app.seed`) e servidor rodando
- [ ] Todos os itens do roteiro couberam em até 5 minutos
- [ ] Pelo menos 3 minutos são de demonstração funcional
- [ ] AI Logistics Extension foi claramente apontada na tela
- [ ] Cada integrante apareceu com nome completo e RM
- [ ] O grupo respondeu se deseja participar do NEXT 2026
- [ ] Vídeo de "plano B" gravado e salvo
