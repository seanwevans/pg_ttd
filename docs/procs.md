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

## `economy_tick()`
Runs the simplified economic simulation. Resource amounts are adjusted by
`resource_rules` and any `resource_industries` consume input resources to
produce outputs.

Usage:
```sql
SELECT economy_tick();
```

For a self-contained example see
[`sql/tests/economy_tick.sql`](../sql/tests/economy_tick.sql). That test seeds the
`resources`, `resource_rules` and `resource_industries` tables then invokes
`economy_tick()`. After the call, the wood resource drops from `10` to `9` while
goods increase from `0` to `1`, demonstrating both growth rules and industry
production.

The procedure is defined in
[`sql/procs/economy_tick.sql`](../sql/procs/economy_tick.sql).

## `move_vehicles()`
Advances every vehicle one tile toward its current scheduled waypoint. When a
vehicle reaches its target, the `schedule_idx` wraps to the next waypoint in its
`schedule`.

Usage:
```sql
CALL move_vehicles();
```

Each call updates the `x`, `y` and `schedule_idx` columns of every row in the
`vehicles` table. The implementation lives in
[`sql/procs/move_vehicles.sql`](../sql/procs/move_vehicles.sql). The script
[`scripts/benchmark_move_vehicles.py`](../scripts/benchmark_move_vehicles.py)
populates test data and measures the performance of this procedure.
