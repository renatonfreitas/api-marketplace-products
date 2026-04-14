# Implementação de API com FastAPI em EC2

Este manual explica os comandos e procedimentos para implantar uma API desenvolvida com FastAPI em uma instância EC2.

---

## Condições

* Conta na AWS (Amazon Web Services)
* Instância EC2 criada (Ubuntu sugerido)
* Chave `.pem` para conexão SSH
* Projeto FastAPI concluido

---

## 1. Acessar a instância EC2

``` bash
ssh -i sua-chave.pem ubuntu@SEU_IP_PUBLICO
```
---

## 2. Atualizar o software

``` bash
sudo apt update && sudo apt upgrade -y
```
---

## 3. Instalar dependências

``` bash
sudo apt install python3-pip python3-venv git -y
```
---

## 4. Duplicar o projeto

``` bash
git clone https://github.com/seu-repositorio/api.git
cd api
```
---

## 5. Estabelecer e ativar um ambiente virtual

``` bash
python3 -m venv venv
source venv/bin/activate
```
---

## 6. Instalar dependências do projeto

``` bash
pip install -r requirements.txt
```

Ou de forma manual:

``` bash
pip install fastapi uvicorn
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

Criar arquivo de serviço:

``` bash
sudo nano /etc/systemd/system/fastapi.service
```

Conteúdo:

``` ini
[Unit]
Description=FastAPI App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/api
ExecStart=/home/ubuntu/api/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar:

``` bash
sudo systemctl start fastapi
sudo systemctl enable fastapi
sudo systemctl status fastapi
```
---

## 10. Instalar e configurar Nginx

Instalar:

``` bash
sudo apt install nginx -y
```

Criar configuração:

``` bash
sudo nano /etc/nginx/sites-available/fastapi
```

Conteúdo:

``` nginx
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

Ativar configuração:

``` bash
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled
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
* Acompanhar os logs
* Utilizar banco gerenciado (RDS)
---

## Considerações Finais

Sua API(FastAPI) estará operando em produção com:

* Alto desempenho (Gunicorn + Uvicorn)
* Proxy reverso (Nginx)
* Segurança utilizando HTTPS (opcional)
---

