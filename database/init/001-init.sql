CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS app_bootstrap_marker (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO app_bootstrap_marker (name)
VALUES ('bid-agent-bootstrap')
ON CONFLICT (name) DO NOTHING;
