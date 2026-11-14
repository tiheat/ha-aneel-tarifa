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
| Preço final | BRL/kWh | `(tarifa + adicional da bandeira) ÷ (1 − ICMS − PIS − COFINS)` (impostos "por dentro"); atributos com as alíquotas |
| Tarifa sem impostos | BRL/kWh | TUSD + TE vigentes; atributos com TUSD, TE, resolução e vigência |
| Bandeira tarifária | — | Estado entre `verde`, `amarela`, `vermelha_p1`, `vermelha_p2` e `escassez_hidrica` (exibidos traduzidos); atributos `nome` (como a ANEEL publica) e `competencia` |
| Adicional da bandeira | BRL/kWh | Acréscimo da bandeira do mês |

Os sensores em BRL/kWh guardam estatísticas de longo prazo, então o histórico de preço fica disponível além da
retenção do recorder. A bandeira é um sensor de opções fixas: em automações, use os estados acima, por exemplo
`{{ is_state('sensor.tarifa_coelba_bandeira_tarifaria', 'vermelha_p2') }}`.

No painel de Energia, use **Preço final** como "entidade com o preço atual" da rede (importação e, se quiser, injeção).

## Configuração

Ao adicionar a integração, informe:

- **Distribuidora**: lista das distribuidoras com tarifa B1 residencial nos dados da ANEEL (a integração recusa a
  configuração se não houver tarifa vigente).
- **Subclasse residencial**: Residencial, Baixa Renda ou faixas da Tarifa/Desconto Social.
- **ICMS, PIS e COFINS** (%): conforme a fatura.

PIS e COFINS mudam todo mês: atualize em *Configurações → Dispositivos e serviços → Tarifa ANEEL → Configurar*; a
integração recarrega sozinha. Para outra distribuidora ou subclasse, adicione uma nova entrada.

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

As versões seguem [SemVer](https://semver.org/lang/pt-BR/) e são geradas automaticamente pelo
[semantic-release](https://semantic-release.gitbook.io/) a cada push ou merge na `main` que passa na CI, a partir
dos [commits convencionais](https://www.conventionalcommits.org/) desde a última tag:

| Commit | Versão |
|---|---|
| `fix: ...`, `perf: ...`, `refactor: ...`, `build: ...` | patch (1.1.**1**) |
| `feat: ...` | minor (1.**2**.0) |
| `BREAKING CHANGE:` no rodapé | major (**2**.0.0) |
| `docs:`, `chore:`, `test:`, `ci:`, `style:` | sem nova versão |

O job `release` atualiza a versão no `manifest.json` e no `pyproject.toml`, acrescenta as notas da versão no
topo do [`CHANGELOG.md`](CHANGELOG.md) e commita os três arquivos direto na `main` (`chore: release X.Y.Z`).
Em seguida cria a tag `vX.Y.Z` e a release no GitHub com as mesmas notas e o `aneel_tarifa.zip` anexado
(usado pelo Marketplace/HACS para instalar e atualizar).

## Desenvolvimento

As ferramentas (Python, ruff, pytest) são instaladas pelo [mise](https://mise.jdx.dev/) a partir do `mise.toml`.
Os testes cobrem o módulo puro `aneel.py` (sem dependência do Home Assistant); a CI roda também o `hassfest`.

```bash
mise run lint
```

```bash
mise run format
```

```bash
mise run test
```
