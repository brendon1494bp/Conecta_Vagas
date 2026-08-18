-- ============================================================
-- BANCO DE DADOS - SISTEMA DE TROCA DE ALUNOS
-- SGBD: MySQL 8.0+
-- Banco: conecta_vagas
-- ============================================================

CREATE DATABASE IF NOT EXISTS conecta_vagas
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE conecta_vagas;

-- ============================================================
-- TABELAS
-- ============================================================

CREATE TABLE IF NOT EXISTS ra (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS escola (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(250) NOT NULL,
    id_ra INT,
    endereco VARCHAR(255),
    telefone VARCHAR(20),
    email VARCHAR(150),
    CONSTRAINT fk_escola_ra FOREIGN KEY (id_ra)
        REFERENCES ra(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS serie (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aluno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    id_serie INT NOT NULL,
    id_escola_atual INT NOT NULL,
    id_escola_desejada INT,
    turno_atual VARCHAR(20),
    turno_desejado VARCHAR(20),
    id_usuario_responsavel INT,
    CONSTRAINT fk_aluno_serie FOREIGN KEY (id_serie)
        REFERENCES serie(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_aluno_escola_atual FOREIGN KEY (id_escola_atual)
        REFERENCES escola(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_aluno_escola_desejada FOREIGN KEY (id_escola_desejada)
        REFERENCES escola(id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_aluno_responsavel FOREIGN KEY (id_usuario_responsavel)
        REFERENCES usuario(id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS match_troca (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno_a INT NOT NULL,
    id_aluno_b INT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ABERTO',
    data_hora_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_match_aluno_a FOREIGN KEY (id_aluno_a)
        REFERENCES aluno(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_match_aluno_b FOREIGN KEY (id_aluno_b)
        REFERENCES aluno(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_match_alunos_diferentes CHECK (id_aluno_a <> id_aluno_b),
    CONSTRAINT chk_status_match CHECK (
        status IN ('ABERTO','ACEITO','RECUSADO','CONCLUIDO','CANCELADO')
    )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mensagem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_match INT NOT NULL,
    mensagem TEXT NOT NULL,
    id_remetente INT NOT NULL,
    lida BOOLEAN NOT NULL DEFAULT FALSE,
    data_hora_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mensagem_match FOREIGN KEY (id_match)
        REFERENCES match_troca(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_mensagem_remetente FOREIGN KEY (id_remetente)
        REFERENCES usuario(id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS avaliacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_match INT NOT NULL,
    id_usuario_avaliador INT NOT NULL,
    nota INT NOT NULL,
    comentario TEXT,
    data_hora_avaliacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_avaliacao_match FOREIGN KEY (id_match)
        REFERENCES match_troca(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_avaliacao_avaliador FOREIGN KEY (id_usuario_avaliador)
        REFERENCES usuario(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_nota CHECK (nota >= 1 AND nota <= 5),
    CONSTRAINT uk_avaliacao UNIQUE (id_match, id_usuario_avaliador)
) ENGINE=InnoDB;

-- ============================================================
-- ÍNDICES
-- ============================================================

CREATE INDEX idx_escola_ra ON escola(id_ra);
CREATE INDEX idx_aluno_serie ON aluno(id_serie);
CREATE INDEX idx_aluno_escola_atual ON aluno(id_escola_atual);
CREATE INDEX idx_aluno_escola_desejada ON aluno(id_escola_desejada);
CREATE INDEX idx_aluno_responsavel ON aluno(id_usuario_responsavel);
CREATE INDEX idx_match_aluno_a ON match_troca(id_aluno_a);
CREATE INDEX idx_match_aluno_b ON match_troca(id_aluno_b);
CREATE INDEX idx_match_status ON match_troca(status);
CREATE INDEX idx_mensagem_match ON mensagem(id_match);
CREATE INDEX idx_mensagem_remetente ON mensagem(id_remetente);
CREATE INDEX idx_avaliacao_match ON avaliacao(id_match);
CREATE INDEX idx_avaliacao_usuario ON avaliacao(id_usuario_avaliador);
