-- Create extension for full-text search (database already exists via POSTGRES_DB env var)
CREATE EXTENSION IF NOT EXISTS pg_trgm;