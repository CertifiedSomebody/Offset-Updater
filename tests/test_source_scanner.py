import os
import tempfile
from offset_updater.source_scanner import SourceScanner


def test_scan_files_basic():
    """Test that SourceScanner correctly finds .cpp and .h files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create fake source files
        file1 = os.path.join(tmpdir, "test1.cpp")
        file2 = os.path.join(tmpdir, "test2.h")
        file3 = os.path.join(tmpdir, "ignore.txt")

        # Write dummy contents
        open(file1, "w").write("void FunctionA() {}")
        open(file2, "w").write("int value = 10;")
        open(file3, "w").write("should_not_be_scanned")

        # Instantiate scanner
        scanner = SourceScanner(tmpdir)
        files = scanner.scan_files()

        # Ensure only .cpp and .h files are returned
        assert len(files) == 2
        assert file1 in files
        assert file2 in files
        assert file3 not in files


def test_scan_files_subdirectories():
    """Ensure scanner detects files inside nested directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "src"))
        os.makedirs(os.path.join(tmpdir, "include"))

        file1 = os.path.join(tmpdir, "src", "main.cpp")
        file2 = os.path.join(tmpdir, "include", "defs.h")

        open(file1, "w").write("int main() { return 0; }")
        open(file2, "w").write("#define TEST 1")

        scanner = SourceScanner(tmpdir)
        files = scanner.scan_files()

        assert len(files) == 2
        assert file1 in files
        assert file2 in files


def test_scan_files_filtering():
    """Ensure incorrect file extensions are excluded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        allowed = [
            os.path.join(tmpdir, "a.cpp"),
            os.path.join(tmpdir, "b.h"),
        ]
        disallowed = [
            os.path.join(tmpdir, "c.json"),
            os.path.join(tmpdir, "d.xml"),
            os.path.join(tmpdir, "e.py"),
        ]

        for path in allowed:
            open(path, "w").write("content")

        for path in disallowed:
            open(path, "w").write("content")

        scanner = SourceScanner(tmpdir)
        scanned = scanner.scan_files()

        assert len(scanned) == 2
        for a in allowed:
            assert a in scanned
        for d in disallowed:
            assert d not in scanned
