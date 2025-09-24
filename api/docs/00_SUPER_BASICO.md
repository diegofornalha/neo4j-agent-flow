# 🎯 O Super Básico da Nossa API - Para Diego

## 🔑 Os 3 Conceitos ESSENCIAIS

### 1️⃣ **É um Tradutor**
```
Browser fala HTTP → Nossa API traduz → Claude entende
```

### 2️⃣ **É um Streaming**
```
Claude responde → API quebra em pedaços → Browser recebe aos poucos
```

### 3️⃣ **É com Memória**
```
Conversa 1 + Conversa 2 + Conversa 3 = Claude lembra tudo
```

---

## 🚀 Código Mínimo que FUNCIONA

### Python (3 linhas)
```python
import requests

# Só isso! Manda mensagem e recebe resposta
response = requests.post("http://localhost:8000/api/chat",
    json={"message": "Oi"})
print(response.text)
```

### JavaScript (4 linhas)
```javascript
fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    body: JSON.stringify({message: "Oi"})
}).then(r => r.text()).then(console.log)
```

### cURL (1 linha)
```bash
curl -X POST localhost:8000/api/chat -d '{"message":"Oi"}' -H "Content-Type: application/json"
```

---

## 📍 Os 2 Endpoints que IMPORTAM

### 1. `/api/chat` - Conversar
```python
# ENVIAR
{
    "message": "sua pergunta aqui"
}

# RECEBER
{
    "content": "resposta do Claude",
    "session_id": "abc-123"
}
```

### 2. `/api/health` - Verificar se tá vivo
```python
# RECEBER
{
    "status": "healthy"  # Tá funcionando!
}
```

---

## 🎮 Como Rodar em 30 Segundos

```bash
# 1. Entre na pasta
cd api

# 2. Instale
pip install fastapi uvicorn

# 3. Rode
python server.py

# 4. Teste
curl localhost:8000/api/health
```

---

## 💡 O Fluxo SUPER Simplificado

```
Você digita "Oi"
      ↓
API recebe POST
      ↓
Manda pro Claude
      ↓
Claude responde "Olá!"
      ↓
API te entrega
```

---

## 🔥 Por que isso é GENIAL?

### Sem nossa API:
```python
# NÃO FUNCIONA no browser
from claude_code_sdk import query  # ❌ Browser não tem Python!
```

### Com nossa API:
```javascript
// FUNCIONA em qualquer lugar!
fetch('/api/chat')  // ✅ Browser, mobile, IoT, tudo!
```

---

## 📝 Exemplo COMPLETO Funcionando

### arquivo: `teste.html`
```html
<!DOCTYPE html>
<html>
<body>
    <button onclick="perguntar()">Clique para Testar</button>
    <div id="resposta"></div>

    <script>
    function perguntar() {
        fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: "Oi, tudo bem?"})
        })
        .then(r => r.json())
        .then(data => {
            document.getElementById('resposta').innerHTML = data.content;
        });
    }
    </script>
</body>
</html>
```

**Salve, abra no browser, clique no botão. PRONTO!**

---

## 🎯 Os 5 Comandos que Você Vai Usar

```bash
# 1. Rodar servidor
python server.py

# 2. Testar se tá vivo
curl localhost:8000/api/health

# 3. Mandar mensagem
curl -X POST localhost:8000/api/chat -d '{"message":"oi"}' -H "Content-Type: application/json"

# 4. Ver logs
tail -f logs/api.log

# 5. Parar servidor
Ctrl + C
```

---

## ⚡ Resumo em 1 Frase

> **"Nossa API deixa você usar Claude AI em qualquer lugar que aceite HTTP"**

---

## 🏆 Teste Rápido de Entendimento

Se você entende isso, entende a API:

```
Browser --HTTP--> Nossa API --SDK--> Claude AI
Browser <--JSON-- Nossa API <--Texto-- Claude AI
```

**É SÓ ISSO!** O resto é detalhe.

---

## 🎮 Próximo Passo

Agora que entendeu o básico:

1. **Rode a API** (python server.py)
2. **Faça 1 request** (curl ou browser)
3. **Veja funcionar**

**Conseguiu? +10 pontos!** 🚀