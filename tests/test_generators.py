from offset_updater.generators import CodeGenerator


def test_generate_cpp_definitions():
    """Ensure generator creates correct C++ define lines."""
    changes = {
        "get_PlayerHealth": ("0x11111", "0x22222"),
        "NewFunction": (None, "0xAAAAA")
    }

    generator = CodeGenerator()
    output = generator.generate_cpp_definitions(changes)

    assert "#define get_PlayerHealth 0x22222" in output
    assert "#define NewFunction 0xAAAAA" in output
    assert len(output.splitlines()) == 2  # 2 lines expected


def test_generate_json_file_output():
    """Ensure generator creates proper JSON dictionary."""
    changes = {
        "FuncA": ("0x100", "0x200"),
        "FuncB": (None, "0x300")
    }

    generator = CodeGenerator()
    json_data = generator.generate_json(changes)

    assert json_data["FuncA"] == "0x200"
    assert json_data["FuncB"] == "0x300"
