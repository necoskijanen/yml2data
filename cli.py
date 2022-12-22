import argparse
import textwrap
from main import execute


if __name__ == "__main__":
    desc = '''
        yml2data
            read yml, generate date (json, csv, etc)
    '''
    parser = argparse.ArgumentParser(description=textwrap.dedent(desc)[1:-1])
    parser.add_argument("--input", type=str, dest="input", nargs=1, required=True,
                        help="select input yml file")
    parser.add_argument("--pattern", type=str, dest="pattern", nargs="+",
                        help="Output a pattern of specific outputs")

    args = parser.parse_args()
    execute(args.input[0], args.pattern)
