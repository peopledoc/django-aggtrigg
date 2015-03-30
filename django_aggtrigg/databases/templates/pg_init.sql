BEGIN;
LOCK TABLE {{table}} IN EXCLUSIVE MODE;
TRUNCATE {{aggtable}};

WITH {% for agg in aggregats %}{{aggregats[agg]["column"]}}
      as (
     (SELECT {{column}}, count({{column}}) FROM {{table}} {% if aggregats[agg]["where"] %} WHERE {{aggregats[agg]["where"]}} {% endif%} GROUP BY {{column}})
     ){% if not loop.last %},{% endif %}
{% endfor %}

INSERT INTO {{aggtable}} ({{column}}, {% for agg in aggregats %}{{aggregats[agg]["column"]}} {% if not loop.last %},{% endif %} {% endfor %}) (SELECT {{table}}.{{column}},
       {% for agg in aggregats %}
          {{aggregats[agg]["column"]}}.count {% if not loop.last %},{% endif %}
       {% endfor %}  FROM {{table}}
       {% for agg in aggregats %}
           LEFT OUTER JOIN
           {{aggregats[agg]["column"]}} ON ({{table}}.{{column}} = {{aggregats[agg]["column"]}}.{{column}})
       {%endfor%}
       GROUP BY
             {{table}}.{{column}},
             {% for agg in aggregats %}
             {{aggregats[agg]["column"]}}.count{% if not loop.last %},{% endif %}
             {% endfor%});
COMMIT;
