from ..propGroups.conversions_to_prop_group import parse_struct_string, parse_tuplestruct_string


def test_parse_tuplestruct_string():
    assert parse_tuplestruct_string("(A)") == ['A']
    assert parse_tuplestruct_string("[(A)]") == ['(A)']

    assert parse_tuplestruct_string("(a: 45, b: 65)") == ['a: 45, b: 65']
    assert parse_tuplestruct_string("[(a: 45, b: 65)]") == ['(a: 45, b: 65)']

    assert parse_tuplestruct_string("[(A), (B)]", start_nesting=0) == ['(A), (B)']
    assert parse_tuplestruct_string("[(A), (B)]", start_nesting=1) == ['A','B']


    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62)])", start_nesting=0) == ['[(-1.8, 2.9), (0.0, -62)]']
    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62)])", start_nesting=1) == ['(-1.8, 2.9), (0.0, -62)']
    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62)])", start_nesting=2) == ['-1.8, 2.9', '0.0, -62']
    assert parse_tuplestruct_string("([(-1.8, 2.9), (0.0, -62), (25)])", start_nesting=2) == ['-1.8, 2.9', '0.0, -62', '25']

    assert parse_tuplestruct_string("(Vec3(x:-2.0, y:120.0, z:1.0))", start_nesting=1) == ['x:-2.0, y:120.0, z:1.0']
    #assert parse_tuplestruct_string("(Vec3(x:-2.0, y:120.0, z:1.0))", start_nesting=2) == ['x:-2.0, y:120.0, z:1.0']

    assert parse_tuplestruct_string("(9)") == ['9']
    assert parse_tuplestruct_string('("toto")') == ['"toto"']
    
    assert parse_tuplestruct_string("(Rgba(red:0.0, green:0.2527536153793335, blue:0.9500448703765869, alpha:1.0))") == ['Rgba(red:0.0, green:0.2527536153793335, blue:0.9500448703765869, alpha:1.0)']
    assert parse_tuplestruct_string("(Rgba(red:0.0, green:0.2527536153793335, blue:0.9500448703765869, alpha:1.0))", start_nesting=1) == ['red:0.0, green:0.2527536153793335, blue:0.9500448703765869, alpha:1.0']

    
    

def test_parse_struct_string():
    assert parse_struct_string("a: 45, b:65") == {'a': '45', 'b':'65'}
    assert parse_struct_string("x:-2.0, y:120.0, z:1.0") == {'x': '-2.0', 'y':'120.0', 'z':'1.0'}

    assert parse_struct_string("filters: (25), memberships: (5)") == {'filters': '(25)', 'memberships':'(5)'}
    