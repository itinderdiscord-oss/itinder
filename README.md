# iTinder Click Counter API

API mínima em Flask para contar cliques no botão "Entrar no Discord".

## Endpoints

- `POST /api/click` — registra um clique. Body opcional: `{"source": "header"}` ou `{"source": "hero"}` pra saber qual botão foi clicado.
- `GET /api/stats` — retorna o total, cliques nas últimas 24h e o total por origem (source).
- `GET /` — health check.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py
```

A API sobe em `http://localhost:5000`.

## Deploy no Render

1. Suba esta pasta (`app.py`, `requirements.txt`) para um repositório no GitHub.
2. No Render, crie um **New Web Service** apontando pro repositório.
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
4. Deploy. Você vai receber uma URL tipo `https://itinder-api.onrender.com`.

## ⚠️ Sobre persistência dos dados

Este projeto usa **SQLite em arquivo local** (`clicks.db`). Isso funciona bem enquanto o serviço está rodando, mas **no plano free do Render o disco não é persistente**: se o serviço reiniciar ou fizer redeploy, o arquivo `clicks.db` é perdido e a contagem zera.

Se você quer que a contagem nunca se perca, duas opções:
- Adicionar um **Render Disk** (persistent disk, plano pago) e apontar `DB_PATH` pra ele.
- Trocar o SQLite por um banco gerenciado, como o **Render Postgres** (tem plano free também, mas com expiração após 90 dias de inatividade — verifique as condições atuais no site do Render).

Para o começo (validar se as pessoas estão clicando), o SQLite já resolve. Se crescer, migrar pro Postgres é simples.

## No frontend

No HTML, antes de redirecionar para o Discord, o botão dispara:

```js
fetch("https://SUA-URL-DO-RENDER.onrender.com/api/click", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ source: "hero" })
});
```

Isso não bloqueia a navegação — o clique é registrado em paralelo enquanto o Discord já abre.
