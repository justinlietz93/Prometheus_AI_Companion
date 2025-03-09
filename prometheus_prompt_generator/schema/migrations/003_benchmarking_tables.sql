-- Migration: 003_benchmarking_tables
-- Created: March 9th, 2025
-- Description: Add LLM benchmarking tables and documentation context

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

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

-- Performance indices for benchmarking tables
CREATE INDEX idx_benchmark_results ON BenchmarkResults(benchmark_id, model_id);
CREATE INDEX idx_prompt_doc_context ON PromptDocContext(prompt_id, doc_id);

-- Create some default models
INSERT INTO Models (name, provider, version, description, is_local) VALUES
('gpt-4-turbo', 'OpenAI', '2023-11', 'Large-scale language model with 1.8 trillion parameters', 0),
('claude-3-opus', 'Anthropic', '2024-01', 'Advanced reasoning model with 175 billion parameters', 0),
('llama-3-70b', 'Meta', '2024-02', 'Open source model with 70 billion parameters', 1),
('mistral-7b', 'Mistral AI', '2023-12', 'Efficient 7 billion parameter model', 1),
('baby-prometheus', 'Prometheus AI', '2025-03', 'Custom fine-tuned model', 1);

-- Add benchmarking views for reporting
CREATE VIEW BenchmarkScores AS
SELECT 
    b.name AS benchmark_name,
    m.name AS model_name,
    m.provider,
    p.type AS prompt_type,
    AVG(br.accuracy_score) AS avg_accuracy,
    AVG(br.coherence_score) AS avg_coherence,
    AVG(br.speed_score) AS avg_speed,
    AVG(br.relevance_score) AS avg_relevance,
    AVG(br.response_time_ms) AS avg_response_time,
    COUNT(*) AS run_count
FROM 
    BenchmarkResults br
JOIN 
    Benchmarks b ON br.benchmark_id = b.id
JOIN 
    Models m ON br.model_id = m.id
LEFT JOIN 
    Prompts p ON br.prompt_id = p.id
GROUP BY 
    b.id, m.id, p.id;

-- Add documentation context view
CREATE VIEW DocumentContext AS
SELECT 
    p.type AS prompt_type,
    d.title AS doc_title,
    d.doc_type,
    pdc.relevance_score,
    pdc.is_active
FROM 
    PromptDocContext pdc
JOIN 
    Prompts p ON pdc.prompt_id = p.id
JOIN 
    Documentation d ON pdc.doc_id = d.id;

-- Record this schema version
INSERT INTO SchemaVersion (version, applied_date, description) 
VALUES (3, datetime('now'), 'Benchmarking tables'); 