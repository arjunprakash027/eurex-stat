# Eurex Feature Engineering Pipeline Documentation

This document provides a guide to the Eurex Feature Engineering Pipeline

## System Architecture

The pipeline follows these core architectural principles:
- **Modularity**: Each transformation is isolated in its own class
- **Extensibility**: New transformers can be added without modifying system code
- **Discoverability**: Transformers are automatically registered and included in the pipeline
- **Abstraction**: A common interface ensures all transformers work consistently

### Key Components

1. **BaseTransformer**: Abstract base class that defines the interface for all transformers
2. **Orchestrator**: Discovers and executes transformers in sequence
3. **Transformers**: Individual processing steps that implement specific data transformations
4. **Main**: Entry point that provides data and executes the pipeline

## Adding New Feature Engineering Steps

### Where to Put Your Code

**The only file(s) you need to modify or create are in the `transformers` directory.**

You have two options:
1. Create a new Python file in the `transformers` directory
2. Add a new class to an existing transformer file

### Creating a New Transformer

To create a new transformer, follow these steps:

1. Create a new Python file in the `transformers` directory (e.g., `my_transformer.py`)
2. Import the BaseTransformer class
3. Define a class that inherits from BaseTransformer
4. Implement the required `process` method
5. Set `is_transformation = True` (optional, as this is the default)

### Example Transformer

Here's a template for creating a new transformer:

```python
"""
My custom transformer for [purpose].
"""

from eurex_feature_engineering.basetransformer import BaseTransformer
import pandas as pd

class MyCustomTransformer(BaseTransformer):
    
    # Optional: explicitly set is_transformation to True (default is already True)
    is_transformation = True
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This method processes the input dataframe and returns the output dataframe
        
        Args:
            df: Input pandas DataFrame
            
        Returns:
            Transformed pandas DataFrame
        """
        # Perform transformations here
        # Example: df['new_column'] = df['existing_column'].apply(some_function)
        
        return df
```

### Best Practices for Transformers

1. **Single Responsibility**: Each transformer should handle one specific type of transformation
2. **Idempotence**: Running the transformer multiple times should produce the same result
3. **Error Handling**: Handle potential errors gracefully to avoid pipeline failures
4. **Documentation**: Document the purpose and behavior of your transformer
5. **Testing**: Consider adding tests for your transformer

## System Files (Do Not Modify)

The following files are part of the core system and should not be modified:

1. **basetransformer.py**: Contains the abstract base class that all transformers inherit from
2. **orchestrator.py**: Dynamically loads and runs transformers
3. **main.py**: Entry point that provides data and invokes the pipeline
4. **utils/stack_and_dedup.py**: Utility functions for data processing

## How the Pipeline Works

1. The `main.py` script loads data and calls the pipeline
2. The `orchestrator.py` script:
   - Discovers all available transformers using dynamic import
   - Registers them in the `BaseTransformer.registry`
   - Creates an instance of each transformer
   - Applies each transformer in sequence to the data
3. Each transformer processes the data according to its implementation
4. The transformed data is returned

## Advanced Usage

### Controlling Transformer Order

The transformers are executed in the order they are discovered and registered. If you need to control the execution order, you can create a custom ordering mechanism in your transformer by overriding the `__init_subclass__` method or implementing a priority system.

### Transformer Dependencies

If a transformer depends on columns created by another transformer, ensure that the dependent transformer is executed after its dependency. You can handle this by:

1. Naming your files to ensure the correct import order (e.g., using numerical prefixes)
2. Implementing a priority system in your transformers
3. Checking for column existence and handling missing dependencies gracefully

### Example Complex Transformer

Here's an example of a more complex transformer that extracts skills from job descriptions:

```python
"""
Skill extraction transformer for job descriptions.
"""

from eurex_feature_engineering.basetransformer import BaseTransformer
import pandas as pd
import re

class SkillsExtractor(BaseTransformer):
    
    def __init__(self):
        # Common tech skills to look for
        self.skill_patterns = [
            'python', 'java', 'javascript', 'sql', 'machine learning',
            'data analysis', 'aws', 'cloud', 'docker', 'kubernetes'
        ]
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract skills from job description"""
        if 'job_description' not in df.columns:
            print("SkillsExtractor: 'job_description' column not found, skipping")
            return df
            
        # Initialize skills columns
        for skill in self.skill_patterns:
            col_name = f"has_{skill.replace(' ', '_')}"
            df[col_name] = False
            
        # Extract skills
        for idx, row in df.iterrows():
            if pd.isna(row['job_description']):
                continue
                
            desc_lower = row['job_description'].lower()
            for skill in self.skill_patterns:
                col_name = f"has_{skill.replace(' ', '_')}"
                df.at[idx, col_name] = bool(re.search(r'\b' + re.escape(skill) + r'\b', desc_lower))
        
        return df
```

## Debugging Tips

1. **Check Registration**: Verify that your transformer is being registered by looking at the log output
2. **Inspect DataFrame**: Add print statements to your transformer to inspect the DataFrame during processing
3. **Exception Handling**: Use try-except blocks to catch and handle errors gracefully
