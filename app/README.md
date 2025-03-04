## Switching to a Different Model
If you want to use a different model, you can pull it by accessing the Ollama container via Bash (or from your terminal if you downloaded it manually) with the following command:

```bash
ollama pull {model_name}
```

After pulling the desired model, update the config.py file by modifying the following lines with the appropriate settings for your chosen model:

```bash
OLLAMA_MODEL = "qwen2.5:1.5b"
EMBEDDING_DIM = 384
```

Make sure the values match the requirements of the new model.

---
## Some Manual Installations (If Necessary)

Below are the steps for setting up the necessary components manually, including the Postgres database, environment, and Ollama installation.

- Setup Postgres Database
```
sudo apt update
sudo apt install postgresql
sudo apt install postgresql-16-pgvector
```

- Setting Up Environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Ollama Installation
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3:instruct
ollama pull bge-m3:latest
ollama serve
```
---
