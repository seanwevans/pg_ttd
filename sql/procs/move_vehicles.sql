-- Procedure to move vehicles one step towards their scheduled waypoints
CREATE OR REPLACE PROCEDURE move_vehicles()
LANGUAGE plpgsql
AS $$
DECLARE
    v RECORD;
    target JSONB;
    target_x INTEGER;
    target_y INTEGER;
    new_x INTEGER;
    new_y INTEGER;
    new_idx INTEGER;
    sched_len INTEGER;
BEGIN
    FOR v IN SELECT * FROM vehicles LOOP
        sched_len := jsonb_array_length(v.schedule);
        IF sched_len = 0 THEN
            CONTINUE;
        END IF;

        IF v.schedule_idx >= sched_len OR v.schedule_idx < 0 THEN
            new_idx := 0;
        ELSE
            new_idx := v.schedule_idx;
        END IF;

        target := v.schedule -> new_idx;
        target_x := (target->>'x')::INTEGER;
        target_y := (target->>'y')::INTEGER;

        new_x := v.x;
        new_y := v.y;

        IF v.x < target_x THEN
            new_x := v.x + 1;
        ELSIF v.x > target_x THEN
            new_x := v.x - 1;
        ELSIF v.y < target_y THEN
            new_y := v.y + 1;
        ELSIF v.y > target_y THEN
            new_y := v.y - 1;
        ELSE
            new_idx := (new_idx + 1) % sched_len;
        END IF;

        UPDATE vehicles
        SET x = new_x,
            y = new_y,
            schedule_idx = new_idx
        WHERE id = v.id;
    END LOOP;
END;
$$;
