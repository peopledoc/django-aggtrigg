CREATE OR REPLACE FUNCTION {{name}} RETURNS TRIGGER AS $BODY$
BEGIN

{% if where_clause %}
IF NEW.{{column}} != OLD.{{column}} THEN
    IF {{where_clause}} THEN
       IF (SELECT {{column}} FROM {{table}} WHERE {{column}}=NEW.{{column}} LIMIT 1) IS NOT NULL THEN
          UPDATE {{table}} SET {{actions_new}} WHERE {{column}}=NEW.{{column}};
       ELSE
       -- else insert a new line
          INSERT INTO {{table}} ({{column}}, {{action_key}}) VALUES ( NEW.{{column}}, 1 );
       END IF;
   END IF;
   IF {{old_where_clause}} THEN
          UPDATE {{table}} SET {{actions_old}} WHERE {{column}}=OLD.{{column}};
   END IF;

ELSE
-- in this case we act on the same line, the field is changed from
-- True to False, from False to True or in not changed at all

    IF (NOT {{where_clause}} AND {{old_where_clause}}) THEN
-- the field is changed from True to False we decrement
        UPDATE {{table}} SET {{actions_old}} WHERE {{column}}=NEW.{{column}};
    ELSE
        IF (NOT {{old_where_clause}} AND {{where_clause}}) THEN
-- the field is changed from False to True, we increment
            IF (SELECT {{column}} FROM {{table}} WHERE {{column}}=NEW.{{column}} LIMIT 1) IS NOT NULL THEN
                UPDATE {{table}} SET {{actions_new}} WHERE {{column}}=NEW.{{column}};
            ELSE
                INSERT INTO {{table}} VALUES ( NEW.{{column}}, 1 );
            END IF;
        END IF;
    END IF;
END IF;
{% else %}

IF NEW.{{column}} != OLD.{{column}} THEN
    UPDATE {{table}} SET {{actions_old}} WHERE {{column}}=OLD.{{column}};
    IF (SELECT {{column}} FROM {{table}} WHERE {{column}}=NEW.{{column}} LIMIT 1) IS NOT NULL THEN
        UPDATE {{table}} SET {{actions_new}} WHERE {{column}}=NEW.{{column}};
    ELSE
        INSERT INTO {{table}} VALUES ( NEW.{{column}}, 1 );
    END IF;
END IF;

{% endif %}
RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;
