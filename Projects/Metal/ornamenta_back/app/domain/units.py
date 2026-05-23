import pint

# Create a single, centralized unit registry.
# This ensures consistency across the entire application.
# All parts of the app that need to work with units should import `unit_registry` from this file.
unit_registry = pint.UnitRegistry()

# Backward compatibility alias (you can remove this later if you update all imports)
ureg = unit_registry  # pylint: disable=invalid-name
