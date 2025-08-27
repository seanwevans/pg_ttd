-- Procedure to move vehicles one step towards their scheduled waypoints
CREATE OR REPLACE PROCEDURE move_vehicles()
LANGUAGE plpgsql
AS $$
BEGIN
    WITH v AS (
        SELECT
            id,
            x,
            y,
            schedule,
            jsonb_array_length(schedule) AS sched_len,
            CASE
                WHEN jsonb_array_length(schedule) = 0 THEN NULL
                WHEN schedule_idx IS NULL
                     OR schedule_idx >= jsonb_array_length(schedule)
                     OR schedule_idx < 0 THEN 0
                ELSE schedule_idx
            END AS idx
        FROM vehicles
    ),
    targets AS (
        SELECT
            id,
            x,
            y,
            sched_len,
            idx,
            (schedule -> idx) AS target,
            ((schedule -> idx) ->> 'x')::int AS target_x,
            ((schedule -> idx) ->> 'y')::int AS target_y
        FROM v
        WHERE sched_len > 0
    ),
    moved AS (
        SELECT
            id,
            CASE
                WHEN x < target_x THEN x + 1
                WHEN x > target_x THEN x - 1
                ELSE x
            END AS new_x,
            CASE
                WHEN x = target_x AND y < target_y THEN y + 1
                WHEN x = target_x AND y > target_y THEN y - 1
                ELSE y
            END AS new_y,
            CASE
                WHEN x = target_x AND y = target_y THEN (idx + 1) % sched_len
                ELSE idx
            END AS new_idx
        FROM targets
    )
    UPDATE vehicles v
    SET
        x = m.new_x,
        y = m.new_y,
        schedule_idx = m.new_idx
    FROM moved m
    WHERE v.id = m.id;
END;
$$;
