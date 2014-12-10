BEGIN;  
LOCK TABLE {{table}} IN EXCLUSIVE MODE;
TRUNCATE {{aggtable}};
INSERT INTO {{aggtable}} (SELECT {{column}}, count({{column}}) FROM {{table}} GROUP BY {{column}});
COMMIT;
