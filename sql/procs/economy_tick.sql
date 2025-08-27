-- Resource and industry tick processing

-- Table storing current resource amounts
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0
);

-- Rules describing growth and decay for each resource
CREATE TABLE IF NOT EXISTS resource_rules (
    resource_id INTEGER PRIMARY KEY REFERENCES resources(id) ON DELETE CASCADE,
    growth_rate INTEGER NOT NULL DEFAULT 0,
    decay_rate INTEGER NOT NULL DEFAULT 0
);

-- Industries consume one resource to produce another
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    input_resource_id INTEGER REFERENCES resources(id),
    output_resource_id INTEGER REFERENCES resources(id),
    input_per_tick INTEGER NOT NULL DEFAULT 0,
    output_per_tick INTEGER NOT NULL DEFAULT 0
);

-- Perform a single economy tick. Resources regenerate/decay and
-- industries consume inputs and produce outputs.
CREATE OR REPLACE FUNCTION economy_tick() RETURNS VOID AS $$
BEGIN
    -- Apply resource growth and decay
    UPDATE resources r
    SET amount = GREATEST(0, r.amount + rr.growth_rate - rr.decay_rate)
    FROM resource_rules rr
    WHERE rr.resource_id = r.id;

    -- Handle industries that have enough input resources
    WITH ready AS (
        SELECT i.id, i.input_resource_id, i.output_resource_id,
               i.input_per_tick, i.output_per_tick
        FROM industries i
        JOIN resources rin ON rin.id = i.input_resource_id
        WHERE rin.amount >= i.input_per_tick
    ), consumed AS (
        UPDATE resources r
        SET amount = r.amount - ready.input_per_tick
        FROM ready
        WHERE r.id = ready.input_resource_id
        RETURNING ready.output_resource_id, ready.output_per_tick
    )
    UPDATE resources r
    SET amount = r.amount + c.output_per_tick
    FROM consumed c
    WHERE r.id = c.output_resource_id;
END;
$$ LANGUAGE plpgsql;
