# Guia de Configuração de Servidor Seguro: Debian 13 (Hostinger KVM)
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
sudo apt install mysql-server -y

# 2. Execute o script de segurança do MySQL para remover usuários anônimos e bancos de teste
sudo mysql_secure_installation
```

### Alterando a Porta e Permitindo Acesso Externo
```bash
# 3. Abra o arquivo de configuração do MySQL
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```
*Localize e altere as seguintes linhas para escutar em todas as interfaces e mudar a porta padrão para uma de sua escolha (ex: 53306):*
```text
port            = 53306
bind-address    = 0.0.0.0
```

```bash
# 4. Reinicie o MySQL para aplicar
sudo systemctl restart mysql

# 5. Crie um usuário administrativo para acesso externo (Substitua as credenciais)
sudo mysql -u root -p -e "CREATE USER 'admin_externo'@'%' IDENTIFIED BY 'SuaSenhaMuitoForte123!';"
sudo mysql -u root -p -e "GRANT ALL PRIVILEGES ON *.* TO 'admin_externo'@'%' WITH GRANT OPTION;"
sudo mysql -u root -p -e "FLUSH PRIVILEGES;"

# 6. Libere a porta customizada no Firewall do servidor
sudo ufw allow 53306/tcp
```
*🔒 Recomendação de Especialista: Deixar a porta do banco aberta para o mundo todo (`0.0.0.0`) é um risco mesmo mudando a porta. Se o seu IP de internet residencial/trabalho for fixo, mude a regra do firewall para liberar apenas o seu IP: `sudo ufw allow from SEU_IP_REIDENCIAL to any port 53306 proto tcp`.*

---

## Passo 5: Preparação do Ambiente Python (Ambiente Virtual)
Isolaremos as dependências do projeto dentro de um ambiente virtual (`venv`), rodando sob um usuário comum e nunca como root.

```bash
# 1. Instale o Python, gerenciador de pacotes e o criador de venv
sudo apt install python3 python3-pip python3-venv -y

# 2. Crie uma pasta para a sua aplicação web
mkdir -p ~/minha-aplicacao && cd ~/minha-aplicacao

# 3. Crie o ambiente virtual isolado (venv)
python3 -m venv .venv

# 4. Ative o ambiente virtual sempre que for trabalhar no projeto
source .venv/bin/activate

# 5. Exemplo de instalação de dependências dentro do ambiente
pip install pip --upgrade
# pip install fastapi uvicorn pymysql (seus pacotes aqui)
```
*Para sair do ambiente virtual no terminal, basta digitar o comando: `deactivate`.*

---

## Passo 6: Instalação e Configuração do Caddy (Proxy Reverso)
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

---

## Passo 7: Proteção Adicional com Cloudflare (Opcional)
Para adicionar uma camada robusta de Rate Limiting e ocultar o IP real da sua VPS Hostinger:
1. Cadastre-se na [Cloudflare](https://www.cloudflare.com/) e adicione seu domínio.
2. Altere os Servidores de Nome (Nameservers) no painel da Hostinger para os fornecidos pela Cloudflare.
3. Ative a "Nuvem Laranja" (Proxy) nos registros DNS.
4. No painel da Cloudflare, navegue até **Security > WAF > Rate Limiting Rules** e crie uma regra limitando requisições excessivas por IP para evitar abusos automatizados.
