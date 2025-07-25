import sys

from .io import export_json_file, import_json_file
from .scheduler import SchedulingProblemModel

def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: kepler in.json out.json', file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    problem = import_json_file(input_file)
    solution = SchedulingProblemModel(problem).solve()
    export_json_file(output_file, solution)

if __name__ == '__main__':
    main()
