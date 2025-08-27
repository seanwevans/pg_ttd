# pg_ttd

**pg_ttd** is a prototype of an attempt at *OpenTTD inside PostgreSQL*.
We attempt to reproduce at least part of OpenTTD within a Postgres database.
That is, all simulation, logic—world generation, tile updates, entities, economics, etc
is implemented as stored procedures and tables in PostgreSQL.

## Renderer

A tiny curses-based renderer is included to visualise the map stored in
PostgreSQL and advance the simulation.

### Launch

1. Ensure the database is populated with the required schema.
2. Provide connection parameters using the standard `PGHOST`, `PGPORT`,
   `PGDATABASE`, `PGUSER` and `PGPASSWORD` environment variables **or** create a
   JSON configuration file and reference it with `PGTTD_CONFIG`.
3. Run the viewer:

   ```bash
   python renderer/cli_viewer.py
   ```

Press `q` to quit. Each refresh calls `tick()` in the database to advance the
world state.

