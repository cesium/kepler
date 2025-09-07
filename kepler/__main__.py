import sys

from . import api
from . import io
from .scheduler import SchedulingProblemModel, SchedulingProblemModelError

def main() -> None:
    if len(sys.argv) == 4 and sys.argv[1] == 'solve':
        input_file = sys.argv[2]
        output_file = sys.argv[3]

        try:
            problem = io.import_json_problem_file(input_file)
            model = SchedulingProblemModel(problem)
            solution = model.solve()
            io.export_json_solution_file(output_file, solution)
        except (io.JsonImporterError, io.JsonExporterError, SchedulingProblemModelError) as e:
            print(str(e), file=sys.stderr)

    elif len(sys.argv) == 2 and sys.argv[1] == 'api':
        api.API().run()

    else:
        print('Usage:',                                                      file=sys.stderr)
        print('  kepler solve <problem-input.json> <schedules-output.json>', file=sys.stderr)
        print('  kepler api',                                                file=sys.stderr)

if __name__ == '__main__':
    main()
