# Stored Procedures

## `new_game(width, height)`
Initializes a new game world. It wipes any existing state, creates a new
`game_state` row with tick zero, and fills the `tiles` and `terrain`
tables with a grid of the supplied dimensions.

Usage:
```sql
CALL new_game(10, 10);
```

## `tick()`
Advances the global tick counter and updates time-dependent tables such as
`terrain`.

Usage:
```sql
CALL tick();
```

### Python wrapper
The script [`scripts/run_tick.py`](../scripts/run_tick.py) calls `tick()` using
[`psycopg`](https://www.psycopg.org/). Set the `DATABASE_URL` environment
variable and run:

```bash
python scripts/run_tick.py
```
