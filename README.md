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

Este projeto usa **Postgres gerenciado pelo Render**, configurado via variável de ambiente `DATABASE_URL`. Isso resolve o problema do SQLite: mesmo que o Web Service reinicie ou "durma" no plano free, o banco de dados continua rodando separado e os dados não se perdem.

Como configurar:

1. No Render, crie um serviço **New + → PostgreSQL** (pode ser plano Free).
2. Copie a **Internal Database URL** gerada.
3. No seu Web Service (a API), vá em **Environment** e crie a variável `DATABASE_URL` com esse valor.
4. Redeploy o serviço (o Render geralmente já reinicia sozinho ao salvar a env var).

**Atenção:** no plano Free do Render Postgres, o banco **expira depois de 90 dias** (o Render avisa por e-mail antes disso). Para um contador de cliques isso costuma bastar, mas se quiser manter os dados por mais tempo, migre pra um plano pago ou exporte os dados periodicamente.

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
