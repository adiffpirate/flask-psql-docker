CREATE TYPE nome_cargo AS ENUM('Presidente', 'DepFederal', 'Senador', 'Governador', 'Prefeito');

CREATE TABLE Partido(
    Nome varchar(50) PRIMARY KEY,
    Sigla varchar(5),
    Numero int,
    Programa varchar(20000)
);

CREATE TABLE Individuo(
    Nome varchar(35) PRIMARY KEY,
    Tipo varchar(4),
    CPF_CNPJ bigint UNIQUE,
    Partido varchar(50),
    FOREIGN KEY (Partido) REFERENCES Partido(Nome) ON DELETE CASCADE
);

CREATE TABLE ProcessoJudicial(
    ProcessId int PRIMARY KEY,
    Procedente boolean,
    DataTermino date,
    Reu varchar(35),
    FOREIGN KEY (Reu) REFERENCES Individuo(Nome) ON DELETE CASCADE
);

CREATE TABLE Pleito(
    PleitoId int PRIMARY KEY,
    TotalDeVotos int
);


CREATE TABLE Candidatura(
    Candidato varchar(35),
    Ano int,
    ViceCandidato varchar(35) UNIQUE,
    Numero int NOT NULL,
    Pleito int NOT NULL,
    NomeCargo nome_cargo,
    Referencia varchar(35),
    PRIMARY KEY(Candidato,Ano),
    FOREIGN KEY (Candidato) REFERENCES Individuo(Nome) ON DELETE CASCADE,
    FOREIGN KEY (ViceCandidato) REFERENCES Individuo(Nome) ON DELETE CASCADE,
    FOREIGN KEY (Pleito) REFERENCES Pleito(PleitoId) ON DELETE CASCADE
);

CREATE TABLE Cargo(
    Candidato varchar(35),
    Ano int,
    NomeCargo nome_cargo,
    Referencia varchar(35),
    Vigencia date,
    PRIMARY KEY(Candidato,Ano),
    FOREIGN KEY (Candidato,Ano) REFERENCES Candidatura(Candidato,Ano) ON DELETE CASCADE
);


CREATE TABLE EquipeDeApoio(
    Candidato varchar(35),
    Ano int,
    Apoiador varchar(35),
    PRIMARY KEY(Apoiador,Ano),
    FOREIGN KEY (Candidato,Ano) REFERENCES Candidatura(Candidato,Ano) ON DELETE CASCADE,
    FOREIGN KEY (Apoiador) REFERENCES Individuo(Nome) ON DELETE CASCADE
);


CREATE TABLE Doacao(
    Candidato varchar(35),
    Ano int,
    Apoiador varchar(35),
    Valor int,
    PRIMARY KEY(Apoiador,Ano),
    FOREIGN KEY (Candidato,Ano) REFERENCES Candidatura(Candidato,Ano) ON DELETE CASCADE,
    FOREIGN KEY (Apoiador) REFERENCES Individuo(Nome) ON DELETE CASCADE
);
