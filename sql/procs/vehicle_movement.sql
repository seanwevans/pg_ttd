-- Vehicle movement procedures
-- Move a single vehicle along a path computed by find_route.

CREATE OR REPLACE FUNCTION move_vehicle(
    vehicle_id integer,
    start_x integer,
    start_y integer,
    end_x integer,
    end_y integer
)
RETURNS void AS $$
DECLARE
    path integer[][];
    next_idx integer;
BEGIN
    path := find_route(start_x, start_y, end_x, end_y);
    IF array_length(path, 1) IS NULL THEN
        RETURN;
    END IF;

    SELECT next_waypoint_idx INTO next_idx
    FROM vehicles WHERE id = vehicle_id;

    IF next_idx IS NULL OR next_idx < 2 THEN
        next_idx := 2;
    END IF;

    IF next_idx > array_length(path, 1) THEN
        RETURN;
    END IF;

    UPDATE vehicles
    SET
        x = path[next_idx][1],
        y = path[next_idx][2],
        next_waypoint_idx = next_idx + 1
    WHERE id = vehicle_id;
END;
$$ LANGUAGE plpgsql;

