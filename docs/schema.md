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
- `id` — primary key.
- `name` — company name.

### `industries`
Industry structures placed on tiles.
- `id` — primary key.
- `name` — industry name.
- `tile_id` — foreign key to the tile it occupies.
- `company_id` — optional owning company.

### `vehicles`
Movable units controlled by companies.
- `id` — primary key.
- `name` — vehicle name.
- `type` — vehicle type (e.g., train, truck).
- `tile_id` — current tile position.
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
- `industries.company_id` → `companies.id`
- `vehicles.tile_id` → `tiles.id`
- `vehicles.company_id` → `companies.id`

These relationships enable querying ownership, positions, and terrain context for simulation routines.
