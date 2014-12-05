CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN
IF NEW.{{column}} != OLD.{{column}} THEN
    UPDATE {{table}} SET {{actions_old}} WHERE {{column}}=NEW.{{column}};
    UPDATE {{table}} SET {{actions_new}} WHERE {{column}}=OLD.{{column}};
END IF;
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
