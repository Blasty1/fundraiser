CREATE VIEW wallets AS 
	SELECT f2.id_user, f2.title ,f2.id_fund,SUM(amount) AS totalReached , end_timestamp AS 'created_at'
	FROM funds  f2,donations
	WHERE donations.id_fund = f2.id_fund AND datetime(end_timestamp) < datetime("now","localtime") 
	GROUP BY f2.id_fund 
	HAVING totalReached >= (
			SELECT target
			FROM funds f1
			WHERE f1.id_fund = f2.id_fund
    )