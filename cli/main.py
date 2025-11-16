import argparse
import json
import os
from offset_updater.dump_parser import DumpParser
from offset_updater.source_scanner import SourceScanner
from offset_updater.offset_analyzer import OffsetAnalyzer
from offset_updater.generators import CodeGenerator
from offset_updater.reporter import Reporter


def load_existing_offsets(source_files):
    """
    Extract existing offsets from source code.

    This version assumes offsets appear in the format:
        #define FunctionName 0x123456
    """
    offsets = {}

    for file in source_files:
        try:
            with open(file, "r", errors="ignore") as f:
                for line in f:
                    line = line.strip()

                    if line.startswith("#define"):
                        parts = line.split()
                        if len(parts) == 3:
                            name = parts[1]
                            value = parts[2]
                            offsets[name] = value
        except Exception:
            pass

    return offsets


def save_generated_files(generator, changes, output_dir):
    """Save all generated outputs into target directory."""
    os.makedirs(output_dir, exist_ok=True)

    # write updated C++ defines
    cpp_output = generator.generate_cpp_definitions(changes)
    with open(os.path.join(output_dir, "offsets_updated.h"), "w") as fp:
        fp.write(cpp_output)

    # write JSON file
    json_output = generator.generate_json(changes)
    with open(os.path.join(output_dir, "offsets.json"), "w") as fp:
        json.dump(json_output, fp, indent=4)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Offset Updater CLI — Automatically detect and update game offsets."
    )

    parser.add_argument(
        "--dump",
        required=True,
        help="Path to the IL2CPP dump file or JSON symbols file."
    )

    parser.add_argument(
        "--src",
        required=True,
        help="Path to the project source folder that contains existing offsets."
    )

    parser.add_argument(
        "--out",
        default="output",
        help="Folder where updated offset files will be written."
    )

    args = parser.parse_args()

    print("🔍 Parsing dump...")
    dump_parser = DumpParser(args.dump)
    parsed_dump = dump_parser.parse()

    print("📡 Scanning source directory...")
    scanner = SourceScanner(args.src)
    source_files = scanner.scan_files()

    print("📄 Reading existing offsets...")
    existing_offsets = load_existing_offsets(source_files)

    print("🧠 Analyzing offset differences...")
    analyzer = OffsetAnalyzer(parsed_dump)
    changes = analyzer.analyze(existing_offsets)

    reporter = Reporter()
    summary_text = reporter.summary(changes)

    print("\n=========== SUMMARY OF CHANGES ===========")
    print(summary_text)
    print("==========================================\n")

    if not changes:
        print("👍 No changes needed. Everything is up-to-date.")
        return

    print("⚙️ Generating updated output files...")
    generator = CodeGenerator()
    save_generated_files(generator, changes, args.out)

    print(f"✅ Offset update complete! Files saved to: {args.out}")


if __name__ == "__main__":
    main()
