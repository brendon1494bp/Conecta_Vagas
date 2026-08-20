# Conecta Vagas

## Guia de Construção do Sistema

**Versão:** 1.0\
**Tecnologia principal:** Python + Flask\
**Banco de dados:** MySQL 8+ ou MariaDB compatível\
**Prioridade de interface:** Mobile-first e altamente responsiva

------------------------------------------------------------------------

# 1. Objetivo deste documento

Este documento é o guia principal para análise, construção e evolução do
**Conecta Vagas**.

Ele deve ser compreensível tanto por:

-   pessoas desenvolvedoras;
-   estudantes e avaliadores;
-   pessoas responsáveis pela manutenção do sistema;
-   ferramentas e assistentes de IA utilizados para implementar ou
    evoluir o projeto.

Sempre que houver dúvida sobre como implementar uma funcionalidade,
deve-se priorizar, nesta ordem:

1.  o objetivo de negócio;
2.  a segurança e integridade dos dados;
3.  a simplicidade da solução;
4.  a experiência do usuário, principalmente em dispositivos móveis;
5.  a organização e facilidade de manutenção do código.

O sistema **não deve ser excessivamente arquitetado**. A solução deve
demonstrar boas práticas sem introduzir complexidade desnecessária.

------------------------------------------------------------------------

# 2. Visão geral do sistema

O **Conecta Vagas** é uma plataforma que ajuda pais ou responsáveis por
alunos da rede pública a encontrar outras famílias interessadas em
realizar uma troca compatível de escola e/ou turno.

A ideia central é semelhante a um sistema de *matching*:

1.  um responsável cadastra uma solicitação de troca para um aluno;
2.  informa a situação atual e a situação desejada;
3.  o sistema procura automaticamente outra solicitação compatível;
4.  quando encontra uma compatibilidade, cria um **match**;
5.  os envolvidos são notificados;
6.  os responsáveis podem negociar por meio de um chat privado;
7.  a negociação pode ser concluída, recusada ou cancelada.

## Exemplo simplificado

### Solicitação A

-   Escola atual: Escola A
-   Turno atual: Matutino
-   Escola desejada: Escola B
-   Turno desejado: Vespertino
-   Série: 5º ano

### Solicitação B

-   Escola atual: Escola B
-   Turno atual: Vespertino
-   Escola desejada: Escola A
-   Turno desejado: Matutino
-   Série: 5º ano

Essas solicitações são potencialmente compatíveis porque a situação
desejada de cada uma corresponde à situação atual da outra.

------------------------------------------------------------------------

# 3. Princípios fundamentais

Todo o sistema deve seguir os princípios abaixo.

## 3.1 KISS --- Keep It Simple

Escolher a solução mais simples que resolva corretamente o problema.

Não adicionar:

-   microserviços;
-   filas;
-   eventos distribuídos;
-   CQRS;
-   múltiplas abstrações;
-   padrões complexos;

sem uma necessidade concreta.

O sistema deve começar como um **monólito modular Flask**.

## 3.2 DRY --- Don't Repeat Yourself

Regras importantes não devem ser copiadas em vários locais.

Exemplos:

-   regra de criação de match deve estar centralizada;
-   validação de acesso a uma solicitação deve ser reutilizável;
-   envio de e-mails deve passar por um serviço apropriado;
-   constantes de status não devem ser repetidas como strings mágicas em
    dezenas de arquivos.

DRY não significa criar abstrações prematuras. Duas ou poucas linhas
semelhantes podem continuar simples quando uma abstração tornaria o
código mais difícil de entender.

## 3.3 Clean Code

O código deve:

-   usar nomes claros;
-   ter funções pequenas e com responsabilidade bem definida;
-   evitar comentários que apenas repitam o código;
-   comentar regras de negócio importantes quando necessário;
-   evitar funções gigantes;
-   evitar condicionais profundamente aninhadas;
-   preferir retorno antecipado quando melhorar a legibilidade;
-   separar regras de negócio da camada HTTP.

Exemplo de bom nome:

``` python
buscar_match_compativel()
```

Exemplo de nome ruim:

``` python
processar()
```

## 3.4 Didática

A arquitetura deve ser fácil de explicar.

Uma pessoa que abra o projeto deve conseguir responder rapidamente:

-   onde ficam as rotas?
-   onde ficam os modelos?
-   onde estão as regras de match?
-   onde ficam os formulários?
-   onde estão os testes?
-   como iniciar o sistema?

O projeto deve preferir soluções explícitas a soluções "mágicas".

## 3.5 Segurança por padrão

Nenhuma tela ou rota deve confiar apenas no que o navegador informa.

O servidor deve validar:

-   autenticação;
-   autorização;
-   propriedade dos recursos;
-   estados permitidos;
-   dados recebidos.

Exemplo: um usuário não pode editar uma solicitação apenas alterando
manualmente uma URL com o ID de outro usuário.

## 3.6 Mobile-first

O público principal provavelmente utilizará smartphones.

Portanto:

-   todas as telas devem funcionar primeiro em telas pequenas;
-   nenhuma ação importante deve depender exclusivamente de *hover*;
-   botões devem ter tamanho confortável para toque;
-   formulários devem ser simples e fáceis de preencher;
-   tabelas largas devem ser evitadas;
-   informações devem preferir cartões, listas ou blocos empilhados;
-   o sistema deve funcionar bem em conexões e dispositivos modestos.

------------------------------------------------------------------------

# 4. Escopo funcional

O sistema deve possuir inicialmente os seguintes módulos:

1.  Autenticação
2.  Recuperação de senha
3.  Perfil do usuário
4.  Dashboard
5.  Solicitações
6.  Motor de Match
7.  Matches e negociação
8.  Chat
9.  Notificações por e-mail
10. Dados de apoio, como escolas, regiões e séries

Funcionalidades como avaliações podem ser tratadas como evolução futura
e não devem aumentar a complexidade do primeiro MVP sem necessidade.

------------------------------------------------------------------------

# 5. Requisitos funcionais

## RF-01 --- Cadastro de usuário

O sistema deve permitir o cadastro de um responsável.

Campos inicialmente esperados:

-   e-mail;
-   senha;
-   confirmação de senha;

Após a exibição da tela inicial de cadastro com estes dados básicos, deve se verificar se o usuário já possui cadastro,
não possuindo, segue para uma tela de complementação do cadastro com os campos
-   CPF (obrigatório)
-   telefone(não obrigatório)

Regras:

-   e-mail deve ser único;
-   CPF, deve seguir a regra de unicidade definida;
-   senha nunca deve ser armazenada em texto puro;
-   campos obrigatórios devem ser validados no servidor;
-   o cadastro deve produzir mensagens claras em caso de erro.

## RF-02 --- Login

O usuário deve poder autenticar-se usando e-mail e senha.

A tela deve conter:

-   e-mail;
-   senha;
-   botão de entrar;
-   link para recuperação de senha;
-   link para criação de conta.

## RF-03 --- Recuperação de senha

O fluxo esperado é:

1.  usuário informa o e-mail;
2.  sistema valida se o e-mail pode receber recuperação;
3.  sistema gera um token seguro e temporário;
4.  sistema envia um link de redefinição;
5.  usuário informa uma nova senha;
6.  token é invalidado após uso ou expiração.

Nunca enviar a senha atual por e-mail.

## RF-04 --- Perfil

O usuário deve poder visualizar e editar seus próprios dados.

A tela deve permitir:

-   visualizar dados atuais;
-   editar informações pessoais;
-   editar telefone;
-   editar e-mail, respeitando validações;
-   editar endereço;
-   alterar senha em fluxo apropriado.

O usuário nunca pode editar o perfil de outro usuário.

## RF-05 --- Dashboard

Após o login, o usuário deve ter acesso a um dashboard simples.

O dashboard deve evitar elementos exagerados, poluídos ou sem utilidade.

Informações sugeridas:

-   lista de solicitacoes com seus status e link para acessá-las, link ou botões para acessar a solicitação, acessar o chat , alterar ou cancelar a solicitação
-   Seção objetiva e com instruções curtas e objetivas sobre como proceder (como criar a soloicitação, e o que fazer depois da solicitação, caso tenham match)
- também ter links para os documentos de 

Cada item deve permitir acesso rápido à funcionalidade correspondente.

## RF-06 --- Criar solicitação

O responsável deve poder cadastrar uma solicitação de troca.

Campos:

### Dados do aluno

-   nome do aluno;
-   série.
-   endereco do aluno

### Situação atual

-   escola atual;
-   turno atual.

### Situação desejada

-   RA desejada
-   escola desejada;
-   turno desejado.

### Informações adicionais

-   motivo da troca - não obrigatório.

A escola desejada deve ser filtrada pela região
selecionada.

A relação entre os campos deve ser simples e clara:

``` text
RA (Região administrativa) desejada
        ↓
Filtra escolas disponíveis
        ↓
Escola desejada
```

O sistema deve validar que os dados são coerentes.

## RF-07 --- Listar solicitações

O usuário deve poder visualizar suas próprias solicitações.

Cada item deve mostrar, de forma resumida:

-   aluno;
-   escola atual;
-   escola desejada;
-   turno atual;
-   turno desejado;
-   série;
-   status;
-   data de criação ou última atualização.

A interface mobile deve preferir cartões empilhados em vez de tabelas
largas.

## RF-08 --- Visualizar solicitação

O usuário deve poder abrir uma solicitação e visualizar todos os seus
detalhes.

A tela deve apresentar:

-   dados do aluno;
-   situação atual;
-   situação desejada;
-   motivo;
-   status;
-   histórico ou informações relevantes do match, quando houver;
-   ações disponíveis de acordo com o estado atual.

## RF-09 --- Editar solicitação

Uma solicitação pode ser editada somente quando seu estado permitir.

Regra inicial sugerida:

-   `DISPONIVEL`: pode editar;
-   `EM_NEGOCIACAO`: edição bloqueada ou tratada com extrema cautela;
-   `CONCLUIDA`: não pode editar;
-   `CANCELADA`: não pode editar.

Se a edição alterar os critérios de compatibilidade, o sistema deve
considerar novamente a busca por match quando a solicitação estiver
disponível.

## RF-10 --- Cancelar solicitação

O usuário pode cancelar uma solicitação disponível.

O cancelamento deve:

-   pedir confirmação;
-   registrar o novo status;
-   impedir novos matches;
-   preservar os dados para histórico quando necessário.

Preferir cancelamento lógico a exclusão física quando houver necessidade
de rastreabilidade.

## RF-11 --- Busca automática de match

Sempre que uma solicitação elegível for criada ou alterada, o sistema
deve procurar uma solicitação compatível.

A compatibilidade inicial deve considerar:

``` text
A.escola_desejada = B.escola_atual
A.escola_atual    = B.escola_desejada

A.turno_desejado  = B.turno_atual
A.turno_atual     = B.turno_desejado

A.serie           = B.serie
```

Além disso:

-   as duas solicitações devem estar disponíveis;
-   não podem pertencer ao mesmo usuário, salvo se futuramente houver
    uma regra diferente;
-   uma solicitação já vinculada a uma negociação ativa não deve receber
    outro match ativo.

A implementação exata deve ficar centralizada em um serviço de domínio.

## RF-12 --- Criação do match

Ao encontrar uma solicitação compatível:

1.  verificar novamente a disponibilidade das duas solicitações;
2.  criar o registro de match;
3.  atualizar os estados necessários;
4.  enviar notificações;
5.  liberar ou preparar o fluxo de negociação.

A criação deve ocorrer de forma transacional para reduzir o risco de uma
solicitação entrar simultaneamente em dois matches.

## RF-13 --- Negociação e confirmação

O projeto deve trabalhar com dois conceitos separados:

### Status da solicitação

Sugestão inicial:

-   `DISPONIVEL`
-   `EM_NEGOCIACAO`
-   `CONCLUIDA`
-   `CANCELADA`

### Status do match

Sugestão inicial:

-   `CRIADO`
-   `ATIVO`
-   `RECUSADO`
-   `CONCLUIDO`
-   `CANCELADO`

Os nomes definitivos podem ser ajustados, mas os dois ciclos de vida
devem permanecer conceitualmente separados.

## RF-14 --- Recusar match

Quando um match for recusado:

-   o match deve registrar a recusa;
-   o chat deve respeitar a regra de encerramento;
-   as solicitações devem voltar a `DISPONIVEL`, quando a regra de
    negócio permitir;
-   as solicitações devem poder participar de novos matches.

## RF-15 --- Concluir negociação

Quando os envolvidos concluírem a negociação:

-   o match deve ser marcado como `CONCLUIDO`;
-   as solicitações correspondentes devem ser marcadas como `CONCLUIDA`;
-   novas negociações não devem ser criadas para essas solicitações.

O sistema não deve fingir que controla a efetiva matrícula escolar se
essa integração não existir. O status representa a conclusão do processo
dentro da plataforma.

## RF-16 --- Chat

Cada match pode possuir uma conversa privada.

A tela do chat deve permitir:

-   visualizar mensagens em ordem cronológica;
-   enviar mensagem;
-   indicar mensagens não lidas, quando aplicável;
-   atualizar a conversa de maneira adequada à implementação escolhida.

Inicialmente, não é obrigatório utilizar WebSocket.

Uma implementação simples pode:

-   atualizar periodicamente;
-   recarregar mensagens de maneira controlada;
-   ou utilizar WebSocket posteriormente.

A simplicidade deve prevalecer no MVP.

## RF-17 --- Segurança do chat

Um usuário só pode:

-   visualizar um chat se participar do match;
-   enviar mensagens se participar do match;
-   enviar mensagens enquanto o estado do match permitir.

O servidor deve validar essas regras.

## RF-18 --- Notificações por e-mail

O sistema deve enviar e-mails para eventos relevantes, por exemplo:

-   recuperação de senha;
-   novo match encontrado;
-   atualização importante da negociação.

O envio deve estar isolado em um serviço.

A regra de negócio não deve conter diretamente detalhes específicos de
SMTP.

------------------------------------------------------------------------

# 6. Fluxos principais

## 6.1 Fluxo de cadastro e acesso

``` text
Usuário acessa sistema
        ↓
Ainda não possui conta?
   ┌────┴────┐
   │         │
  Sim       Não
   │         │
Cadastro    Login
   │         │
   └────┬────┘
        ↓
    Dashboard
```

## 6.2 Fluxo de criação de solicitação

``` text
Dashboard
    ↓
Nova solicitação
    ↓
Preenche dados
    ↓
Validação
    ↓
Salva solicitação
    ↓
Busca match compatível
    │
    ├── Não encontrou
    │       ↓
    │   DISPONIVEL
    │
    └── Encontrou
            ↓
      Cria match
            ↓
      Notifica usuários
            ↓
      Inicia negociação
```

## 6.3 Fluxo de negociação

``` text
Match criado
     ↓
Usuários notificados
     ↓
Negociação disponível
     ↓
Chat
     │
 ┌───┴───────────────┐
 │                   │
Concluído          Recusado/
 │                 Cancelado
 ↓                   ↓
CONCLUIDO        Solicitações
                 voltam a DISPONIVEL
                 quando permitido
```

## 6.4 Fluxo de acesso ao chat

``` text
Usuário abre solicitação
        ↓
Existe match relacionado?
        │
   ┌────┴────┐
   │         │
  Não       Sim
   │         │
Nenhum      Exibir ação
chat        "Abrir conversa"
              ↓
       Validar participação
              ↓
            Chat
```

------------------------------------------------------------------------

# 7. Telas esperadas

## 7.1 Tela de login

Objetivo: acesso rápido e simples.

Elementos:

-   logo ou nome do sistema;
-   campo de e-mail;
-   campo de senha;
-   botão principal "Entrar";
-   link "Esqueci minha senha";
-   link "Criar conta".

Em mobile:

-   formulário em largura confortável;
-   botão destacado;
-   sem necessidade de zoom;
-   teclado apropriado para cada tipo de campo.

## 7.2 Tela de cadastro

Deve ser dividida visualmente em grupos simples:

1.  email
2.  senha.
3.  confirmação da senha.

Em mobile, evitar uma tela excessivamente longa e confusa. Pode utilizar
seções claramente identificadas, mantendo o formulário em uma única
experiência simples.

## 7.2.2 Tela de continuidade do cadastro

Após a confirmação de que se trata de um novo usuário, deve seguir para a tela que exija o CPF do resposnável e que permita também colocar o telefone sem obrigatoriedade

1.  cpf
2. telefone

Em mobile, evitar uma tela excessivamente longa e confusa. Pode utilizar
seções claramente identificadas, mantendo o formulário em uma única
experiência simples.

## 7.3 Dashboard

Estrutura sugerida:

``` text
[Olá, Nome]

[ Solicitações ativas ]
[ Negociações ]

Minhas solicitações recentes

[ Card da solicitação ]
Aluno
Escola A → Escola B
Matutino → Vespertino
Status
[ Ver detalhes ]
```

Em telas maiores, os cartões podem ser organizados em mais colunas.

## 7.4 Lista de solicitações

Cada solicitação deve ser um cartão.

Exemplo conceitual:

``` text
Aluno: João

Escola atual
Escola A

Deseja
Escola B

Matutino → Vespertino

Status: DISPONIVEL

[ Ver detalhes ]
```

## 7.5 Formulário de solicitação

Ordem sugerida:

### Seção 1 --- Aluno

-   nome;
-   série.

### Seção 2 --- Situação atual

-   escola atual;
-   turno atual.

### Seção 3 --- Situação desejada

-   RA(Região administrativa) desejada
-   escola desejada;
-   turno desejado.

### Seção 4 --- Motivo

-   motivo da solicitação - Não é obrigatório

Botão final:

``` text
Salvar solicitação
```

Em edição:

``` text
Salvar alterações
```

## 7.6 Detalhe da solicitação

Deve apresentar informações de leitura fácil, agrupadas.

Ações devem depender do status.

Exemplos:

### DISPONIVEL

-   editar;
-   cancelar.

### EM_NEGOCIACAO

-   ver negociação;
-   abrir chat;
-   cancelar negociação, se permitido.

### CONCLUIDA

-   visualizar resumo.

### CANCELADA

-   visualizar histórico;
-   eventualmente permitir nova solicitação.

## 7.7 Tela do match

Deve explicar claramente que uma compatibilidade foi encontrada.

Pode mostrar, sem expor informações desnecessárias:

-   resumo da própria solicitação;
-   resumo da compatibilidade;
-   status;
-   ações disponíveis.

O sistema deve tomar cuidado para não expor dados pessoais antes do
momento apropriado.

## 7.8 Tela do chat

Em mobile:

-   mensagens ocupam a maior parte da tela;
-   área de digitação permanece facilmente acessível;
-   botão de enviar é adequado para toque;
-   textos longos devem quebrar corretamente;
-   não utilizar elementos pequenos demais.

Estrutura conceitual:

``` text
← Voltar

Negociação

---------------------
Mensagem recebida

          Minha mensagem
---------------------

[ Digite uma mensagem... ] [Enviar]
```

------------------------------------------------------------------------

# 8. Requisitos não funcionais

## RNF-01 --- Responsividade

Todas as telas devem ser extremamente responsivas.

A implementação deve seguir **mobile-first**.

A interface deve ser testada pelo menos em larguras aproximadas de:

-   320 px;
-   375 px;
-   414 px;
-   tablet;
-   desktop.

Não utilizar largura fixa que provoque rolagem horizontal.

## RNF-02 --- Usabilidade

O sistema deve:

-   usar linguagem clara;
-   informar erros de forma compreensível;
-   confirmar ações destrutivas;
-   manter navegação consistente;
-   evitar excesso de informação;
-   ter botões e campos facilmente utilizáveis em telas sensíveis ao
    toque.

## RNF-03 --- Desempenho

Para o escopo inicial:

-   evitar consultas desnecessárias;
-   criar índices para campos utilizados em filtros e relacionamentos;
-   evitar o problema N+1 nas consultas ORM;
-   paginar listas caso o volume cresça;
-   não carregar dados que a tela não utiliza.

## RNF-04 --- Segurança

O sistema deve possuir:

-   senhas armazenadas com hash seguro;
-   proteção CSRF para formulários;
-   validação no servidor;
-   proteção contra acesso indevido;
-   consultas parametrizadas por meio do ORM;
-   gerenciamento seguro de sessão;
-   segredos em variáveis de ambiente;
-   tokens de recuperação temporários e seguros.

Arquivos `.env` nunca devem ser versionados com segredos reais.

## RNF-05 --- Manutenibilidade

O código deve ser:

-   modular;
-   previsível;
-   fácil de localizar;
-   testável;
-   documentado no nível necessário.

Cada módulo deve possuir uma responsabilidade clara.

## RNF-06 --- Testabilidade

Regras importantes devem possuir testes automatizados.

Prioridade inicial:

1.  autenticação;
2.  criação de solicitação;
3.  regra de match;
4.  regras de status;
5.  autorização;
6.  chat.

A regra de match é uma das partes mais importantes para testes.

## RNF-07 --- Compatibilidade de banco

O sistema deve funcionar com MySQL 8+ ou MariaDB compatível.

A implementação deve evitar dependências desnecessárias de recursos
exclusivos de um único banco quando isso dificultar a portabilidade
entre os dois.

------------------------------------------------------------------------

# 9. Arquitetura recomendada

A arquitetura inicial será um **monólito modular**.

Isso significa:

-   uma aplicação principal;
-   um banco de dados principal;
-   módulos organizados por funcionalidade;
-   regras de negócio isoladas quando necessário.

Não utilizar microserviços no MVP.

## Estrutura recomendada

``` text
conecta_vagas/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── escola.py
│   │   ├── serie.py
│   │   ├── solicitacao.py
│   │   ├── match.py
│   │   └── mensagem.py
│   │
│   ├── auth/
│   │   ├── routes.py
│   │   ├── forms.py
│   │   └── templates/
│   │
│   ├── dashboard/
│   │   ├── routes.py
│   │   └── templates/
│   │
│   ├── solicitacoes/
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── services.py
│   │   └── templates/
│   │
│   ├── matches/
│   │   ├── routes.py
│   │   ├── services.py
│   │   └── templates/
│   │
│   ├── chat/
│   │   ├── routes.py
│   │   ├── services.py
│   │   └── templates/
│   │
│   ├── perfil/
│   │   ├── routes.py
│   │   ├── forms.py
│   │   └── templates/
│   │
│   ├── services/
│   │   └── email_service.py
│   │
│   ├── utils/
│   │   ├── decorators.py
│   │   └── security.py
│   │
│   └── templates/
│       ├── base.html
│       └── components/
│
├── migrations/
├── tests/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

------------------------------------------------------------------------

# 10. Responsabilidade de cada camada

## 10.1 Rotas

As rotas devem cuidar principalmente de HTTP.

Fluxo esperado:

``` text
Receber requisição
        ↓
Validar formulário/entrada
        ↓
Verificar autenticação/autorização
        ↓
Chamar serviço ou regra apropriada
        ↓
Retornar resposta ou renderizar tela
```

Uma rota não deve conter uma grande quantidade de regra de negócio.

## 10.2 Models

Representam:

-   entidades;
-   relacionamentos;
-   regras simples diretamente relacionadas à entidade.

Evitar transformar os models em locais com centenas de linhas de regras
complexas sem necessidade.

## 10.3 Forms

Devem concentrar validações de entrada relacionadas ao formulário.

Mesmo com validação no frontend, a validação do servidor continua
obrigatória.

## 10.4 Services

Devem ser utilizados principalmente para regras de negócio relevantes.

Exemplos:

``` text
criar_solicitacao()
buscar_match_compativel()
criar_match()
recusar_match()
concluir_match()
enviar_email_match()
```

Não criar uma camada de serviço para cada operação trivial apenas por
obrigação arquitetural.

## 10.5 Templates

Devem focar em apresentação.

Evitar colocar regras complexas de negócio dentro de templates.

## 10.6 Utils

Devem conter utilitários genuinamente reutilizáveis.

Não utilizar `utils.py` como um local genérico para qualquer código sem
categoria.

------------------------------------------------------------------------

# 11. Regra de ouro das rotas

Uma rota ideal deve ser curta e fácil de ler.

Conceitualmente:

``` python
@bp.post("/solicitacoes")
@login_required
def criar():
    form = SolicitacaoForm()

    if not form.validate_on_submit():
        return render_template("solicitacoes/form.html", form=form)

    solicitacao = solicitacao_service.criar(
        usuario=current_user,
        dados=form.data
    )

    match_service.procurar_e_processar(solicitacao)

    return redirect(url_for("solicitacoes.detalhe", id=solicitacao.id))
```

O objetivo não é copiar exatamente esse código, mas manter esta
separação:

``` text
HTTP → validação → serviço/regra → resposta
```

------------------------------------------------------------------------

# 12. Modelo de dados inicial

Entidades principais:

``` text
Usuario
    │
    └── Solicitação
              │
              ├── Escola atual
              ├── Escola desejada
              ├── Série
              │
              └── Match
                    │
                    └── Mensagens
```

Tabelas principais esperadas:

-   `usuario`
-   `ra` ou outra entidade regional, se necessária
-   `escola`
-   `serie`
-   `solicitacao`
-   `match_troca`
-   `mensagem`

## Solicitação

Campos conceituais:

-   id;
-   nome_aluno;
-   id_serie;
-   id_escola_atual;
-   id_escola_desejada;
-   turno_atual;
-   turno_desejado;
-   id_usuario_responsavel;
-   motivo_troca;
-   status;
-   data_criacao;
-   data_atualizacao.

## Match

Campos conceituais:

-   id;
-   id_solicitacao_a;
-   id_solicitacao_b;
-   status;
-   data_hora_criacao;
-   data_hora_atualizacao.

## Mensagem

Campos conceituais:

-   id;
-   id_match;
-   id_remetente;
-   mensagem;
-   data_hora_envio;
-   data_hora_leitura.

------------------------------------------------------------------------

# 13. Integridade e concorrência

A regra:

> "uma solicitação não pode participar de dois matches ativos
> simultaneamente"

é uma regra crítica.

A criação do match deve:

1.  buscar candidato;
2.  verificar novamente os estados;
3.  criar o match;
4.  alterar os estados das solicitações;
5.  confirmar a transação.

Essas operações devem ocorrer de maneira consistente.

A implementação concreta pode utilizar transações e mecanismos
apropriados do MySQL/MariaDB.

Não assumir que:

``` python
if solicitacao.status == "DISPONIVEL":
```

por si só é suficiente em cenários concorrentes.

------------------------------------------------------------------------

# 14. Status como regras explícitas

Evitar alterações arbitrárias de status.

O sistema deve ter transições permitidas claramente definidas.

Exemplo:

``` text
DISPONIVEL
    ├── criar match → EM_NEGOCIACAO
    └── cancelar → CANCELADA

EM_NEGOCIACAO
    ├── concluir → CONCLUIDA
    ├── recusar → DISPONIVEL
    └── cancelar → DISPONIVEL ou CANCELADA

CONCLUIDA
    └── estado final

CANCELADA
    └── estado final
```

Se houver necessidade futura, essa regra pode ser centralizada em uma
estrutura específica de transições.

Para o MVP, não criar uma máquina de estados complexa sem necessidade.

------------------------------------------------------------------------

# 15. Autorização

Para cada recurso sensível, verificar explicitamente:

## Solicitação

O usuário atual é o proprietário?

## Match

O usuário atual participa de uma das solicitações?

## Mensagem

O remetente participa do match?

Nunca confiar em IDs enviados pelo navegador para decidir autorização.

------------------------------------------------------------------------

# 16. Convenções de código

## Nomes

Preferir nomes descritivos.

Bom:

``` python
solicitacao
match_compativel
usuario_responsavel
buscar_solicitacoes_disponiveis
```

Evitar:

``` python
x
dados2
obj
proc
teste_final_novo
```

## Funções

Preferir funções com uma responsabilidade principal.

Evitar:

``` python
def processar_tudo():
```

quando ela:

-   valida formulário;
-   cria solicitação;
-   procura match;
-   envia e-mail;
-   grava log;
-   atualiza tela.

Separar em operações compreensíveis.

## Constantes

Status devem ser centralizados.

Evitar espalhar:

``` python
if status == "EM_NEGOCIACAO":
```

por todo o projeto sem uma definição central.

Pode-se utilizar constantes ou `Enum`, mantendo a solução simples.

------------------------------------------------------------------------

# 17. Tratamento de erros

Erros devem ser claros para usuários e úteis para desenvolvedores.

Usuário:

> "Não foi possível salvar sua solicitação. Verifique os campos
> destacados."

Log técnico:

-   erro detalhado;
-   contexto apropriado;
-   sem registrar senha ou dados secretos.

Não exibir stack traces em produção.

------------------------------------------------------------------------

# 18. Configuração por ambiente

O projeto deve separar configuração de:

-   desenvolvimento;
-   testes;
-   produção.

Exemplos de variáveis:

``` text
SECRET_KEY
DATABASE_URL
MAIL_SERVER
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
MAIL_USE_TLS
```

O arquivo `.env.example` deve documentar as variáveis sem conter
segredos reais.

------------------------------------------------------------------------

# 19. Dependências sugeridas

A escolha final pode ser ajustada, mas o conjunto inicial deve
permanecer simples.

Sugestões:

-   Flask;
-   Flask-SQLAlchemy;
-   Flask-Migrate;
-   Flask-Login;
-   Flask-WTF;
-   driver MySQL/MariaDB compatível;
-   biblioteca de carregamento de variáveis de ambiente;
-   biblioteca de testes.

Não adicionar dependências apenas por conveniência momentânea se uma
solução simples já existir no projeto.

------------------------------------------------------------------------

# 20. Estratégia de interface

A interface deve ser:

-   limpa;
-   moderna sem excesso visual;
-   acessível;
-   rápida;
-   orientada à tarefa.

Prioridades:

``` text
1. Clareza
2. Facilidade de uso
3. Responsividade
4. Consistência
5. Aparência
```

A aparência não deve prejudicar a clareza.

Não adicionar:

-   animações excessivas;
-   gráficos sem informação útil;
-   dashboards poluídos;
-   múltiplas cores sem propósito;
-   elementos decorativos que aumentem a complexidade.

------------------------------------------------------------------------

# 21. Critérios de qualidade antes de considerar uma funcionalidade pronta

Uma funcionalidade está pronta quando:

-   [ ] atende ao requisito funcional;
-   [ ] funciona em mobile;
-   [ ] possui validação no servidor;
-   [ ] possui autorização adequada;
-   [ ] trata erros esperados;
-   [ ] não duplica regra de negócio importante;
-   [ ] possui nomes claros;
-   [ ] não introduz complexidade desnecessária;
-   [ ] possui teste quando a regra é relevante;
-   [ ] não quebra funcionalidades existentes.

------------------------------------------------------------------------

# 22. Ordem sugerida de implementação

## Fase 1 --- Base

1.  criar repositório;
2.  configurar ambiente virtual;
3.  criar estrutura Flask;
4.  configurar MySQL/MariaDB;
5.  configurar SQLAlchemy;
6.  configurar migrations;
7.  configurar variáveis de ambiente;
8.  criar layout base responsivo.

## Fase 2 --- Autenticação

1.  cadastro;
2.  login;
3.  logout;
4.  proteção de rotas;
5.  recuperação de senha.

## Fase 3 --- Perfil

1.  visualizar perfil;
2.  editar dados;
3.  alterar senha.

## Fase 4 --- Dados de apoio

1.  escolas;
2.  regiões/localidades;
3.  séries;
4.  turnos.

## Fase 5 --- Solicitações

1.  criar;
2.  listar;
3.  visualizar;
4.  editar;
5.  cancelar;
6.  controlar status.

## Fase 6 --- Motor de match

1.  implementar consulta de compatibilidade;
2.  validar série;
3.  validar escolas;
4.  validar turnos;
5.  impedir match duplicado;
6.  garantir consistência transacional;
7.  criar testes.

## Fase 7 --- Negociação

1.  tela de match;
2.  estados;
3.  aceitar/recusar conforme fluxo definido;
4.  concluir.

## Fase 8 --- Chat

1.  listar mensagens;
2.  enviar mensagens;
3.  validar participação;
4.  indicar leitura, se implementado.

## Fase 9 --- Notificações

1.  recuperação de senha;
2.  match encontrado;
3.  outros eventos relevantes.

## Fase 10 --- Qualidade final

1.  testes;
2.  revisão de segurança;
3.  testes em mobile;
4.  revisão de responsividade;
5.  revisão de mensagens de erro;
6.  limpeza de código;
7.  documentação de execução.

------------------------------------------------------------------------

# 23. Orientação específica para implementação por IA

Ao utilizar uma IA para construir ou evoluir o sistema, a IA deve seguir
estas regras:

1.  não inventar funcionalidades fora do requisito sem justificar;
2.  não alterar regras de negócio existentes silenciosamente;
3.  priorizar o código mais simples e legível;
4.  verificar o padrão existente antes de criar novos padrões;
5.  reutilizar serviços e componentes existentes quando apropriado;
6.  não criar abstrações excessivas;
7.  separar HTTP de regra de negócio;
8.  validar autorização no servidor;
9.  considerar mobile em toda nova tela;
10. criar ou atualizar testes para regras críticas;
11. explicar alterações arquiteturais relevantes;
12. manter compatibilidade com MySQL/MariaDB;
13. não armazenar segredos no código;
14. não armazenar senhas em texto puro.

Antes de criar uma nova camada, classe ou padrão, perguntar
conceitualmente:

> "Isso realmente simplifica o sistema ou apenas parece mais
> sofisticado?"

Se aumentar a complexidade sem benefício concreto, não deve ser criado.

------------------------------------------------------------------------

# 24. Decisão arquitetural final

A arquitetura padrão do Conecta Vagas será:

> **Aplicação Flask monolítica e modular, organizada principalmente por
> domínio de negócio, utilizando SQLAlchemy para persistência,
> MySQL/MariaDB como banco de dados, Blueprints para módulos HTTP e uma
> camada de serviços apenas para regras de negócio relevantes.**

O sistema deve priorizar:

``` text
Simplicidade
    ↓
Clareza
    ↓
Segurança
    ↓
Organização
    ↓
Testabilidade
    ↓
Evolução
```

E não:

``` text
Sofisticação arquitetural
    ↓
Complexidade
    ↓
Mais abstrações
    ↓
Mais dificuldade para entender
```

------------------------------------------------------------------------

# 25. Resumo das regras essenciais

1.  Uma solicitação pertence a um responsável.
2.  Uma solicitação possui situação atual e situação desejada.
3.  Um match relaciona duas solicitações compatíveis.
4.  Solicitações e matches possuem ciclos de vida separados.
5.  Uma solicitação não deve participar de dois matches ativos
    simultaneamente.
6.  A criação do match deve ser consistente e transacional.
7.  O chat pertence a um match.
8.  Apenas participantes podem acessar o chat.
9.  O servidor sempre valida autenticação e autorização.
10. Senhas são armazenadas somente com hash seguro.
11. Todas as telas são construídas com prioridade mobile-first.
12. O código deve seguir KISS, DRY e Clean Code.
13. A arquitetura deve ser simples, explícita e didática.
14. Funcionalidades devem ser adicionadas apenas quando agregarem valor
    real.
15. A regra de negócio central --- o matching --- deve permanecer clara,
    centralizada e bem testada.

------------------------------------------------------------------------

# 26. Próximos artefatos recomendados

Após este guia, os próximos documentos ou etapas recomendados são:

1.  revisão e versão definitiva do modelo de dados;
2.  diagrama entidade-relacionamento;
3.  mapa de telas e navegação;
4.  definição formal das regras de status e transições;
5.  critérios exatos do algoritmo de match;
6.  backlog de implementação;
7.  estrutura inicial do projeto Flask;
8.  primeiro conjunto de migrations;
9.  protótipo responsivo das telas principais.

Este documento deve servir como referência central durante todas essas
etapas.
