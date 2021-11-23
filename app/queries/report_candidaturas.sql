SELECT
	nome,
	nomecargo,
	ano
FROM
	cargo
	RIGHT JOIN
	individuo ON (cargo.candidato = individuo.nome)
WHERE
	cargo.candidato IS NOT NULL
ORDER BY ano DESC, cargo
