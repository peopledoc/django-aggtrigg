CREATE TABLE {{name}} ({{column.name}} {{column.type}}{% for agg in aggregats %}, agg_{{agg.name}} {{agg.type}}{% endfor %});
CREATE INDEX ON {{name}} ({{column.name}});
