# Data

## Engine

- **SQLite first.** A file: no server, trivial backups, easy tests.
- **Postgres** when there are many concurrent writers, more than one server
  instance, or a need for Postgres features (PostGIS for spatial queries,
  full-text search, heavy JSON querying).
- **Turso / libsql** when a SQLite app is deployed serverless: the same SQL
  locally (a file) and in production.
- **No MySQL.**

## Access layer

| Where | Use |
|---|---|
| TypeScript servers and CLIs | **Prisma** (schema + `prisma migrate`; driver adapters: `@prisma/adapter-libsql` for SQLite/Turso, `@prisma/adapter-pg` for Postgres) |
| Expo apps (on device) | **Drizzle** + expo-sqlite (drizzle-kit migrations) |
| Python tools and bots | raw **sqlite3**, schema as a numbered migration list |
| Python services on Postgres | **SQLAlchemy 2** (async) + **Alembic** |

Prisma notes:
- The `prisma-client` generator with `importFileExtension = "ts"` and
  `moduleFormat = "esm"` generates a client Node can run directly; generate it
  into `src/generated/prisma` (git-ignored) from a `postinstall` script.
- The database URL lives in `prisma.config.ts`, read from `DATABASE_URL`.
- pnpm must be allowed to run `prisma` and `@prisma/engines` install scripts
  (`allowBuilds` in `pnpm-workspace.yaml`).

## Migrations (firm)

Every schema change is a new, numbered, committed migration. Never edit an
applied migration; never change the schema by hand.

- Prisma: `pnpm run db:migrate` (`prisma migrate dev`) in development,
  `prisma migrate deploy` in production.
- Alembic: `alembic revision --autogenerate -m "…"`, review it, `alembic
  upgrade head`; `alembic check` in CI catches models without a migration.
- Raw sqlite3: a list of SQL strings; `PRAGMA user_version` records how many
  have run:

```python
MIGRATIONS = ["CREATE TABLE runs (...);", "ALTER TABLE runs ADD COLUMN note TEXT;"]

def migrate(conn):
    (version,) = conn.execute("PRAGMA user_version").fetchone()
    for number, sql in enumerate(MIGRATIONS[version:], start=version + 1):
        conn.executescript(sql)
        conn.execute(f"PRAGMA user_version = {number}")
        conn.commit()
```

Tests run against a database built from the migrations, never a hand-written
copy of the schema.

## Files

- Database files live in `data/` (git-ignored, with a `.gitkeep`); the path
  comes from an environment variable or flag, never hard-coded elsewhere.
- Uploads and blobs go behind a small storage interface: local filesystem in
  development, S3-compatible storage (Cloudflare R2) in production. Never in
  the database, never in git.

## Backups

- A SQLite database on a long-running server that holds data worth keeping:
  **Litestream** replicating to S3/R2.
- Hosted databases: rely on the provider's backups, and know how to restore.
