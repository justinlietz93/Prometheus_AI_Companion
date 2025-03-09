-- Migration: 002_analytics_tables
-- Created: March 9th, 2025
-- Description: Add analytics tables for prompt scoring and usage tracking

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Quality tracking: PromptScores
CREATE TABLE PromptScores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL,
  clarity_score REAL,            -- 1-5 clarity rating
  specificity_score REAL,        -- 1-5 specificity rating
  effectiveness_score REAL,      -- 1-5 effectiveness rating
  overall_score REAL,            -- 1-100 combined score
  scorer TEXT,                   -- User or system
  timestamp TEXT,                -- When scored
  feedback TEXT,                 -- Improvement suggestions
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id) ON DELETE CASCADE
);

-- Usage tracking: PromptUsage
CREATE TABLE PromptUsage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL,
  timestamp TEXT,                -- When used
  context_id INTEGER,            -- Usage context reference
  user_id TEXT,                  -- Who used it
  successful INTEGER,            -- Boolean success flag (1/0)
  response_time_ms INTEGER,      -- Response time in ms
  result_summary TEXT,           -- Brief outcome
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id) ON DELETE CASCADE,
  FOREIGN KEY (context_id) REFERENCES UsageContext(id)
);

-- Context: UsageContext
CREATE TABLE UsageContext (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  context_type TEXT,             -- Project, task, etc.
  context_name TEXT,             -- Specific context name
  description TEXT               -- Context details
);

-- Denormalized metrics: ReportingMetrics
CREATE TABLE ReportingMetrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  metric_type TEXT,              -- Usage, score, etc.
  metric_name TEXT,              -- Specific metric
  timestamp TEXT,                -- When recorded
  value REAL,                    -- Metric value
  dimension TEXT,                -- Category, tag, etc.
  dimension_value TEXT           -- Specific dimension value
);

-- Performance indices for analytics tables
CREATE INDEX idx_prompt_scores ON PromptScores(prompt_id);
CREATE INDEX idx_prompt_usage ON PromptUsage(prompt_id);
CREATE INDEX idx_reporting_metrics ON ReportingMetrics(metric_type, timestamp);

-- Add analytics triggers

-- Update average scores when a new score is added
CREATE TRIGGER update_avg_score_insert
AFTER INSERT ON PromptScores
BEGIN
    UPDATE Prompts 
    SET avg_score = (
        SELECT AVG(overall_score) 
        FROM PromptScores 
        WHERE prompt_id = NEW.prompt_id
    )
    WHERE id = NEW.prompt_id;
END;

-- Update average scores when a score is updated
CREATE TRIGGER update_avg_score_update
AFTER UPDATE ON PromptScores
BEGIN
    UPDATE Prompts 
    SET avg_score = (
        SELECT AVG(overall_score) 
        FROM PromptScores 
        WHERE prompt_id = NEW.prompt_id
    )
    WHERE id = NEW.prompt_id;
END;

-- Update usage count when a new usage is recorded
CREATE TRIGGER update_usage_count
AFTER INSERT ON PromptUsage
BEGIN
    UPDATE Prompts 
    SET usage_count = usage_count + 1,
        last_used = NEW.timestamp
    WHERE id = NEW.prompt_id;
END;

-- Record category statistics
CREATE TRIGGER update_category_stats
AFTER UPDATE ON Prompts
BEGIN
    UPDATE Categories
    SET avg_category_score = (
        SELECT AVG(avg_score)
        FROM Prompts
        WHERE category_id = NEW.category_id
        AND avg_score IS NOT NULL
    )
    WHERE id = NEW.category_id;
END;

-- Create reporting metrics function
CREATE TRIGGER record_daily_metrics
AFTER INSERT ON PromptUsage
BEGIN
    -- Daily usage count
    INSERT INTO ReportingMetrics (
        metric_type, metric_name, timestamp, value, dimension, dimension_value
    )
    VALUES (
        'usage', 'daily_count', 
        strftime('%Y-%m-%d', NEW.timestamp), 
        1,
        'prompt_id', 
        NEW.prompt_id
    )
    ON CONFLICT (metric_type, metric_name, timestamp, dimension, dimension_value) 
    DO UPDATE SET value = value + 1;
END;

-- Record this schema version
INSERT INTO SchemaVersion (version, applied_date, description) 
VALUES (2, datetime('now'), 'Analytics tables'); 