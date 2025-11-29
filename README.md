# Warsaw_AI_Hackathon_TrustNexus

## Backend

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv init
uv sync
```


```
cd backend
uv run manage.py migrate
uv run manage.py runserver
```

```
uv run python manage.py makemigrations backendApp
uv run python manage.py migrate
```

## LLM
1. Create .env file in repository root
2. set OPEN_AI_TOKEN=<CYFRONET API TOKEN>