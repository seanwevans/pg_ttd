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
    cur RECORD;
    nbr RECORD;
    path integer[][] := ARRAY[]::integer[][];
    step_cost integer;
    terrain_type text;
BEGIN
    DROP TABLE IF EXISTS tmp_open;
    CREATE TEMP TABLE tmp_open(
        x int,
        y int,
        cost int,
        priority int
    ) ON COMMIT DROP;
    DROP TABLE IF EXISTS tmp_came;
    CREATE TEMP TABLE tmp_came(
        x int,
        y int,
        prev_x int,
        prev_y int,
        cost int
    ) ON COMMIT DROP;

    INSERT INTO tmp_open VALUES (start_x, start_y, 0,
        abs(start_x - end_x) + abs(start_y - end_y));
    INSERT INTO tmp_came VALUES (start_x, start_y, NULL, NULL, 0);

    LOOP
        SELECT * INTO cur FROM tmp_open ORDER BY priority LIMIT 1;
        IF NOT FOUND THEN
            RETURN ARRAY[]::integer[][];
        END IF;
        DELETE FROM tmp_open WHERE x = cur.x AND y = cur.y AND cost = cur.cost AND priority = cur.priority;
        EXIT WHEN cur.x = end_x AND cur.y = end_y;

        FOR nbr IN
            SELECT cur.x + 1 AS x, cur.y AS y
            UNION ALL SELECT cur.x - 1, cur.y
            UNION ALL SELECT cur.x, cur.y + 1
            UNION ALL SELECT cur.x, cur.y - 1
        LOOP
            SELECT type INTO terrain_type
            FROM terrain
            WHERE tile_x = nbr.x AND tile_y = nbr.y;
            IF terrain_type IS NULL OR terrain_type IN ('water', 'mountain') THEN
                CONTINUE;
            END IF;

            step_cost := 1;
            IF cost_map IS NOT NULL THEN
                SELECT cost_map[s][3] INTO step_cost
                FROM generate_subscripts(cost_map, 1) AS s
                WHERE cost_map[s][1] = nbr.x AND cost_map[s][2] = nbr.y;
                step_cost := COALESCE(step_cost, 1);
            END IF;

            IF NOT EXISTS (SELECT 1 FROM tmp_came WHERE x = nbr.x AND y = nbr.y) THEN
                INSERT INTO tmp_came VALUES (nbr.x, nbr.y, cur.x, cur.y, cur.cost + step_cost);
                INSERT INTO tmp_open VALUES (
                    nbr.x,
                    nbr.y,
                    cur.cost + step_cost,
                    cur.cost + step_cost + abs(nbr.x - end_x) + abs(nbr.y - end_y)
                );
            END IF;
        END LOOP;
    END LOOP;

    cur.x := end_x;
    cur.y := end_y;
    LOOP
        path := ARRAY[ARRAY[cur.x, cur.y]] || path;
        EXIT WHEN cur.x = start_x AND cur.y = start_y;
        SELECT prev_x, prev_y INTO cur.x, cur.y FROM tmp_came WHERE x = cur.x AND y = cur.y;
        IF cur.x IS NULL THEN
            RETURN ARRAY[]::integer[][];
        END IF;
    END LOOP;

    RETURN path;
END;
$$ LANGUAGE plpgsql;
