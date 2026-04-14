# Implementação de API com FastAPI em EC2

Este manual explica os comandos e procedimentos para implantar uma API desenvolvida com FastAPI em uma instância EC2.

---

## Condições

* Conta na AWS (Amazon Web Services)
* Instância EC2 criada (Amazon Linux)
* Chave `.ppk` para conexão SSH(via PuTTY)
* Projeto FastAPI concluido

---

## 1. Acessar a instância EC2

### Usando PuTTY (Windows)

1. Abra o PuTTY

2. Em **Host Name**, insira:

```
ec2-user@SEU_IP_PUBLICO
```

3. Vá em:

```
Connection → SSH → Auth → Credentials
```

4. Selecione sua chave `.ppk`
5. Clique em **Open**

---

## 2. Atualizar o software

``` bash
sudo dnf update -y
```
---

## 3. Instalar dependências

```bash
sudo dnf install python3 git -y
```

Instalar o **uv**:

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

Recarregar o shell:

```bash
source ~/.bashrc
```

## 4. Duplicar o projeto

``` bash
git clone https://github.com/seu-repositorio/api.git
cd api
```
---

## 5. Estabelecer e ativar um ambiente virtual

Criar ambiente virtual:

```bash
uv venv
```

Ativar:

```bash
source .venv/bin/activate
```
---

## 6. Instalar dependências do projeto

Se houver `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

Ou instalar manualmente:

```bash
uv pip install fastapi uvicorn
```
---

## 7. Executar a aplicação (modo desenvolvimento)

``` bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Acesse:

```
http://SEU_IP:8000/docs
```
---

## 8. Executar em produção (Gunicorn + Uvicorn)

Instale:

``` bash
pip install gunicorn uvicorn
```

Execute:

``` bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
---

## 9. Criar serviço com systemd

Criar arquivo:

```bash
sudo nano /etc/systemd/system/fastapi.service
```

Conteúdo:

```ini
[Unit]
Description=FastAPI App
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/api
ExecStart=/home/ec2-user/api/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar:

```bash
sudo systemctl daemon-reexec
sudo systemctl start fastapi
sudo systemctl enable fastapi
sudo systemctl status fastapi
```
---

## 10. Instalar e configurar Nginx

Instalar:

```bash
sudo dnf install nginx -y
```

Iniciar Nginx:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

Criar configuração:

```bash
sudo nano /etc/nginx/conf.d/fastapi.conf
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name SEU_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Reiniciar:

```bash
sudo systemctl restart nginx
```
---

## 11. Configurar HTTPS (Opcional)

Instalar Certbot:

``` bash
sudo apt install certbot python3-certbot-nginx -y
```

Gerar certificado:

``` bash
sudo certbot --nginx
```
---

## 12. Testes finais

* Acesse via navegador: `http://SEU_IP`
* Verifique logs:

```bash
journalctl -u fastapi
```
---

## Arquitetura Final

```
Cliente → Nginx → Gunicorn → FastAPI
```
---

## Boas práticas

* Empregar variáveis de ambiente (.env)
* Não expor portas desnecessárias
* Configurar firewall (Security Groups)
* Monitorar logs regularmente 
* Utilizar banco gerenciado (RDS)
---

## Considerações Finais

Sua API(FastAPI) estará operando em produção com:

* Alto desempenho (Gunicorn + Uvicorn)
* Proxy reverso (Nginx)
* Segurança utilizando HTTPS (opcional)
---
