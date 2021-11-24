-- verifica se candidato já se candidatou a um cargo no ano determinado
CREATE OR REPLACE FUNCTION check_candidato() RETURNS trigger AS $check_candidato$
BEGIN
    IF (
        EXISTS (
            SELECT (Candidato, Ano) FROM Candidatura WHERE (Candidato = new.Candidato AND Ano = new.Ano)
        ) OR EXISTS (
            SELECT (ViceCandidato, Ano) FROM Candidatura WHERE (ViceCandidato = new.Candidato AND Ano = new.Ano)
        )
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. Este candidato já se candidatou a um cargo nesse ano.';
    ELSE
        RETURN NEW;
    END IF;
END;
$check_candidato$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaCandidatura
    BEFORE INSERT OR UPDATE ON Candidatura
    FOR EACH ROW EXECUTE PROCEDURE check_candidato();

-- verifica se o vice-candidato já se candidatou a um cargo no ano determinado
CREATE OR REPLACE FUNCTION check_vice() RETURNS trigger AS $check_vice$
BEGIN
    IF new.ViceCandidato IS NOT NULL AND (
        EXISTS (
            SELECT (Candidato, Ano) FROM Candidatura WHERE (Candidato = new.ViceCandidato AND Ano = new.Ano)
        ) OR EXISTS (
            SELECT (ViceCandidato, Ano) FROM Candidatura WHERE (ViceCandidato = new.ViceCandidato AND Ano = new.Ano)
        )
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O vice-candidato já se candidatou a um cargo nesse ano.';
    ELSE
        RETURN NEW;
    END IF;
END;
$check_vice$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaVice
    BEFORE INSERT OR UPDATE ON Candidatura
    FOR EACH ROW EXECUTE PROCEDURE check_vice();

-- verifica se o candidato e o vice são ficha-limpa
CREATE OR REPLACE FUNCTION check_ficha() RETURNS trigger AS $check_ficha$
BEGIN
    IF EXISTS (
        SELECT (Reu, Procedente, DataTermino) FROM ProcessoJudicial WHERE (Reu = new.Candidato AND Procedente = TRUE AND (date_part('year', DataTermino) - new.Ano) < 5)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O candidato não é ficha limpa.';
    END IF;
    IF new.ViceCandidato IS NOT NULL AND EXISTS (
        SELECT (Reu, Procedente, DataTermino) FROM ProcessoJudicial WHERE (Reu = new.ViceCandidato AND Procedente = TRUE AND (date_part('year', DataTermino) - new.Ano) < 5)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O vice-candidato não é ficha limpa.';  
    END IF;
    RETURN NEW;
END;
$check_ficha$ LANGUAGE plpgsql;

-- verifica se o candidato e o vice são filiados a um partido
CREATE OR REPLACE FUNCTION check_partido() RETURNS trigger AS $check_partido$
BEGIN
    IF EXISTS (
        SELECT (Nome, Partido) FROM Individuo WHERE (Nome = new.Candidato AND Partido IS NULL)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O candidato não é filiado a um partido.';
    END IF;
    IF new.ViceCandidato IS NOT NULL AND EXISTS (
        SELECT (Nome, Partido) FROM Individuo WHERE (Nome = new.ViceCandidato AND Partido IS NULL)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O vice-candidato não é filiado a um partido.';  
    END IF;
    RETURN NEW;
END;
$check_partido$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaPartido
    BEFORE INSERT OR UPDATE ON Candidatura
    FOR EACH ROW EXECUTE PROCEDURE check_partido();

-- muda data de término do processo quando inserir procedente true/false
CREATE OR REPLACE FUNCTION check_proc() RETURNS trigger AS $check_proc$
BEGIN
    IF (old.Procedente IS NULL) AND (new.Procedente IS NOT NULL) AND (new.DataTermino IS NULL) AND (old.DataTermino IS NULL) THEN
        new.DataTermino := now();
    END IF;
    RETURN NEW;
END;
$check_proc$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaDataTermino
    AFTER UPDATE ON ProcessoJudicial
    FOR EACH ROW EXECUTE PROCEDURE check_proc();


-- Cada cargo deve ter uma quantidade de eleitos – por exemplo, a presidência só pode ter um único
-- eleito; o cargo de deputado federal pode ter até 500 eleitos;

-- verifica se presidente adicionado é o presidente eleito
CREATE OR REPLACE FUNCTION check_pres() RETURNS trigger AS $check_pres$
BEGIN
    CREATE TEMP TABLE eleitos ON COMMIT DROP AS
    SELECT Candidato FROM Candidatura
    WHERE (Ano = new.Ano AND NomeCargo = 'Presidente' AND Referencia = new.Referencia)
    ORDER BY (SELECT TotalDeVotos FROM Pleito WHERE (Candidatura.Pleito = Pleito.PleitoId))
    DESC LIMIT 1;

    IF NOT EXISTS (SELECT * FROM eleitos WHERE Candidato = new.Candidato) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo não foi eleito ao cargo de Presidente no ano indicado.';
    ELSE
        new.Vigencia := (TO_DATE(new.Ano::TEXT || '-12-31', 'YYYY-MM-DD') + interval '1 year');
        RETURN NEW;
    END IF;
END;
$check_pres$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaPresidente
    BEFORE INSERT OR UPDATE ON Cargo
    FOR EACH ROW WHEN (new.NomeCargo = 'Presidente') EXECUTE PROCEDURE check_pres();

-- verifica se o dep. federal adicionado foi eleito
CREATE OR REPLACE FUNCTION check_dep() RETURNS trigger AS $check_dep$
BEGIN
    CREATE TEMP TABLE eleitos ON COMMIT DROP AS
    SELECT Candidato FROM Candidatura
    WHERE (Ano = new.Ano AND NomeCargo = 'DepFederal' AND Referencia = new.Referencia)
    ORDER BY (SELECT TotalDeVotos FROM Pleito WHERE (Candidatura.Pleito = Pleito.PleitoId))
    DESC LIMIT 500;

    IF NOT EXISTS (SELECT * FROM eleitos WHERE Candidato = new.Candidato) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo não foi eleito ao cargo de Deputado Federal no ano indicado.';
    ELSE
        new.Vigencia := (TO_DATE(new.Ano::TEXT || '-12-31', 'YYYY-MM-DD') + interval '1 year');
        RETURN NEW;
    END IF;
END;
$check_dep$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaDeputado
    BEFORE INSERT OR UPDATE ON Cargo
    FOR EACH ROW WHEN (new.NomeCargo = 'DepFederal') EXECUTE PROCEDURE check_dep();

-- verifica se o senador adicionado foi eleito
CREATE OR REPLACE FUNCTION check_senador() RETURNS trigger AS $check_senador$
BEGIN
    CREATE TEMP TABLE eleitos ON COMMIT DROP AS
    SELECT Candidato FROM Candidatura
    WHERE (Ano = new.Ano AND NomeCargo = 'Senador' AND Referencia = new.Referencia)
    ORDER BY (SELECT TotalDeVotos FROM Pleito WHERE (Candidatura.Pleito = Pleito.PleitoId))
    DESC LIMIT 81;

    IF NOT EXISTS (SELECT * FROM eleitos WHERE Candidato = new.Candidato) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo não foi eleito ao cargo de Senador no ano indicado.';
    ELSE
        new.Vigencia := (TO_DATE(new.Ano::TEXT || '-12-31', 'YYYY-MM-DD') + interval '1 year');
        RETURN NEW;
    END IF;
END;
$check_senador$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaSenador
    BEFORE INSERT OR UPDATE ON Cargo
    FOR EACH ROW WHEN (new.NomeCargo = 'Senador') EXECUTE PROCEDURE check_senador();

-- verifica se o governador adicionado foi eleito
CREATE OR REPLACE FUNCTION check_gov() RETURNS trigger AS $check_gov$
BEGIN
    CREATE TEMP TABLE eleitos ON COMMIT DROP AS
    SELECT Candidato FROM Candidatura
    WHERE (Ano = new.Ano AND NomeCargo = 'Governador' AND Referencia = new.Referencia)
    ORDER BY (SELECT TotalDeVotos FROM Pleito WHERE (Candidatura.Pleito = Pleito.PleitoId))
    DESC LIMIT 1;

    IF NOT EXISTS (SELECT * FROM eleitos WHERE Candidato = new.Candidato) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo não foi eleito ao cargo de Governador no ano indicado.';
    ELSE
        new.Vigencia := (TO_DATE(new.Ano::TEXT || '-12-31', 'YYYY-MM-DD') + interval '1 year');
        RETURN NEW;
    END IF;
END;
$check_gov$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaGovernador
    BEFORE INSERT OR UPDATE ON Cargo
    FOR EACH ROW WHEN (new.NomeCargo = 'Governador') EXECUTE PROCEDURE check_gov();

-- verifica se o prefeito adicionado foi eleito
CREATE OR REPLACE FUNCTION check_pref() RETURNS trigger AS $check_pref$
BEGIN
    CREATE TEMP TABLE eleitos ON COMMIT DROP AS
    SELECT Candidato FROM Candidatura
    WHERE (Ano = new.Ano AND NomeCargo = 'Prefeito' AND Referencia = new.Referencia)
    ORDER BY (SELECT TotalDeVotos FROM Pleito WHERE (Candidatura.Pleito = Pleito.PleitoId))
    DESC LIMIT 1;
    
    IF NOT EXISTS (SELECT * FROM eleitos WHERE Candidato = new.Candidato) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo não foi eleito ao cargo de Prefeito no ano indicado.';
    ELSE
        new.Vigencia := (TO_DATE(new.Ano::TEXT || '-12-31', 'YYYY-MM-DD') + interval '1 year');
        RETURN NEW;
    END IF;
END;
$check_pref$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaPrefeito
    BEFORE INSERT OR UPDATE ON Cargo
    FOR EACH ROW WHEN (new.NomeCargo = 'Prefeito') EXECUTE PROCEDURE check_pref();

-- verifica se indivíduo já faz parte de alguma equipe de apoio no ano determinado
CREATE OR REPLACE FUNCTION check_equipe() RETURNS trigger AS $check_equipe$
BEGIN
    IF EXISTS (
        SELECT (Apoiador, Ano) FROM EquipeDeApoio WHERE (Apoiador = new.Apoiador AND Ano = new.Ano)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo já faz parte de uma equipe de apoio.';
    ELSE
        RETURN NEW;
    END IF;
END;
$check_equipe$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaEquipe
    BEFORE INSERT OR UPDATE ON EquipeDeApoio
    FOR EACH ROW EXECUTE PROCEDURE check_equipe();

-- atualiza vigência do cargo com base no ano de eleição
CREATE OR REPLACE FUNCTION set_vigencia() RETURNS trigger AS $set_vigencia$
DECLARE date_string TEXT;
BEGIN
    SELECT CONCAT(Ano, '-12-31') INTO date_string FROM Cargo WHERE (Candidato = new.Candidato AND Ano = new.Ano);
    new.Vigencia := (TO_DATE(date_string, 'YYYY-MM-DD') + interval '1 year');
    RETURN NEW;
END;
$set_vigencia$ LANGUAGE plpgsql;

CREATE TRIGGER SetVigencia
    BEFORE INSERT OR UPDATE ON Cargo
    FOR EACH ROW EXECUTE PROCEDURE set_vigencia();

-- verifica se indivíduo já fez uma doação na campanha atual do candidato
CREATE OR REPLACE FUNCTION check_doacao() RETURNS trigger AS $check_doacao$
DECLARE
    pessoa_tipo varchar(5);
BEGIN
    SELECT Tipo INTO pessoa_tipo FROM Individuo WHERE (Nome = new.Apoiador);
    IF pessoa_tipo = 'PJ' AND EXISTS (
        SELECT (Apoiador, Candidato, Ano) FROM Doacao WHERE (Apoiador = new.Apoiador AND Candidato = new.Candidato AND Ano = new.Ano)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O indivíduo já fez uma doação para este candidato nesta campanha.';
    ELSE
        RETURN NEW;
    END IF;
END;
$check_doacao$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaDoacao
    BEFORE INSERT OR UPDATE ON Doacao
    FOR EACH ROW EXECUTE PROCEDURE check_doacao();
