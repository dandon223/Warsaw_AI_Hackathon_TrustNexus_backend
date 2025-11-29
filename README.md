# Warsaw_AI_Hackathon_TrustNexus

## Backend

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv init
```


```
cd backend
uv run manage.py migrate
uv run manage.py runserver
```