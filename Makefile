PSQL?=psql
SCHEMA=sql/schema.sql

.PHONY: generate-schema
generate-schema:
	python scripts/generate_schema.py

.PHONY: apply-schema
apply-schema:
	$(PSQL) $(PSQLFLAGS) -f $(SCHEMA)
