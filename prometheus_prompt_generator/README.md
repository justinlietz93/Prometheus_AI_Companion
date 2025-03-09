# Prometheus AI Prompt Generator

## Overview

The Prometheus AI Prompt Generator is a desktop application for managing, generating, and evaluating AI prompts. It helps users create effective prompts for various AI models, track prompt performance, and share prompts with the community.

## Features

- Create, edit, and organize prompts by category and tags
- Generate new prompts based on templates and context
- Evaluate prompt effectiveness through benchmarking
- Track prompt usage and performance analytics
- Share prompts with the community
- Support for multiple LLM providers (OpenAI, Anthropic, etc.)
- Code map generation for understanding repository structure

## Installation

### Prerequisites

- Python 3.8 or higher
- Qt 6.2 or higher
- SQLite 3.36.0 or higher

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/prometheus_prompt_generator.git
   cd prometheus_prompt_generator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python -m prometheus_prompt_generator.schema.db_init
   ```

4. Run the application:
   ```
   python -m prometheus_prompt_generator
   ```

## Project Structure

- **data/**: Database and configuration files
- **domain/**: Domain models and business logic
- **schema/**: Database schema and migrations
- **services/**: Application services and business operations
- **ui/**: User interface components
- **tests/**: Test files
- **STANDARDS/**: Development standards and guidelines

## Development Standards

This project follows a comprehensive set of development standards to ensure code quality, maintainability, and scalability. The standards are documented in the `STANDARDS/` directory:

- [Architecture Patterns](./STANDARDS/Architecture_Patterns.md): Layered architecture and design patterns
- [SOLID Principles](./STANDARDS/SOLID_Principles.md): Application of SOLID design principles
- [CRUD Standards](./STANDARDS/CRUD_Standards.md): Guidelines for data operations
- [DRY Principle](./STANDARDS/DRY_Principle.md): Code reuse and abstraction guidelines
- [Separation of Concerns](./STANDARDS/Separation_of_Concerns.md): Component responsibilities and boundaries
- [Code Style Guide](./STANDARDS/Code_Style_Guide.md): Coding conventions and formatting
- [Database Standards](./STANDARDS/Database_Standards.md): Database design and usage
- [UI Standards](./STANDARDS/UI_Standards.md): Qt components and user interface guidelines
- [Standards Summary](./STANDARDS/Standards_Summary.md): Quick reference to all standards

For new contributors, please review these standards before submitting changes to the codebase.

## Testing

Run the tests with pytest:

```
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes (following our development standards)
4. Run tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI and Anthropic for their LLM APIs
- Qt for the UI framework
- The contributors to the project

Last updated: March 9, 2025 