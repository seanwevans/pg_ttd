# Pathfinding

`find_route` in `sql/procs/pathfinding.sql` provides a basic A* search across a
grid using Manhattan distance. The function returns an array of coordinates from
the start location to the destination. While it currently ignores obstacles and
terrain costs, it establishes a foundation that can be extended with richer
world data.
