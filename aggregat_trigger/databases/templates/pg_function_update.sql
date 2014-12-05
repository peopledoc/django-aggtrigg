CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN
IF NEW.{{column}} != OLD.{{column}} THEN
    UPDATE {{table}} SET {{actions_old}} WHERE {{column}}=OLD.{{column}};
    IF (SELECT {{column}} FROM {{table}} WHERE {{column}}=NEW.{{column}} LIMIT 1) IS NOT NULL THEN
        UPDATE {{table}} SET {{actions_new}} WHERE {{column}}=NEW.{{column}};
    ELSE
        INSERT INTO {{table}} VALUES ( NEW.{{column}}, 1 );    
    END IF;
END IF;
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
