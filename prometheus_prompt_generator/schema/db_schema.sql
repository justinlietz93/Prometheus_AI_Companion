-- Prometheus AI Prompt Generator - SQLite Database Schema
-- Created: March 9th, 2025
-- This script creates all tables, indices, and constraints for the Prometheus application

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

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
  last_used TEXT,                -- Last usage timestamp
  FOREIGN KEY (category_id) REFERENCES Categories(id)
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

-- Model registry: Models
CREATE TABLE Models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,     -- Model name
  provider TEXT,                 -- OpenAI, HuggingFace, etc.
  version TEXT,                  -- Model version
  description TEXT,              -- Model details
  is_local INTEGER               -- Boolean local/cloud flag (1/0)
);

-- Benchmark definitions: Benchmarks
CREATE TABLE Benchmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,                     -- Benchmark name
  description TEXT,              -- Benchmark description
  prompt_text TEXT,              -- The prompt used
  created_date TEXT,             -- When created
  user_id TEXT,                  -- Who created it
  metrics TEXT                   -- JSON of metrics used
);

-- Benchmark results: BenchmarkResults
CREATE TABLE BenchmarkResults (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  benchmark_id INTEGER NOT NULL,
  model_id INTEGER NOT NULL,
  prompt_id INTEGER,             -- Optional prompt reference
  accuracy_score REAL,           -- 1-5 accuracy rating
  coherence_score REAL,          -- 1-5 coherence rating
  speed_score REAL,              -- 1-5 speed rating
  relevance_score REAL,          -- 1-5 relevance rating
  response_text TEXT,            -- Model response
  response_time_ms INTEGER,      -- Response time in ms
  timestamp TEXT,                -- When benchmarked
  FOREIGN KEY (benchmark_id) REFERENCES Benchmarks(id) ON DELETE CASCADE,
  FOREIGN KEY (model_id) REFERENCES Models(id) ON DELETE CASCADE,
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id)
);

-- Documentation storage: Documentation
CREATE TABLE Documentation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,                    -- Document title
  content TEXT,                  -- Document content
  file_path TEXT,                -- Original file path
  doc_type TEXT,                 -- API, code, etc.
  tags TEXT,                     -- JSON array of tags
  created_date TEXT,             -- When added
  updated_date TEXT              -- When updated
);

-- Context mapping: PromptDocContext
CREATE TABLE PromptDocContext (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL,
  doc_id INTEGER NOT NULL,
  relevance_score REAL,          -- How relevant the doc is
  is_active INTEGER,             -- Boolean usage flag (1/0)
  inserted_at TEXT,              -- When associated
  FOREIGN KEY (prompt_id) REFERENCES Prompts(id) ON DELETE CASCADE,
  FOREIGN KEY (doc_id) REFERENCES Documentation(id) ON DELETE CASCADE
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

-- Performance indices
CREATE INDEX idx_prompts_type ON Prompts(type);
CREATE INDEX idx_prompts_category ON Prompts(category_id);
CREATE INDEX idx_prompt_versions ON PromptVersions(prompt_id, version_num);
CREATE INDEX idx_prompt_scores ON PromptScores(prompt_id);
CREATE INDEX idx_prompt_usage ON PromptUsage(prompt_id);
CREATE INDEX idx_benchmark_results ON BenchmarkResults(benchmark_id, model_id);
CREATE INDEX idx_prompt_doc_context ON PromptDocContext(prompt_id, doc_id);
CREATE INDEX idx_reporting_metrics ON ReportingMetrics(metric_type, timestamp);

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