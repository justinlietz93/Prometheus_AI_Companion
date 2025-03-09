-- Migration: 001_initial_schema
-- Created: March 9th, 2025
-- Description: Initial schema for Prometheus AI Prompt Generator

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS SchemaVersion (
    version INTEGER PRIMARY KEY,
    applied_date TEXT NOT NULL,
    description TEXT
);

-- Core entity: Prompts
CREATE TABLE Prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT UNIQUE NOT NULL,     -- Business key (e.g., 'code_review')
  title TEXT NOT NULL,           -- Display name
  template TEXT NOT NULL,        -- Prompt template text
  description TEXT,              -- Description
  author TEXT,                   -- Creator
  version TEXT,                  -- Version string
  created_date TEXT,             -- ISO format date
  updated_date TEXT,             -- ISO format date
  category_id INTEGER,           -- Category reference
  avg_score REAL,                -- Calculated average score
  usage_count INTEGER DEFAULT 0, -- Usage counter
  last_used TEXT                 -- Last usage timestamp
);

-- Categorization: Tags
CREATE TABLE Tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,     -- Tag name
  description TEXT,              -- Description
  color TEXT                     -- Hex color code
);

-- Organization: Categories
CREATE TABLE Categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,     -- Category name
  description TEXT,              -- Description
  display_order INTEGER,         -- UI display order
  prompt_count INTEGER DEFAULT 0,-- Calculated prompt count
  avg_category_score REAL        -- Calculated average score
);

-- Junction table: PromptTagAssociation
CREATE TABLE PromptTagAssociation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE,
  UNIQUE(prompt_id, tag_id)
);

-- Version control: PromptVersions
CREATE TABLE PromptVersions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL,
  version_num INTEGER NOT NULL,
  template TEXT NOT NULL,
  changes TEXT,
  author TEXT,
  created_date TEXT,
  version_score REAL,
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id) ON DELETE CASCADE,
  UNIQUE(prompt_id, version_num)
);

-- Hierarchy: CategoryHierarchy
CREATE TABLE CategoryHierarchy (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  parent_id INTEGER NOT NULL,
  child_id INTEGER NOT NULL,
  FOREIGN KEY (parent_id) REFERENCES Categories(id) ON DELETE CASCADE,
  FOREIGN KEY (child_id) REFERENCES Categories(id) ON DELETE CASCADE,
  UNIQUE(parent_id, child_id)
);

-- Performance indices for core tables
CREATE INDEX idx_prompts_type ON Prompts(type);
CREATE INDEX idx_prompts_category ON Prompts(category_id);
CREATE INDEX idx_prompt_versions ON PromptVersions(prompt_id, version_num);

-- Create some default categories
INSERT INTO Categories (name, description, display_order) VALUES
('General', 'General-purpose prompts', 1),
('Development', 'Software development prompts', 2),
('Research', 'Research and data analysis prompts', 3),
('Creative', 'Creative writing prompts', 4),
('Business', 'Business and professional prompts', 5);

-- Create some default tags
INSERT INTO Tags (name, description, color) VALUES
('ai', 'Artificial Intelligence', '#007bff'),
('development', 'Software Development', '#28a745'),
('writing', 'Content Writing', '#dc3545'),
('analysis', 'Data Analysis', '#6610f2'),
('productivity', 'Productivity', '#fd7e14');

-- Record this schema version
INSERT INTO SchemaVersion (version, applied_date, description) 
VALUES (1, datetime('now'), 'Initial schema'); 