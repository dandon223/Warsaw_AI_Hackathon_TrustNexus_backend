# Warsaw_AI_Hackathon_TrustNexus

## Backend

### How to run

1. Create .env file in repository root with:

* LLM API KEY (OPEN_AI_TOKEN=<CYFRONET API TOKEN>)
* Cryptography key (EMAIL_ENCRYPTION_KEY=<GENERATED KEY>):
    * key generate running: 
```
uv run python - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
```
2. Run backend:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv init
uv sync
cd backend
uv run python manage.py makemigrations backendApp
uv run manage.py migrate
uv run manage.py runserver
```

### How to format code
```
uv run ruff check --select I --fix
uv run ruff format
```