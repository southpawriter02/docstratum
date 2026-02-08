# Getting Started with DocStratum

> Learn how to set up and run your first analysis in just 5 minutes.

## Installation

DocStratum requires Python 3.8+. Install via pip:

```bash
pip install docstratum
```

## First Analysis

Create a simple script to analyze your documentation:

```python
from docstratum import Analyzer

analyzer = Analyzer()
results = analyzer.analyze('./docs')
print(f"Found {len(results)} issues")
```

## Next Steps

- Review the API Reference for advanced features
- Check Configuration for environment setup
- Explore examples in the project repository
