# API Reference

> Complete reference for all public DocStratum APIs and their parameters.

## Analyzer Class

### Methods

#### `analyze(path: str, config: Optional[Dict])`

Analyze a documentation ecosystem at the given path.

**Parameters:**
- `path` (str): Root directory of the documentation
- `config` (Dict): Optional configuration dictionary

**Returns:**
- `AnalysisResult`: Object containing metrics and issues

#### `validate(config: Dict)`

Validate ecosystem configuration format and values.

**Parameters:**
- `config` (Dict): Configuration to validate

**Returns:**
- `bool`: True if valid, raises ValueError otherwise

## Result Types

Analysis results include:
- Health score (0-100)
- Issue list with severity levels
- Ecosystem type classification
