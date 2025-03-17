-- Migration: 005_prompt_urgency_levels
-- Created: March 14, 2025
-- Description: Add support for prompt urgency levels in the database

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create PromptUrgencyLevels table to store different urgency levels for each prompt
CREATE TABLE PromptUrgencyLevels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL,
  urgency_level INTEGER NOT NULL,  -- 1 to 10
  content TEXT NOT NULL,           -- Prompt content for this urgency level
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id) ON DELETE CASCADE,
  UNIQUE(prompt_id, urgency_level)
);

-- Add an index for quick lookup by prompt_id and urgency_level
CREATE INDEX idx_prompt_urgency ON PromptUrgencyLevels(prompt_id, urgency_level);

-- Update the Prompts table to add field that identifies if this is a template-based or urgency-based prompt
ALTER TABLE Prompts ADD COLUMN uses_urgency_levels INTEGER DEFAULT 0;  -- Boolean 0/1

-- Record this schema version
INSERT INTO SchemaVersion (version, applied_date, description) 
VALUES (5, datetime('now'), 'Add prompt urgency levels support'); 