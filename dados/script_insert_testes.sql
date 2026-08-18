-- ============================================================
-- MASSA DE TESTE
-- ============================================================

INSERT IGNORE INTO serie (nome) VALUES
('1º Ano - Ensino Fundamental'),('2º Ano - Ensino Fundamental'),
('3º Ano - Ensino Fundamental'),('4º Ano - Ensino Fundamental'),
('5º Ano - Ensino Fundamental'),('6º Ano - Ensino Fundamental'),
('7º Ano - Ensino Fundamental'),('8º Ano - Ensino Fundamental'),
('9º Ano - Ensino Fundamental'),('1º Ano - Ensino Médio'),
('2º Ano - Ensino Médio'),('3º Ano - Ensino Médio');

INSERT INTO ra (nome) VALUES
('RA Plano Piloto'),('RA Taguatinga'),('RA Ceilândia'),
('RA Águas Claras'),('RA Samambaia');

INSERT INTO escola (nome,id_ra,endereco,telefone,email) VALUES
('Centro Educacional Asa Norte',1,'SGAN 610, Brasília - DF','(61) 3000-1001','contato@ceanorte.com.br'),
('Colégio Horizonte',1,'Asa Sul, Brasília - DF','(61) 3000-1002','contato@horizonte.com.br'),
('Escola Modelo Brasília',1,'EQS 308, Brasília - DF','(61) 3000-1003','contato@modelobrasilia.com.br'),
('Centro Educacional Taguatinga',2,'Taguatinga Centro, Brasília - DF','(61) 3000-1004','contato@cetaguatinga.com.br'),
('Colégio Novo Saber',2,'Taguatinga Norte, Brasília - DF','(61) 3000-1005','contato@novosaber.com.br'),
('Escola Parque Ceilândia',3,'Ceilândia Norte, Brasília - DF','(61) 3000-1006','contato@escolaparqueceil.com.br'),
('Colégio Águas Claras',4,'Águas Claras, Brasília - DF','(61) 3000-1007','contato@colegioaguasclaras.com.br'),
('Escola Samambaia Sul',5,'Samambaia Sul, Brasília - DF','(61) 3000-1008','contato@samambaiasul.com.br');

INSERT INTO usuario (nome,email,senha,cpf,telefone) VALUES
('Carlos Almeida','carlos.almeida@email.com','senha_teste_123','111.111.111-11','(61) 99111-1111'),
('Mariana Souza','mariana.souza@email.com','senha_teste_123','222.222.222-22','(61) 99222-2222'),
('João Pereira','joao.pereira@email.com','senha_teste_123','333.333.333-33','(61) 99333-3333'),
('Fernanda Oliveira','fernanda.oliveira@email.com','senha_teste_123','444.444.444-44','(61) 99444-4444'),
('Ricardo Santos','ricardo.santos@email.com','senha_teste_123','555.555.555-55','(61) 99555-5555'),
('Patrícia Costa','patricia.costa@email.com','senha_teste_123','666.666.666-66','(61) 99666-6666'),
('Lucas Rodrigues','lucas.rodrigues@email.com','senha_teste_123','777.777.777-77','(61) 99777-7777'),
('Juliana Martins','juliana.martins@email.com','senha_teste_123','888.888.888-88','(61) 99888-8888');

INSERT INTO aluno
(nome,id_serie,id_escola_atual,id_escola_desejada,turno_atual,turno_desejado,id_usuario_responsavel)
VALUES
('Pedro Almeida',7,1,4,'MANHA','MANHA',1),
('Ana Souza',7,4,1,'MANHA','MANHA',2),
('Gabriel Pereira',8,2,5,'TARDE','TARDE',3),
('Laura Oliveira',8,5,2,'TARDE','TARDE',4),
('Miguel Santos',9,3,6,'MANHA','MANHA',5),
('Beatriz Costa',9,6,3,'MANHA','MANHA',6),
('Rafael Rodrigues',10,7,1,'TARDE','TARDE',7),
('Sofia Martins',10,1,7,'TARDE','TARDE',8),
('Lucas Almeida',6,4,5,'MANHA','MANHA',1),
('Helena Souza',6,5,4,'MANHA','MANHA',2),
('Arthur Pereira',11,2,7,'TARDE','TARDE',3),
('Manuela Oliveira',11,7,2,'TARDE','TARDE',4);

INSERT INTO match_troca (id_aluno_a,id_aluno_b,status) VALUES
(1,2,'ABERTO'),(3,4,'ACEITO'),(5,6,'CONCLUIDO'),
(7,8,'RECUSADO'),(9,10,'ABERTO'),(11,12,'CONCLUIDO');

INSERT INTO mensagem (id_match,mensagem,id_remetente,lida) VALUES
(1,'Olá! Tenho interesse em realizar a troca.',1,TRUE),
(1,'Olá Pedro! Também tenho interesse. Podemos verificar os detalhes.',2,TRUE),
(1,'Perfeito. Vou verificar com meu responsável.',1,FALSE),
(2,'Olá! Vi que nossas escolas atendem às necessidades da troca.',3,TRUE),
(2,'Sim. Podemos prosseguir com a troca.',4,TRUE),
(3,'A troca foi concluída com sucesso.',5,TRUE),
(3,'Perfeito! Obrigada pela negociação.',6,TRUE),
(4,'Infelizmente não vou conseguir realizar a troca neste momento.',8,TRUE),
(5,'Olá! Você ainda tem interesse na troca?',1,FALSE),
(6,'Podemos confirmar a conclusão da troca.',3,TRUE),
(6,'Sim, está tudo certo.',4,TRUE);

INSERT INTO avaliacao (id_match,id_usuario_avaliador,nota,comentario) VALUES
(3,5,5,'Excelente experiência. Todo o processo ocorreu conforme combinado.'),
(3,6,5,'Muito boa negociação e comunicação.'),
(6,3,4,'Processo tranquilo e bem organizado.'),
(6,4,5,'Excelente experiência com a troca.');

-- ============================================================
-- CONSULTAS DE VERIFICAÇÃO
-- ============================================================

SHOW TABLES;

SELECT * FROM ra;
SELECT * FROM escola;
SELECT * FROM serie;
SELECT * FROM usuario;
SELECT * FROM aluno;
SELECT * FROM match_troca;
SELECT * FROM mensagem;
SELECT * FROM avaliacao;