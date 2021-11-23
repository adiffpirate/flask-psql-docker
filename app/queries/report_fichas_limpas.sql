SELECT
	individuo.nome,
	processoJudicial.procedente as procedente,
	processoJudicial.dataTermino as dataTermino
FROM
	individuo
	LEFT JOIN
	processoJudicial ON (individuo.nome = processoJudicial.reu)
WHERE
	procedente IS NULL OR procedente = FALSE
	OR (
		procedente = TRUE
		AND ((CURRENT_DATE::DATE - dataTermino::DATE) > 1825)
	)
ORDER BY procedente DESC, dataTermino DESC, individuo.nome
