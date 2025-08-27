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

### `resources`
Tracked quantities for raw materials or goods.
- `id` — primary key.
- `name` — unique resource name.
- `amount` — current stock level.

### `resource_rules`
Growth and decay rates applied each economy tick.
- `resource_id` — references the resource.
- `growth_rate` — amount gained per tick.
- `decay_rate` — amount lost per tick.

### `resource_industries`
Lightweight factories that convert one resource into another. These are
distinct from map `industries` and exist purely in the economic model.
- `id` — primary key.
- `name` — unique industry name.
- `input_resource_id` — resource consumed each tick.
- `output_resource_id` — resource produced.
- `input_per_tick` — units of input consumed per tick.
- `output_per_tick` — units of output produced per tick.

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
- `resource_rules.resource_id` → `resources.id`
- `resource_industries.input_resource_id` → `resources.id`
- `resource_industries.output_resource_id` → `resources.id`

These relationships enable querying ownership, positions, and terrain context for simulation routines.
