-- Pathfinding utilities
-- Implements a simple A* search over a grid using Manhattan distance.

CREATE OR REPLACE FUNCTION find_route(start_x integer, start_y integer,
                                      end_x integer, end_y integer)
RETURNS integer[][] AS $$
DECLARE
    cur_x integer;
    cur_y integer;
    cur_cost integer;
    nbr RECORD;
    path integer[][] := ARRAY[]::integer[][];
BEGIN
    -- Ensure we can run multiple times in a session
    DROP TABLE IF EXISTS open_set;
    DROP TABLE IF EXISTS came_from;

    -- Nodes to be explored, ordered by estimated total cost
    CREATE TEMP TABLE open_set(
        x      integer,
        y      integer,
        cost   integer,
        pri    integer
    ) ON COMMIT DROP;

    -- Tracks how we reached each explored node
    CREATE TEMP TABLE came_from(
        x       integer,
        y       integer,
        prev_x  integer,
        prev_y  integer,
        cost    integer,
        PRIMARY KEY (x, y)
    ) ON COMMIT DROP;

    INSERT INTO open_set VALUES
        (start_x, start_y, 0, abs(start_x - end_x) + abs(start_y - end_y));
    INSERT INTO came_from VALUES (start_x, start_y, NULL, NULL, 0);

    LOOP
        SELECT x, y, cost INTO cur_x, cur_y, cur_cost
        FROM open_set
        ORDER BY pri
        LIMIT 1;

        -- No path found
        IF NOT FOUND THEN
            RETURN ARRAY[]::integer[][];
        END IF;

        DELETE FROM open_set WHERE x = cur_x AND y = cur_y;

        EXIT WHEN cur_x = end_x AND cur_y = end_y;

        -- Explore four neighbouring tiles
        FOR nbr IN
            SELECT cur_x + 1 AS x, cur_y AS y
            UNION ALL SELECT cur_x - 1, cur_y
            UNION ALL SELECT cur_x, cur_y + 1
            UNION ALL SELECT cur_x, cur_y - 1
        LOOP
            IF NOT EXISTS (SELECT 1 FROM came_from
                           WHERE x = nbr.x AND y = nbr.y) THEN
                INSERT INTO came_from(x, y, prev_x, prev_y, cost)
                VALUES (nbr.x, nbr.y, cur_x, cur_y, cur_cost + 1);
                INSERT INTO open_set(x, y, cost, pri)
                VALUES (
                    nbr.x, nbr.y, cur_cost + 1,
                    cur_cost + 1
                    + abs(nbr.x - end_x) + abs(nbr.y - end_y)
                );
            END IF;
        END LOOP;
    END LOOP;

    -- Reconstruct path from end to start
    cur_x := end_x;
    cur_y := end_y;
    LOOP
        path := ARRAY[[cur_x, cur_y]] || path;
        EXIT WHEN cur_x = start_x AND cur_y = start_y;
        SELECT prev_x, prev_y INTO cur_x, cur_y
        FROM came_from WHERE x = cur_x AND y = cur_y;
        -- Safety: no path recorded
        IF NOT FOUND THEN
            RETURN ARRAY[]::integer[][];
        END IF;
    END LOOP;

    RETURN path;
END;
$$ LANGUAGE plpgsql;

