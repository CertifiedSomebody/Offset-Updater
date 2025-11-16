import os
import tempfile
from offset_updater.dump_parser import DumpParser


# ---------------------------------------------------------
# Helper: create a temporary dump.cs file
# ---------------------------------------------------------
def create_temp_dump(content: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".cs")
    tmp.write(content.encode("utf-8"))
    tmp.close()
    return tmp.name


# ---------------------------------------------------------
# Test: basic offset parsing
# ---------------------------------------------------------
def test_basic_dump_parsing():
    content = """
    // Example dump file
    public static IntPtr Subtract => (IntPtr)0x31557C0;
    public static IntPtr AddStuff => (IntPtr)0xABCDEF;
    """

    path = create_temp_dump(content)
    parser = DumpParser()
    result = parser.parse(path)

    assert result is not None
    assert result.get("Subtract") == "31557C0"
    assert result.get("AddStuff") == "ABCDEF"

    os.remove(path)


# ---------------------------------------------------------
# Test: duplicate method names (should keep last occurrence)
# ---------------------------------------------------------
def test_duplicate_methods():
    content = """
    public static IntPtr DoSomething => (IntPtr)0x111111;
    public static IntPtr DoSomething => (IntPtr)0x222222;
    """

    path = create_temp_dump(content)
    parser = DumpParser()
    result = parser.parse(path)

    # Last one should override
    assert result["DoSomething"] == "222222"

    os.remove(path)


# ---------------------------------------------------------
# Test: malformed hex values are ignored
# ---------------------------------------------------------
def test_malformed_hex():
    content = """
    public static IntPtr Broken => (IntPtr)0xZZZZZZ;  // invalid
    public static IntPtr Valid  => (IntPtr)0x123ABC;
    """

    path = create_temp_dump(content)
    parser = DumpParser()
    result = parser.parse(path)

    assert "Valid" in result
    assert result["Valid"] == "123ABC"

    # Broken should NOT be included
    assert "Broken" not in result

    os.remove(path)


# ---------------------------------------------------------
# Test: empty file returns empty dict
# ---------------------------------------------------------
def test_empty_dump():
    path = create_temp_dump("")
    parser = DumpParser()
    result = parser.parse(path)

    assert result == {}

    os.remove(path)


# ---------------------------------------------------------
# Test: no matching patterns returns empty
# ---------------------------------------------------------
def test_no_offsets_found():
    content = """
    // unrelated text
    class Foo {}
    int x = 5;
    """

    path = create_temp_dump(content)
    parser = DumpParser()
    result = parser.parse(path)

    assert result == {}

    os.remove(path)
