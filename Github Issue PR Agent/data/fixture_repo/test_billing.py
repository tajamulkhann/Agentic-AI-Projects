from billing import total_with_tax

def test_normal():
    assert total_with_tax(100,0.1,0.05)==94.5

def test_precision():
    assert total_with_tax(0.02,0.25,0.05)==0.02
