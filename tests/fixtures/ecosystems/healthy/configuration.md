# Configuration

> Environment variables and configuration options for DocStratum.

## Environment Variables

### Logging

- `DOCSTRATUM_LOG_LEVEL`: Set to DEBUG, INFO, WARNING, or ERROR (default: INFO)
- `DOCSTRATUM_LOG_FILE`: Path to write logs (default: stdout)

### Performance

- `DOCSTRATUM_CACHE_DIR`: Directory for caching analysis results
- `DOCSTRATUM_MAX_FILE_SIZE`: Maximum file size in bytes (default: 5MB)
- `DOCSTRATUM_WORKERS`: Number of parallel analysis workers (default: 4)

## Configuration File

Create a `docstratum.yaml` in your project root:

```yaml
analysis:
  depth: 3
  follow_external_links: false
  output_format: json
```
