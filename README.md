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

**Via Marketplace (Home Assistant 2026.11+) ou HACS (recomendado):**

1. Em *Configurações → Marketplace* (ou HACS, em versões anteriores), abra *Repositórios customizados* e adicione
   `https://github.com/tiheat/ha-aneel-tarifa` com a categoria *Integração*.
2. Instale **Tarifa ANEEL** e reinicie o Home Assistant.
3. Em *Configurações → Dispositivos e serviços → Adicionar integração*, procure **Tarifa ANEEL**.

Novas versões aparecem como atualização no próprio Home Assistant, a partir das releases deste repositório.

**Via SSH (desenvolvimento):** com o host `ha` configurado no `~/.ssh/config`, copie o código local e reinicie:

```bash
mise run deploy
```

```bash
mise run restart
```

## Limitações

- Considera só tarifa convencional B1 residencial (sem tarifa branca).
- Não inclui custos fixos da fatura (iluminação pública, custo de disponibilidade) nem o Fio B não compensado da
  geração distribuída (Lei 14.300); usar o mesmo preço para a injeção superestima o crédito.
- Se a ANEEL trocar os identificadores dos conjuntos de dados, atualize `RESOURCE_*` em `const.py`.

## Versionamento e releases

As versões seguem [SemVer](https://semver.org/lang/pt-BR/) e são geradas pelo
[release-please](https://github.com/googleapis/release-please) a partir das mensagens de commit
(`feat:` → minor, `fix:` → patch, `feat!:`/`BREAKING CHANGE` → major):

1. Cada merge na `main` abre ou atualiza um PR de release com a próxima versão, o `CHANGELOG.md` e o
   `version` do `manifest.json`.
2. O merge desse PR cria a tag `vX.Y.Z` e a release no GitHub com `aneel_tarifa.zip` anexado (usado pelo HACS).

## Desenvolvimento

```bash
mise run lint
```

```bash
mise run test
```
