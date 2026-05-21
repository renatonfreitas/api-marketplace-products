# 🚀 Guia de Deploy: FastAPI no AWS EC2
 
Este guia explica todos os passos para implantar a **API Marketplace de Produtos** em uma instância EC2 da AWS com Linux.
 
---
 
## 📋 Pré-requisitos
 
- Conta AWS ativa
- Instância EC2 criada (Amazon Linux 2)
- Acesso SSH à instância (chave `.pem` ou PuTTY com `.ppk`)
- Banco de dados Supabase criado e configurado
- Projeto FastAPI pronto no repositório Git
---
 
## 1️⃣ Conectar à Instância EC2
 
### Usando SSH (Linux/macOS)
 
```bash
chmod 400 sua-chave.pem
ssh -i sua-chave.pem ec2-user@SEU_IP_PUBLICO
```
 
### Usando PuTTY (Windows)
 
1. Abra o **PuTTY**
2. Em **Host Name**, insira: `ec2-user@SEU_IP_PUBLICO`
3. Vá em: **Connection → SSH → Auth → Credentials**
4. Selecione sua chave `.ppk`
5. Clique em **Open**
> 💡 **Dica:** Salve a sessão para fácil acesso futuro
 
---
 
## 2️⃣ Atualizar o Sistema
 
```bash
sudo dnf update -y
```
 
---
 
## 3️⃣ Instalar Dependências
 
### Python e Git
 
```bash
sudo dnf install python3 git -y
```
 
### Gerenciador de Pacotes `uv`
 
```bash
curl -Ls https://astral.sh/uv/install.sh | bash
source ~/.bashrc
```
 
Verifique a instalação:
 
```bash
uv --version
```
 
---
 
## 4️⃣ Clonar o Projeto
 
```bash
cd /home/ec2-user
git clone https://github.com/renatonfreitas/api-marketplace-products.git
cd api-marketplace-products
```
 
---
 
## 5️⃣ Configurar Variáveis de Ambiente
 
Crie o arquivo `.env`:
 
```bash
nano .env
```
 
Cole o conteúdo (com suas credenciais Supabase):
 
```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-api-key-publica
 
# FastAPI
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```
 
Salve com **Ctrl+O**, **Enter**, **Ctrl+X**
 
---
 
## 6️⃣ Instalar Dependências do Projeto
 
```bash
uv sync --no-dev
```
 
---
 
## 7️⃣ Testar em Desenvolvimento
 
Ative o ambiente virtual:
 
```bash
source .venv/bin/activate
```
 
Execute a aplicação:
 
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
 
Teste:
 
```bash
curl http://localhost:8000/
```
 
Você deve receber:
 
```json
{
  "message": "API de produtos rodando!",
  "version": "2.0.0",
  "docs": "/docs"
}
```
 
Para acessar o Swagger: `http://SEU_IP:8000/docs`
 
Para interromper: **Ctrl+C**
 
---
 
## 8️⃣ Configurar Produção com Gunicorn + Uvicorn
 
### Instalar Gunicorn
 
```bash
uv pip install gunicorn uvicorn[standard]
```
 
### Testar Gunicorn
 
```bash
uv run gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```
 
Se funcionar, você verá:
 
```
[INFO] Starting gunicorn 21.x.x
[INFO] Listening at: 0.0.0.0:8000 (12345)
```
 
Interrompa com **Ctrl+C**
 
---
 
## 9️⃣ Criar Serviço Systemd
 
Crie o arquivo de serviço:
 
```bash
sudo nano /etc/systemd/system/api-marketplace.service
```
 
Cole o conteúdo:
 
```ini
[Unit]
Description=API Marketplace de Produtos
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=60
 
[Service]
Type=notify
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/api-marketplace-products
Environment="PATH=/home/ec2-user/api-marketplace-products/.venv/bin"
ExecStart=/home/ec2-user/api-marketplace-products/.venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --graceful-timeout 30 \
    app.main:app
 
Restart=always
RestartSec=10
 
[Install]
WantedBy=multi-user.target
```
 
Salve e saia.
 
### Ativar o Serviço
 
```bash
sudo systemctl daemon-reload
sudo systemctl start api-marketplace
sudo systemctl enable api-marketplace
sudo systemctl status api-marketplace
```
 
Você deve ver:
 
```
● api-marketplace.service - API Marketplace de Produtos
   Loaded: loaded (/etc/systemd/system/api-marketplace.service)
   Active: active (running) since ...
```
 
---
 
## 🔟 Instalar e Configurar Nginx
 
### Instalar Nginx
 
```bash
sudo dnf install nginx -y
```
 
### Criar Configuração
 
```bash
sudo nano /etc/nginx/conf.d/api-marketplace.conf
```
 
Cole o conteúdo:
 
```nginx
upstream api_marketplace {
    server 127.0.0.1:8000;
}
 
server {
    listen 80;
    server_name SEU_IP_PUBLICO;
 
    client_max_body_size 10M;
 
    location / {
        proxy_pass http://api_marketplace;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
 
    # Cache de arquivos estáticos
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```
 
### Ativar Nginx
 
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```
 
---
 
## 1️⃣1️⃣ Configurar HTTPS com Let's Encrypt (Recomendado)
 
### Instalar Certbot
 
```bash
sudo dnf install certbot python3-certbot-nginx -y
```
 
### Gerar Certificado
 
```bash
sudo certbot --nginx -d SEU_DOMINIO.com
```
 
Se for um IP público sem domínio, use um domínio temporário ou pule para o step 12.
 
---
 
## 1️⃣2️⃣ Configurar Security Groups da AWS
 
1. Acesse **EC2 → Instances** no console AWS
2. Selecione sua instância
3. Vá em **Security** → Clique no Security Group
4. Clique em **Inbound rules** → **Edit inbound rules**
5. Adicione as seguintes regras:
| Type | Protocol | Port Range | Source |
|------|----------|-----------|--------|
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| SSH | TCP | 22 | Seu IP (para segurança) |
 
6. Clique em **Save rules**
---
 
## 1️⃣3️⃣ Testes Finais
 
### Verificar se a API está respondendo
 
```bash
curl http://SEU_IP/
```
 
Deve retornar:
 
```json
{
  "message": "API de produtos rodando!",
  "version": "2.0.0",
  "docs": "/docs"
}
```
 
### Acessar a documentação Swagger
 
Abra no navegador:
 
```
http://SEU_IP/docs
```
 
### Verificar logs do serviço
 
```bash
sudo journalctl -u api-marketplace -f
```
 
### Verificar logs do Nginx
 
```bash
sudo tail -f /var/log/nginx/error.log
```
 
---
 
## 📊 Arquitetura Final
 
```
Internet
   ↓
AWS Security Groups (Firewall)
   ↓
Nginx (Porta 80/443)
   ↓
Gunicorn (Porta 8000)
   ↓
FastAPI App (app.main:app)
   ↓
Supabase PostgreSQL
```
 
---
 
## 🛠️ Troubleshooting
 
### Problema: "Connection refused" ao acessar a API
 
**Solução:**
```bash
# Verifique se o serviço está ativo
sudo systemctl status api-marketplace
 
# Reinicie o serviço
sudo systemctl restart api-marketplace
 
# Verifique os logs
sudo journalctl -u api-marketplace -n 50
```
 
### Problema: "502 Bad Gateway" do Nginx
 
**Solução:**
```bash
# Verifique se o Gunicorn está rodando
curl http://127.0.0.1:8000/
 
# Reinicie ambos
sudo systemctl restart api-marketplace
sudo systemctl restart nginx
```
 
### Problema: "SUPABASE_KEY not found"
 
**Solução:**
```bash
# Verifique o arquivo .env
cat /home/ec2-user/api-marketplace-products/.env
 
# Certifique-se de que tem as chaves corretas
# Reinicie o serviço
sudo systemctl restart api-marketplace
```
 
### Problema: Instância fora do ar
 
**Solução:**
```bash
# Conecte via SSH e verifique a memória
free -h
 
# Verifique o espaço em disco
df -h
 
# Se necessário, aumente a instância no console AWS
```
 
### Problema: Lento ou timeout
 
**Solução:**
1. Aumentar workers do Gunicorn (no arquivo systemd):
   ```ini
   -w 8  # ao invés de 4
   ```
 
2. Aumentar timeouts do Nginx:
   ```nginx
   proxy_read_timeout 120s;
   ```
 
3. Aumentar tipo de instância EC2 (t3.small → t3.medium)
---
 
## 📈 Monitoramento e Manutenção
 
### Ver uso de recursos
 
```bash
# CPU e memória
top
 
# Espaço em disco
df -h
 
# Logs da API
sudo journalctl -u api-marketplace -n 100 -f
```
 
### Atualizar a aplicação
 
```bash
cd /home/ec2-user/api-marketplace-products
git pull origin main
uv sync --no-dev
sudo systemctl restart api-marketplace
```
 
### Fazer backup do banco de dados
 
O Supabase oferece backups automáticos, mas você pode exportar dados:
 
```bash
# Via Supabase CLI
supabase db pull
```
 
---
 
## ✅ Checklist de Produção
 
- [ ] HTTPS configurado (Let's Encrypt)
- [ ] Security Groups restritos (apenas HTTP/HTTPS/SSH)
- [ ] Variáveis de ambiente configuradas (.env)
- [ ] Logs sendo monitorados
- [ ] Backup do Supabase habilitado
- [ ] Autoscaling configurado (opcional)
- [ ] CloudWatch alarms configurados (opcional)
- [ ] Domínio apontando para IP (se aplicável)
---
 
## 📚 Recursos Úteis
 
- [FastAPI Deploy](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Proxy Documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Supabase Documentation](https://supabase.com/docs)
---
 
## 🆘 Suporte
 
Se tiver dúvidas, abra uma issue no repositório:
 
```
https://github.com/renatonfreitas/api-marketplace-products/issues
```
 
---
 