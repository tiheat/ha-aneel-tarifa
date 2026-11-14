# Tarifa ANEEL para Home Assistant

Integração customizada que calcula o **preço final da energia por kWh** a partir dos
[dados abertos da ANEEL](https://dadosabertos.aneel.gov.br/), para usar no painel de Energia do Home Assistant.

- **Tarifa homologada** (TUSD + TE) da distribuidora escolhida, grupo B1 residencial convencional,
  conjunto [Tarifas de aplicação das distribuidoras](https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica).
- **Bandeira tarifária** do mês e seu adicional, conjunto
  [Bandeiras Tarifárias](https://dadosabertos.aneel.gov.br/dataset/bandeiras-tarifarias).
- **Impostos** (ICMS, PIS e COFINS) informados na configuração e editáveis em *Configurar*, já que PIS/COFINS mudam todo mês na fatura.

Os dados são consultados a cada 6 horas. Reajustes anuais e novas bandeiras entram automaticamente.

## Sensores

| Sensor | Unidade | Descrição |
|---|---|---|
| Preço final | BRL/kWh | `(tarifa + adicional da bandeira) ÷ (1 − ICMS − PIS − COFINS)` (impostos "por dentro") |
| Tarifa sem impostos | BRL/kWh | TUSD + TE vigentes; atributos com TUSD, TE, resolução e vigência |
| Bandeira tarifária | — | Verde, Amarela, Vermelha P1/P2…; atributo `competencia` |
| Adicional da bandeira | BRL/kWh | Acréscimo da bandeira do mês |

No painel de Energia, use **Preço final** como "entidade com o preço atual" da rede (importação e, se quiser, injeção).

## Instalação

Requer Home Assistant 2025.8 ou superior. O ícone da integração (pasta `brand/`) aparece a partir do 2026.3;
os SVGs de origem ficam em `assets/`.

**Via SSH (este repositório):** com o host `ha` configurado no `~/.ssh/config`:

```bash
mise run deploy
```

```bash
mise run restart
```

Depois, em *Configurações → Dispositivos e serviços → Adicionar integração*, procure **Tarifa ANEEL**.

**Via HACS:** adicione este repositório como repositório customizado do tipo *Integração*
(repositórios privados exigem token do GitHub no HACS).

## Limitações

- Considera só tarifa convencional B1 residencial (sem tarifa branca).
- Não inclui custos fixos da fatura (iluminação pública, custo de disponibilidade) nem o Fio B não compensado da
  geração distribuída (Lei 14.300); usar o mesmo preço para a injeção superestima o crédito.
- Se a ANEEL trocar os identificadores dos conjuntos de dados, atualize `RESOURCE_*` em `const.py`.

## Desenvolvimento

```bash
mise run lint
```

```bash
mise run test
```
