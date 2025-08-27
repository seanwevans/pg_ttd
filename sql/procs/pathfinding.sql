-- Pathfinding utilities
-- Implements a simple A* search over a grid using Manhattan distance.

CREATE OR REPLACE FUNCTION find_route(
    start_x integer,
    start_y integer,
    end_x integer,
    end_y integer,
    cost_map integer[][] DEFAULT NULL  -- optional costs: [x, y, cost]
)
RETURNS integer[][] AS $$
DECLARE
    cur_x integer;
    cur_y integer;
    cur_cost integer;
    nbr RECORD;
    node integer[];
    path integer[][] := ARRAY[]::integer[][];
    open_set integer[][] := ARRAY[]::integer[][];  -- [x,y,cost,priority]
    came_from integer[][] := ARRAY[]::integer[][]; -- [x,y,prev_x,prev_y,cost]
    idx integer;
    pri integer;
    step_cost integer;
    terrain_type text;
BEGIN
    -- Seed initial node
    open_set := ARRAY[[start_x, start_y, 0,
                       abs(start_x - end_x) + abs(start_y - end_y)]];
    came_from := ARRAY[[start_x, start_y, NULL::integer, NULL::integer, 0]];

    LOOP
        -- No nodes left to explore
        IF array_length(open_set, 1) IS NULL THEN
            RETURN ARRAY[]::integer[][];
        END IF;

        -- Find node with lowest priority
        idx := 1;
        pri := open_set[1][4];
        FOR i IN 2..array_length(open_set, 1) LOOP
            IF open_set[i][4] < pri THEN
                pri := open_set[i][4];
                idx := i;
            END IF;
        END LOOP;

        node := open_set[idx];
        cur_x := node[1];
        cur_y := node[2];
        cur_cost := node[3];

        -- Remove current node from open set
        open_set := ARRAY(
            SELECT elem FROM unnest(open_set) WITH ORDINALITY AS u(elem, ord)
            WHERE ord <> idx
        );

        -- Goal reached
        EXIT WHEN cur_x = end_x AND cur_y = end_y;

        -- Explore neighbouring tiles
        FOR nbr IN
            SELECT cur_x + 1 AS x, cur_y AS y
            UNION ALL SELECT cur_x - 1, cur_y
            UNION ALL SELECT cur_x, cur_y + 1
            UNION ALL SELECT cur_x, cur_y - 1
        LOOP
            -- Skip impassable terrain (e.g. water or mountain)
            SELECT type INTO terrain_type
            FROM terrain
            WHERE tile_x = nbr.x AND tile_y = nbr.y;
            IF terrain_type IS NULL OR terrain_type IN ('water', 'mountain') THEN
                CONTINUE;
            END IF;

            -- Determine traversal cost for this tile
            step_cost := 1;
            IF cost_map IS NOT NULL THEN
                SELECT c[3] INTO step_cost
                FROM unnest(cost_map) AS c
                WHERE c[1] = nbr.x AND c[2] = nbr.y;
                step_cost := COALESCE(step_cost, 1);
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM unnest(came_from) AS cf
                WHERE cf[1] = nbr.x AND cf[2] = nbr.y
            ) THEN
                came_from := came_from ||
                    ARRAY[[nbr.x, nbr.y, cur_x, cur_y, cur_cost + step_cost]];
                open_set := open_set ||
                    ARRAY[[nbr.x, nbr.y, cur_cost + step_cost,
                           cur_cost + step_cost +
                           abs(nbr.x - end_x) + abs(nbr.y - end_y)]];
            END IF;
        END LOOP;
    END LOOP;

    -- Reconstruct path
    cur_x := end_x;
    cur_y := end_y;
    LOOP
        path := ARRAY[[cur_x, cur_y]] || path;
        EXIT WHEN cur_x = start_x AND cur_y = start_y;
        SELECT cf[3], cf[4] INTO cur_x, cur_y
        FROM unnest(came_from) AS cf
        WHERE cf[1] = cur_x AND cf[2] = cur_y;
        IF cur_x IS NULL THEN
            RETURN ARRAY[]::integer[][];
        END IF;
    END LOOP;

    RETURN path;
END;
$$ LANGUAGE plpgsql;

