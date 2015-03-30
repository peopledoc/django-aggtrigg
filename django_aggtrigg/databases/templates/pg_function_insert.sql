CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN
{% if where_clause %}
IF {{where_clause}} THEN
{% endif %}
IF (SELECT {{column}} FROM {{aggtable}} WHERE {{column}}=NEW.{{column}} LIMIT 1) IS NOT NULL THEN
    UPDATE {{aggtable}} SET {{actions}} WHERE {{column}}=NEW.{{column}};
ELSE
    INSERT INTO {{aggtable}} VALUES ( NEW.{{column}}, 1 );    
END IF;
{% if where_clause %}
END IF;
{% endif %}
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
