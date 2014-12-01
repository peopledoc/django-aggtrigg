CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN
IF (SELECT {{column}} FROM {{aggtable}} WHERE {{column}}=NEW.{{column}} LIMIT 1) IS NOT NULL THEN
    UPDATE {{aggtable}} SET {{actions}} WHERE {{column}}=NEW.{{column}};
ELSE
    INSERT INTO {{aggtable}} VALUES ( NEW.{{column}}, 1 );
    
END IF;
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
