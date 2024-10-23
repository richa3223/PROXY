from pytest_bdd import scenarios

scenarios(
    "./features/validate_relationships/1_valid_relationships.feature",
    "./features/validate_relationships/2_valid_relationships_include_parameter.feature",
    "./features/validate_relationships/3_invalid_relationships.feature",
    "./features/validate_relationships/4_operation_outcomes.feature",
)
