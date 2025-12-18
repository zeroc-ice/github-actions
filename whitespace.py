# Skip patterns
import fnmatch
import os
import re
import sys


trailingWhitespaceSkipPatterns = [
    r"(Grammar|Scanner)\.(h|cpp|m)",
    "(coeur.utf8)$",
    "(GRADLE_LICENSE)$",
    "(Resource.designer.cs)$",
    "(gradlew|gradlew.bat)$",
]
multipleEmptyLinesSkipPatterns = [
    r"(Grammar|Scanner)\.(h|cpp|m)",
    "(coeur.utf8)$",
    "(GRADLE_LICENSE)$",
    "src/ice/msi/docs/main/THIRD_PARTY_LICENSE.txt",
    "(Resource.designer.cs)$",
    "(gradlew|gradlew.bat)$",
]


def get_tracked_files(exclude_binary=True):
    """Finds all tracked files in the current git repository."""
    files = []
    if exclude_binary:
        pipe = os.popen("git grep -I --name-only  -e .")
    else:
        pipe = os.popen("git ls-files")
    for line in pipe.readlines():
        p = os.path.join(".", line.strip())
        files.append(p)
    return files


def find(pattern, exclude_binary=True):
    """Finds all files matching the given pattern in the current git repository."""
    if not isinstance(pattern, list):
        pattern = [pattern]
    result = []
    for fullpath in get_tracked_files(exclude_binary):
        if os.path.isdir(fullpath):
            continue
        basename = os.path.basename(fullpath)
        for p in pattern:
            if fnmatch.fnmatch(os.path.normpath(fullpath) if "/" in p else basename, p):
                result.append(fullpath)
                break
    return result


def empty_line_max(filename):
    """Returns the maximum number of consecutive empty lines allowed in a file."""
    # Python files can have two empty lines.
    if filename.endswith(".py"):
        return 2
    else:
        return 1


def check_new_line_eof(filename, last_line):
    """Returns true if the last line of the file ends with a newline."""
    skip_patterns = [
        "(.sln|.csproj|.vcxproj|.vcxproj.filters|vcxproj.user|.uwp.appxmanifest|.resx|packages.config|packages.lock.json)$",
        "/Images.xcassets/",
    ]

    for p in skip_patterns:
        if re.search(p, filename):
            return True

    return re.search("\r?\n", last_line)


def check_whitespace(filename):
    """Returns true if the file does not contain trailing whitespace or multiple empty lines."""
    failed = False
    skip_trailing_white_space = False
    skip_multiple_empty_lines = False

    for p in trailingWhitespaceSkipPatterns:
        if re.search(p, filename):
            skip_trailing_white_space = True
    for p in multipleEmptyLinesSkipPatterns:
        if re.search(p, filename):
            skip_multiple_empty_lines = True

    kwargs = {"encoding": "utf-8"}
    try:
        with open(filename, "r", **kwargs) as file:
            lines = file.readlines()

            empty_lines = []
            for line_number, line in enumerate(lines):
                if not skip_multiple_empty_lines and empty_line_max(filename) > 0:
                    if len(line.strip()) == 0:
                        empty_lines.append(line_number)
                    else:  # Non-empty line (maybe first after multiple empty lines)
                        if len(empty_lines) > empty_line_max(filename):
                            print(
                                f"error: {filename} contains multiple empty lines ({empty_lines[0] + 1},{line_number + 1})"
                            )
                            failed = True
                        empty_lines = []

                if not skip_trailing_white_space and re.search("[ \t]+$", line):
                    print(f"error: {filename} contains trailing whitespace")
                    failed = True

            # Ensure exactly one newline at end of file
            if not skip_multiple_empty_lines and len(lines) > 0:
                if len(lines[-1].strip()) == 0:
                    print(f"error: {filename} ends with more than one newline")
                    failed = True
                elif not check_new_line_eof(filename, lines[-1]):
                    print(f"error: {filename} does not end with a newline")
                    failed = True
    except UnicodeDecodeError:
        print(f"error: {filename} is not UTF-8 encoded")
        failed = True

    return not failed


if __name__ == "__main__":
    EXIT_STATUS = 0
    for pattern in sys.argv[1:]:
        foundFiles = find(pattern)
        for f in foundFiles:
            if not check_whitespace(f):
                EXIT_STATUS = 1
    sys.exit(EXIT_STATUS)
