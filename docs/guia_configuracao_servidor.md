# Guia de Configuração de Servidor Seguro para produção: Debian 13 (VPS)
Este documento apresenta o passo a passo completo para configurar sua VPS do zero, garantindo a segurança do sistema e preparando o ambiente para uma aplicação Python com banco de dados MySQL e servidor web Caddy.

---

## Passo 1: Atualização Inicial e Criação de Usuário Seguro
Ao acessar a VPS pela primeira vez como `root`, o primeiro objetivo é criar um usuário comum para operar o sistema e aplicar as atualizações de segurança.

```bash
# 1. Atualize a lista de pacotes e o sistema operacional
apt update && apt upgrade -y

# 2. Crie um novo usuário seguro (substitua 'usuario_seguro' pelo nome desejado)
adduser usuario_seguro

# 3. Adicione o novo usuário ao grupo de administradores (sudo)
usermod -aG sudo usuario_seguro
```

---

## Passo 2: Endurecimento do Acesso SSH
Modificar a porta padrão do SSH e desativar o acesso direto ao root reduz drasticamente as tentativas de invasão automatizadas (ataques de força bruta).

```bash
# 1. Abra o arquivo de configuração do SSH
sudo nano /etc/ssh/sshd_config.d/custom.conf
```
*Insira as seguintes linhas no arquivo (escolha uma porta aleatória, por exemplo, 4822):*
```text
Port 4822
PermitRootLogin no
PasswordAuthentication yes
```
*(Nota: O ideal de mercado é usar Chaves SSH e definir `PasswordAuthentication no`. Caso use chaves, certifique-se de copiar sua chave pública para `~/.ssh/authorized_keys` antes de desativar as senhas).*

```bash
# 2. Reinicie o serviço SSH para aplicar as alterações
sudo systemctl restart ssh
```
*⚠️ ATENÇÃO: Não feche seu terminal atual. Abra uma nova janela de terminal e tente se conectar com o novo usuário e a nova porta (`ssh usuario_seguro@IP_DA_VPS -p 4822`) para garantir que funciona.*

---

## Passo 3: Configuração do Firewall (UFW) e Fail2Ban
O firewall controlará estritamente quais portas estão visíveis para a internet. O Fail2Ban bloqueará IPs que tentarem errar senhas no SSH.

```bash
# 1. Instale o firewall UFW e o Fail2Ban
sudo apt install ufw fail2ban -y

# 2. Defina as regras padrão de bloqueio
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 3. Libere as portas essenciais (HTTP, HTTPS e sua porta SSH customizada)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 4822/tcp

# 4. Ative o firewall
sudo ufw enable

# 5. Inicie e ative o Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## Passo 4: Instalação e Proteção do MySQL (Porta Customizada)
Configuraremos o MySQL para operar em uma porta diferente da padrão (3306), permitindo o acesso externo seguro através do firewall apenas quando necessário.

```bash
# 1. Instale o servidor MySQL
sudo apt install mariadb-server -y
```

### Porta e acesso ao banco
```bash
# 1. Abra o arquivo de configuração do MariaDB
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```
Por padrão, mantenha o banco acessível somente pela própria VPS. Altere a porta apenas se houver uma necessidade operacional concreta:
```text
port            = 53306
bind-address    = 127.0.0.1
```

```bash
# 2. Reinicie o MariaDB para aplicar
sudo systemctl restart mariadb
```
O arquivo de configuração da aplicação usa `127.0.0.1`, portanto não é necessário abrir a porta do banco no UFW. Se o acesso externo for indispensável, use VPN ou libere a porta somente para IPs confiáveis, alterando `bind-address` e a regra do firewall de forma coordenada. Nunca use `GRANT ALL ON *.*` para a aplicação nem exponha um usuário administrativo com host `%`.

---

## Passo 5: Instalação, configuração do Git e clone do repositório
Execute esta etapa conectado com o usuário comum da aplicação. Não clone o projeto nem instale dependências como `root`.

```bash
# 1. Instale o Git e as ferramentas necessárias
sudo apt install git ca-certificates -y

# 2. Configure sua identidade do Git neste servidor
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@example.com"

# 3. Clone o repositório (substitua pela URL real)
mkdir -p ~/apps
git clone https://github.com/SEU_USUARIO/conecta_vagas.git ~/apps/conecta_vagas
cd ~/apps/conecta_vagas
```

Para repositórios privados, prefira autenticação por chave SSH ou token do provedor Git. Não coloque senhas diretamente na URL do clone.

Para atualizar uma instalação existente:

```bash
cd ~/apps/conecta_vagas
git pull --ff-only
```

## Passo 6: Preparação do ambiente Python
As dependências ficam isoladas em um ambiente virtual (`venv`), executado pelo usuário comum da aplicação.

```bash
# 1. Instale Python, pip e o criador de ambientes virtuais
sudo apt install python3 python3-pip python3-venv -y

# 2. Crie e ative o ambiente virtual
cd ~/apps/conecta_vagas
python3 -m venv .venv
source .venv/bin/activate

# 3. Atualize o pip e instale as dependências
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para sair do ambiente virtual no terminal, use `deactivate`.

## Passo 7: Configuração do banco de dados da aplicação
Com o MySQL/MariaDB instalado e protegido, execute primeiro o schema e depois os scripts de dados de apoio do projeto. Essa etapa deve ocorrer antes de configurar `DATABASE_URL` no `.env`:

```bash
cd ~/apps/conecta_vagas
mysql -u root -p < dados/script_criacao_db.sql
mysql -u root -p conecta_vagas < dados/script_insert_ra.sql
mysql -u root -p conecta_vagas < dados/script_insert_serie.sql
mysql -u root -p conecta_vagas < dados/script_insert_escolas.sql
```

Depois de criar o banco, crie o arquivo de ambiente a partir do exemplo:

```bash
cd ~/apps/conecta_vagas
cp .env.example .env
chmod 600 .env
```

Gere uma chave secreta forte, sem usar uma chave publicada no repositório:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para o `.env` e configure também o SMTP:

```text
SECRET_KEY=cole_a_chave_gerada_aqui
DATABASE_URL=mysql://usuario_app:SENHA_FORTE@127.0.0.1:53306/conecta_vagas
```

Para gerar o arquivo `.env` em qualquer ambiente, use `.env.example` como base com `cp .env.example .env` e depois altere os valores. Nunca versione o `.env`, não compartilhe a `SECRET_KEY` e não registre senhas ou tokens nos logs.

Use um usuário específico da aplicação, com permissões somente no banco `conecta_vagas`. Evite expor a porta do banco à internet; se o acesso externo for indispensável, libere-a no firewall apenas para IPs confiáveis.

---

## Passo 8: Instalação e Configuração do Caddy (Proxy Reverso)
O Caddy receberá as requisições na porta 80/443, emitirá o certificado SSL automaticamente e repassará o tráfego para a sua aplicação Python (rodando localmente em uma porta interna como a 8000).

```bash
# 1. Baixe e instale o Caddy Server oficial para Debian
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy -y

# 2. Configure o Caddyfile para direcionar o domínio à sua aplicação Python
sudo nano /etc/caddy/Caddyfile
```
*Apague o conteúdo padrão do arquivo e adicione a estrutura abaixo (substitua pelo seu domínio real):*
```text
seu-dominio.com.br {
    reverse_proxy localhost:8000
}
```

```bash
# 3. Recarregue a configuração do Caddy
sudo systemctl reload caddy
```

```bash
#4.  instala a CA raiz local do Caddy no trust store da máquina
sudo caddy trust
```
---

## Passo 9: Serviço da aplicação com systemd (recomendado para produção)
Em uma VPS Linux, use o `systemd` para iniciar a aplicação automaticamente, reiniciá-la caso caia e iniciá-la junto com o sistema. O Caddy continuará recebendo o tráfego público e encaminhando-o para o Gunicorn em `127.0.0.1:8000`.

Crie o serviço abaixo, substituindo `ubuntu` pelo usuário Linux que possui o projeto:

```bash
sudo nano /etc/systemd/system/conecta-vagas.service
```

Conteúdo:

```ini
[Unit]
Description=Conecta Vagas Flask application
After=network.target mariadb.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/apps/conecta_vagas
EnvironmentFile=/home/ubuntu/apps/conecta_vagas/.env
ExecStart=/home/ubuntu/apps/conecta_vagas/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Ative, inicie e confira o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable conecta-vagas
sudo systemctl start conecta-vagas
sudo systemctl status conecta-vagas
```

Veja os logs em tempo real:

```bash
sudo journalctl -u conecta-vagas -f
```

Após atualizar o código, reinstale dependências se necessário e reinicie:

```bash
cd ~/apps/conecta_vagas
source .venv/bin/activate
python -m pip install -r requirements.txt
sudo systemctl restart conecta-vagas
```

Não use `python run.py` como servidor público em produção; ele serve para desenvolvimento/testes. O Gunicorn é o processo de aplicação usado pelo serviço, enquanto o Caddy permanece como proxy reverso e responsável pelo HTTPS.

## Passo 10: Proteção Adicional com Cloudflare (Opcional)
Para adicionar uma camada robusta de Rate Limiting e ocultar o IP real da sua VPS Hostinger:
1. Cadastre-se na [Cloudflare](https://www.cloudflare.com/) e adicione seu domínio.
2. Altere os Servidores de Nome (Nameservers) no painel da Hostinger para os fornecidos pela Cloudflare.
3. Ative a "Nuvem Laranja" (Proxy) nos registros DNS.
4. No painel da Cloudflare, navegue até **Security > WAF > Rate Limiting Rules** e crie uma regra limitando requisições excessivas por IP para evitar abusos automatizados.
