# Pathfinding

The current implementation uses stub functions defined in `sql/procs/pathfinding.sql`.
These functions return empty paths and are placeholders for a future algorithm.

The intended implementation will use Dijkstra or A* to compute optimal routes
between coordinates. Once implemented, vehicle movement procedures will be able
to call `find_route` to obtain a valid path.
