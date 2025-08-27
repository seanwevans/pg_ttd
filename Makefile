PSQL?=psql
SCHEMA=sql/schema.sql

.PHONY: apply-schema
apply-schema:
	$(PSQL) $(PSQLFLAGS) -f $(SCHEMA)
