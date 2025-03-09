# Schema Validation Report

Database: C:\github\prompts\prometheus_prompt_generator\data\prometheus.db
Date: 2025-03-09 09:44:19

## Schema Validation Results

- [PASS] Table Prompts exists
- [PASS] Table Tags exists
- [PASS] Table Categories exists
- [PASS] Table PromptTagAssociation exists
- [PASS] Table PromptVersions exists
- [PASS] Table CategoryHierarchy exists
- [PASS] Table PromptScores exists
- [PASS] Table PromptUsage exists
- [PASS] Table Models exists
- [PASS] Table Benchmarks exists
- [PASS] Table BenchmarkResults exists
- [PASS] Table Documentation exists
- [PASS] Table UsageContext exists
- [PASS] Table ReportingMetrics exists
- [PASS] Table PromptDocContext exists
- [PASS] Table ApiKeys exists
- [PASS] Table CodeMapUsage exists
- [PASS] Table LlmUsage exists
- [PASS] Table SchemaExtension exists
- [PASS] No foreign key constraint violations
- [PASS] Index idx_prompts_type exists
- [PASS] Index idx_prompts_category exists
- [PASS] Index idx_prompts_custom exists
- [PASS] Index idx_prompt_scores exists
- [PASS] Index idx_prompt_usage exists
- [PASS] Index idx_reporting_metrics exists
- [PASS] Index idx_benchmark_results exists
- [PASS] Index idx_prompt_doc_context exists
- [PASS] Index idx_api_keys exists
- [PASS] Index idx_code_map_usage exists
- [PASS] Index idx_llm_usage exists
- [PASS] Index idx_llm_usage_billing exists
- [PASS] Index idx_schema_extension exists

## Performance Test Results

- Get all prompts: 0.21ms (avg over 5 runs, 3 rows)
- [PASS] Performance within requirements (<100ms)
- Get prompts by type: 0.16ms (avg over 5 runs, 1 rows)
- [PASS] Performance within requirements (<100ms)
- Get prompts with tags: 0.20ms (avg over 5 runs, 3 rows)
- [PASS] Performance within requirements (<100ms)
- Get prompt usage statistics: 0.20ms (avg over 5 runs, 3 rows)
- [PASS] Performance within requirements (<100ms)
- Search prompts by title or description: 0.17ms (avg over 5 runs, 0 rows)
- [PASS] Performance within requirements (<100ms)
- Get benchmark results by model: 0.16ms (avg over 5 runs, 6 rows)
- [PASS] Performance within requirements (<100ms)
- Get API keys by provider: 0.26ms (avg over 5 runs, 1 rows)
- [PASS] Performance within requirements (<100ms)
- Get LLM usage statistics: 0.21ms (avg over 5 runs, 2 rows)
- [PASS] Performance within requirements (<100ms)
- Get code map usage by user: 0.18ms (avg over 5 runs, 2 rows)
- [PASS] Performance within requirements (<100ms)

## Summary

[PASS] Schema validation passed
[PASS] Performance tests passed
