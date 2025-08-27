# Database Schema

The schema defines core tables for representing the game world and simulation state.

## Tables

### `terrain`
Stores terrain types.
- `id` — primary key.
- `name` — human readable name.

### `tiles`
Represents each map tile.
- `id` — primary key.
- `x`, `y` — tile coordinates.
- `terrain_id` — foreign key to `terrain`.
- Each `(x, y)` pair is unique.

### `companies`
Companies owned by players or AI.
- `company_id` — primary key.
- `name` — company name.
- `cash` — total available money.
- `income` — earnings generated in the current tick.
- `expenses` — money spent in the current tick.

### `industries`
Industry structures placed on tiles.
- `id` — primary key.
- `name` — industry name.
- `tile_id` — foreign key to the tile it occupies.
- `company_id` — optional owning company.

### `vehicles`
Movable units controlled by companies.
- `id` — primary key.
- `x`, `y` — current map coordinates.
- `schedule` — array of waypoint objects.
- `schedule_idx` — index of the next waypoint.
- `cargo` — array of carried items.
- `company_id` — owning company.

### `game_state`
Singleton metadata about the running simulation.
- `id` — primary key for potential multiple saves.
- `current_tick` — global tick counter.
- `seed` — world generation seed.
- `created_at` — timestamp when the state was created.

## Relationships
- `tiles.terrain_id` → `terrain.id`
- `industries.tile_id` → `tiles.id`
- `industries.company_id` → `companies.company_id`
- `vehicles.company_id` → `companies.company_id`

These relationships enable querying ownership, positions, and terrain context for simulation routines.
