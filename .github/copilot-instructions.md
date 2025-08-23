# GitHub Copilot Instructions

## Documentation Guidelines
- Always use Google-style docstrings for all functions and classes
- Keep docstrings concise and to the point, avoid excessive detail
- Write all documentation in English only

## Logging Guidelines
- Use `info` level for tracking progress and workflow advancement
- Use `debug` level for displaying results, input values, and detailed information
- Follow this naming convention for all log messages:
    ```
    {function_name} :: {log message/information}
    ```
Example:
def example_function(param1, param2):
    """
    Example function that demonstrates logging and documentation standards.

    Args:
        param1 (str): Description of param1.
        param2 (int): Description of param2.

    Returns:
        bool: Description of the return value.
    """
    logger.info("example_function :: Starting function execution")
    result = some_processing(param1, param2)
    logger.debug(f"example_function :: Processing result: {result}")
    logger.info("example_function :: Function execution completed")
    return result

## Pydantic Guidelines
- Use Pydantic BaseModel for creating value objects and entities
- Always use Field() from pydantic to define field constraints and descriptions
- Provide clear and descriptive field descriptions for all attributes
- Use appropriate type hints and validation rules

Example:
"""
class Query(BaseModel):
    """
    Value Object for a user query.
    Immutable object representing a question/request.
    """
    model_config = ConfigDict(frozen=True)
    content: str = Field(..., description="The content of the query, typically a question or request.")
"""