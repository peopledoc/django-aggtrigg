CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN
{% if where_clause %}
IF {{where_clause}} THEN
{% endif %}
UPDATE {{table}} SET {{actions}} WHERE {{column}}=OLD.{{column}};
{% if where_clause %}
END IF;
{% endif %}
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
