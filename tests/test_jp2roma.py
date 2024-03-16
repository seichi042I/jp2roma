from src import jp2roma
import pyopenjtalk
import pytest

@pytest.mark.parametrize(
    # argnames
    [
        "input_string",
        "expected"
    ],
    # augvalues
    [
        ("abCd",True),
        ("123",True),
        ("aBcd123",True),
        ("ABCD890",True),
        ("ＡＢＣＤ",False),
        ("あいうえ",False),
        ("１２３４",False),
    ]
)
def test_is_half_width_alphanumeric(input_string,expected):
    result = jp2roma.is_half_width_alphanumeric(input_string)
    
    assert result == expected
    
@pytest.mark.parametrize(
    # argmanes
    [
        "input_list",
        "expected"
    ],
    # argvalues
    [
        (['_','a','b','c'],['a','b','c']),
        (['_','a','b','c','_'],['a','b','c']),
        (['cl','a','b','c','_'],['a','b','c']),
        (['_','_','cl','a','b','c','_','cl','_'],['a','b','c']),
    ]
)
def test_trim_underscores(input_list,expected):
    result = jp2roma.trim_underscores(input_list)
    assert result == expected


@pytest.mark.parametrize(
    # argmanes
    [
        "input_text",
        "expected"
    ],
    #argvalues
    [
        ("もっと", ['m','o','cl','t','o']),
        ("アート", ['a', 'a', 't', 'o']),
        ("それと、これ", ['s', 'o', 'r', 'e', 't', 'o','pau','k','o','r','e']),
        ("って言ってた", ['cl', 't', 'e', 'i', 'cl', 't','e','t','a']),
    ]
)
def test_labels_to_phonemes(input_text,expected):
    njd_features = pyopenjtalk.run_frontend(input_text)
    labels = pyopenjtalk.make_label(njd_features)
    result = jp2roma.labels_to_phonemes(labels)
    assert result == expected

@pytest.mark.parametrize(
    #argmanes
    [
        "input_list",
        "expected"
    ],
    # argvalues
    [
        (['m','o','cl','t','o'],['m','o','t','t','o']),
        (['a','cl','t','o'],['a','t','t','o']),
        (['i','cl','t','e'],['i','t','t','e']),
        (['ch','i','cl','t','a'],['ch','i','t','t','a']),
        (['i','cl','t','a','cl','k','e'],['i','t','t','a','k','k','e']),
    ]
)
def test_replace_cl_with_consonant(input_list,expected):
    result = jp2roma.replace_cl_with_consonant(input_list)
    
    assert result == expected

@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("今日は良い天気ですね", "kyouhayoitenkidesune"),
        ("もっと", "motto"),
        ("アート", "aato"),
        ("前と後ろ", "maetoushiro"),
        ("あれ？", "are"),
        ("それと、これ", "soreto_kore"),
        ("WiFiが使えません", "WiFigatsukaemasen"),
        ("って言ってた", "teitteta"),
        ("3、4、1、スタート！", "3_4_1_sutaato"),
        ("45秒で何ができる？", "45byoudenanigadekiru"),
        ("秒速30万キロメートル", "byousoku30mankiromeetoru"),
    ]
)
def test_jp2roma_conversion(input_text, expected):
    assert jp2roma.jp2roma(input_text) == expected