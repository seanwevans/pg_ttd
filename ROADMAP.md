# pg_ttd Roadmap

This document outlines the staged development plan for **pg_ttd**:  
a PostgreSQL-first simulation of a Transport Tycoon–style world.  
The roadmap balances incremental playability with long-term architectural goals.

---

## Stage 0 — Foundations (MVP Skeleton)

- [x] **Schema bootstrapping**
  - Tables for `tiles`, `terrain`, `industries`, `vehicles`, `companies`.
  - Metadata table for `game_state` (tick counter, seed, parameters).
- [x] **Stored procedures**
  - `new_game(width, height)`
  - `tick()`
- [x] **Graphics placeholders**
  - Script to generate dummy tile sprites stored in DB (e.g., base64 PNGs).
- [x] **Basic renderer**
  - Ncurses or HTTPX script to visualize map state from queries.

---

## Stage 1 — Core Simulation Loop

- [x] Implement economy tick:
  - Resource growth/decay rules.
  - Industry input → output cycles.
- [x] Vehicles:
  - Encode as rows with position, schedule, cargo.
  - Simple movement per tick.
- [x] Pathfinding stubs (stored procedure placeholders).
- [x] Company balance sheets (profit/loss tracked in DB).

---

## Stage 2 — Player Actions

- [ ] `build_station(x, y, type)`
- [ ] `build_track(x1, y1, x2, y2)`
- [ ] `build_industry(x, y, kind)`
- [ ] Transaction safety: atomic rollbacks for invalid builds.
- [ ] Enforce company ownership and permissions.

---

## Stage 3 — Visualization & Frontend

- [ ] **Renderer upgrade**
  - Web-based viewer via PostgREST + simple React canvas.
  - Tile → sprite rendering.
- [ ] **Ncurses client**
  - Text-based interface for headless play.
- [ ] **Query-based frontend**
  - UI is dumb: all state lives in DB, clients only SELECT/POST.

---

## Stage 4 — Multi-Node / Networking

- [ ] Define strongly connected components (SCCs) for local economies.
- [ ] Model **latency as light-speed delay** between SCCs (e.g., Earth ↔ Mars).
- [ ] Replication layer for eventual consistency across nodes.
- [ ] Test interplanetary sync with one-node delay model.

---

## Stage 5 — Advanced Mechanics

- [ ] Terrain generation with noise functions inside SQL.
- [ ] Pathfinding: Dijkstra/A* in stored procedures.
- [ ] AI competitors (as autonomous stored procedures).
- [ ] Multiplayer arbitration via PostgREST sessions.

---

## Stage 6 — Ecosystem Integration

- [ ] Docker setup with Postgres + PostgREST pre-configured.
- [ ] Optional web service that converts DB state into rendered frames.
- [ ] GitHub Actions for schema migrations & testing.
- [ ] Example datasets (e.g., Earth map, Mars map).

---

## Long-Term Vision

- **pg_ttd as a proof-of-concept** for using databases as simulation engines.  
- Scale beyond Transport Tycoon into generalized **Postgres-backed simulations**.  
- Use pg_ttd to explore distributed play across planetary distances.

---

## Current Status

- Schema: ✅ base tables and metadata established.
- Simulation loop: ✅ tick, economy, and movement procedures in place.
- Renderer: ✅ CLI viewer with placeholder sprites.
- Player actions: ⏳ design phase.

