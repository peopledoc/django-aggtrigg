CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN
IF (SELECT {{column}}  FROM {{table}} WHERE {{column}}=NEW.{{column}}) > 0 THEN
    UPDATE {{table}} SET {{actions}} WHERE {{column}}=NEW.{{column}};
ELSE
    INSERT INTO {{table}} VALUES (NEW.{{column}}, 1);
END IF;
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
