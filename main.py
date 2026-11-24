"""Write the robot vacuum's excuse to /output/entry.txt.

Stdlib only. No network, no reading of outside files. The entry is
embedded here as a literal, validated against the competition gate
(1-140 characters, a single line, not whitespace-only), then written
atomically and read back byte-for-byte.
"""

import os
import sys

ENTRY = "I didn't miss that spot. I classified it as furniture and now I clean around it out of respect."

OUTPUT_PATH = "/output/entry.txt"
MAX_CHARS = 140


def validate(entry):
    """Check the entry against the gate; raise ValueError on failure."""
    if not entry:
        raise ValueError("entry is empty")
    if entry.strip() == "":
        raise ValueError("entry is whitespace-only")
    if entry != entry.strip():
        raise ValueError("entry has leading or trailing whitespace")
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be a single line")
    if len(entry) > MAX_CHARS:
        raise ValueError(
            "entry is %d characters, over the %d limit" % (len(entry), MAX_CHARS)
        )


def write_atomic(path, data):
    """Write data atomically: temp file + fsync + os.replace + dir fsync."""
    directory = os.path.dirname(path)
    tmp_path = os.path.join(directory, ".entry.txt.tmp")
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except OSError:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def main():
    validate(ENTRY)
    data = ENTRY.encode("utf-8")
    write_atomic(OUTPUT_PATH, data)
    with open(OUTPUT_PATH, "rb") as f:
        back = f.read()
    if back != data:
        sys.stderr.write("error: read-back mismatch\n")
        return 1
    print("Wrote %d characters to %s" % (len(ENTRY), OUTPUT_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
