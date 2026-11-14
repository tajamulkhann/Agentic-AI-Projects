import pytest
from agentic_core.model_bridge import validate_plan

def test_accepts_known_tool_order():
    assert validate_plan({'steps':['search','compare','search']},['search','compare']) == ['search','compare']

def test_blocks_unknown_or_malformed_model_tool():
    with pytest.raises(ValueError):validate_plan({'steps':['execute_shell']},['search'])
    with pytest.raises(ValueError):validate_plan({'step':'search'},['search'])
