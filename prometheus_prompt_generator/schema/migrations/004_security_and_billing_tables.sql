-- Migration: 004_security_and_billing_tables
-- Created: March 9th, 2025
-- Description: Add security, billing, and tracking tables for API keys, usage metrics, and custom prompts

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Add is_custom flag to Prompts table
ALTER TABLE Prompts ADD COLUMN is_custom INTEGER DEFAULT 0 NOT NULL;
CREATE INDEX idx_prompts_custom ON Prompts(is_custom);

-- API Key storage with encryption support
CREATE TABLE ApiKeys (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider TEXT NOT NULL,       -- OpenAI, Anthropic, etc.
  key_name TEXT NOT NULL,       -- Display name for the key
  key_value TEXT NOT NULL,      -- Encrypted key value
  is_active INTEGER DEFAULT 1,  -- Whether key is currently active
  created_date TEXT NOT NULL,   -- When added
  updated_date TEXT,            -- When last modified
  last_used_date TEXT,          -- When last used
  user_id TEXT,                 -- Who added it
  usage_limit REAL,             -- Optional usage limit
  usage_current REAL DEFAULT 0, -- Current usage amount
  env_context TEXT,             -- Development, Production, etc.
  UNIQUE(provider, key_name)
);

-- Secure index for API keys
CREATE INDEX idx_api_keys ON ApiKeys(provider, is_active);

-- Code Map Generator usage tracking
CREATE TABLE CodeMapUsage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,      -- When used
  user_id TEXT,                 -- Who used it
  session_id TEXT,              -- Session identifier
  repo_path TEXT,               -- Repository path
  file_count INTEGER,           -- Number of files processed
  node_count INTEGER,           -- Number of nodes generated
  edge_count INTEGER,           -- Number of edges generated
  generation_time_ms INTEGER,   -- Time to generate the map
  map_complexity_score REAL,    -- Complexity score of the generated map
  successful INTEGER DEFAULT 1, -- Whether generation was successful
  error_message TEXT,           -- If failed, error details
  prompt_id INTEGER,            -- Related prompt if used
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id)
);

CREATE INDEX idx_code_map_usage ON CodeMapUsage(timestamp, user_id);

-- LLM Usage tracking for billing and analytics
CREATE TABLE LlmUsage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,      -- When used
  provider TEXT NOT NULL,       -- OpenAI, Anthropic, etc.
  model TEXT NOT NULL,          -- GPT-4, Claude, etc.
  api_key_id INTEGER,           -- Reference to used API key
  prompt_tokens INTEGER,        -- Input token count
  completion_tokens INTEGER,    -- Output token count
  total_tokens INTEGER,         -- Total token count
  estimated_cost REAL,          -- Estimated cost in USD
  billing_category TEXT,        -- Category for billing purposes
  user_id TEXT,                 -- Who used it
  project_id TEXT,              -- Project identifier
  feature_used TEXT,            -- Feature that triggered LLM usage
  prompt_id INTEGER,            -- Related prompt if used
  request_id TEXT,              -- Unique request identifier
  latency_ms INTEGER,           -- Round-trip latency
  FOREIGN KEY (api_key_id) REFERENCES ApiKeys(id),
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id)
);

CREATE INDEX idx_llm_usage ON LlmUsage(provider, model, timestamp);
CREATE INDEX idx_llm_usage_billing ON LlmUsage(billing_category, timestamp);

-- Schema Extension Log - tracks schema changes for future extensibility
CREATE TABLE SchemaExtension (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,     -- Table being extended
  column_name TEXT NOT NULL,    -- Column being added
  column_type TEXT NOT NULL,    -- Data type of column
  migration_id INTEGER,         -- Migration that added it
  added_date TEXT NOT NULL,     -- When was it added
  reason TEXT,                  -- Why was it added
  is_required INTEGER DEFAULT 0 -- Is it a required field
);

CREATE INDEX idx_schema_extension ON SchemaExtension(table_name);

-- Add tracking triggers

-- Track code map generation in reporting metrics
CREATE TRIGGER track_code_map_usage
AFTER INSERT ON CodeMapUsage
BEGIN
    -- Daily usage count
    INSERT INTO ReportingMetrics (
        metric_type, metric_name, timestamp, value, dimension, dimension_value
    )
    VALUES (
        'feature', 'code_map_generator', 
        strftime('%Y-%m-%d', NEW.timestamp), 
        1,
        'user_id', 
        NEW.user_id
    )
    ON CONFLICT (metric_type, metric_name, timestamp, dimension, dimension_value) 
    DO UPDATE SET value = value + 1;
    
    -- Track complexity scores
    INSERT INTO ReportingMetrics (
        metric_type, metric_name, timestamp, value, dimension, dimension_value
    )
    VALUES (
        'complexity', 'code_map_score', 
        strftime('%Y-%m-%d', NEW.timestamp), 
        NEW.map_complexity_score,
        'user_id', 
        NEW.user_id
    )
    ON CONFLICT (metric_type, metric_name, timestamp, dimension, dimension_value) 
    DO UPDATE SET value = (value + NEW.map_complexity_score) / 2; -- Running average
END;

-- Track LLM usage in reporting metrics
CREATE TRIGGER track_llm_usage
AFTER INSERT ON LlmUsage
BEGIN
    -- Daily token usage
    INSERT INTO ReportingMetrics (
        metric_type, metric_name, timestamp, value, dimension, dimension_value
    )
    VALUES (
        'tokens', NEW.model, 
        strftime('%Y-%m-%d', NEW.timestamp), 
        NEW.total_tokens,
        'provider', 
        NEW.provider
    )
    ON CONFLICT (metric_type, metric_name, timestamp, dimension, dimension_value) 
    DO UPDATE SET value = value + NEW.total_tokens;
    
    -- Cost tracking
    INSERT INTO ReportingMetrics (
        metric_type, metric_name, timestamp, value, dimension, dimension_value
    )
    VALUES (
        'cost', NEW.model, 
        strftime('%Y-%m-%d', NEW.timestamp), 
        NEW.estimated_cost,
        'provider', 
        NEW.provider
    )
    ON CONFLICT (metric_type, metric_name, timestamp, dimension, dimension_value) 
    DO UPDATE SET value = value + NEW.estimated_cost;
    
    -- Update API key usage
    UPDATE ApiKeys 
    SET usage_current = usage_current + NEW.estimated_cost,
        last_used_date = NEW.timestamp
    WHERE id = NEW.api_key_id;
END;

-- Record this schema version
INSERT INTO SchemaVersion (version, applied_date, description) 
VALUES (4, datetime('now'), 'Security and billing tables'); 