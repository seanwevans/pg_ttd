-- Pathfinding stub functions
-- TODO: implement Dijkstra or A* algorithm

CREATE OR REPLACE FUNCTION find_route(start_x integer, start_y integer, end_x integer, end_y integer)
RETURNS integer[][] AS $$
BEGIN
    -- Placeholder: returns empty path until algorithm is implemented
    RETURN ARRAY[]::integer[][];
END;
$$ LANGUAGE plpgsql;

