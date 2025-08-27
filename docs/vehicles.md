# Vehicles

Vehicles move across the map following a sequence of waypoints stored in
their `schedule` JSON column. Each waypoint is an object of the form
`{"x": <int>, "y": <int>}`.

`move_vehicles()` advances every vehicle one tile per tick using a set-based
`UPDATE` statement:

1. The next waypoint is read from `schedule[schedule_idx]`.
2. The vehicle's `x` or `y` coordinate is incremented toward the target by
   one step.
3. When the target tile is reached, `schedule_idx` advances to the next
   waypoint, wrapping to the start when the route is finished.

The procedure ignores vehicles with an empty schedule.

For route-based movement a vehicle tracks progress with `next_waypoint_idx`,
which stores the next step within the current path returned by `find_route`.

Benchmarking with 100k vehicles on PostgreSQL 16 reduced execution time from
roughly 2.0s with a row-by-row loop to about 1.5s using the set-based query.
