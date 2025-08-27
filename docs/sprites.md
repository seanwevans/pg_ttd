# Sprite Generation

This project stores small sprite images directly in the database.  The
`tools/generate_sprites.py` script creates a handful of colored square
PNGs and writes SQL statements that can be used to seed the database.

## Generating sprites

```
python tools/generate_sprites.py
```

Running the script produces `sql/seed_sprites.sql` containing `INSERT`
statements with Base64–encoded image data.

## Creating the table and seeding data

Create the table and populate it with the generated sprites:

```
psql -f sql/sprites.sql
psql -f sql/seed_sprites.sql
```

After these commands the `sprites` table will contain a row for each
sprite with its Base64-encoded PNG data.
