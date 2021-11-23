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
    IF (
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
    IF EXISTS (
        SELECT (Reu, Procedente, DataTermino) FROM ProcessoJudicial WHERE (Reu = new.ViceCandidato AND Procedente = TRUE AND (date_part('year', DataTermino) - new.Ano) < 5)
    ) THEN
        RAISE EXCEPTION 'Atualização inválida. O vice-candidato não é ficha limpa.';  
    END IF;
    RETURN NEW;
END;
$check_ficha$ LANGUAGE plpgsql;

CREATE TRIGGER VerificaFicha
    BEFORE INSERT OR UPDATE ON Candidatura
    FOR EACH ROW EXECUTE PROCEDURE check_ficha();

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
    BEFORE UPDATE ON ProcessoJudicial
    FOR EACH ROW EXECUTE PROCEDURE check_proc();

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
