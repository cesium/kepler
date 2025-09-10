from concurrent.futures import Future, ThreadPoolExecutor
import uuid

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import uvicorn

from . import io
from .scheduler import SchedulingProblemModel, SchedulingProblemModelError
from .types import SchedulingProblemSolution

class API:
    def __init__(self) -> None:
        self.__jobs: dict[uuid.UUID, Future[SchedulingProblemSolution]] = {}
        self.__executor = ThreadPoolExecutor(max_workers=1)

        self.__starlette = Starlette(routes=[
            Route('/api/v1/solve', self.__solve, methods=['POST']),
            Route('/api/v1/solution/{jobid:uuid}', self.__solution, methods=['GET'])
        ], exception_handlers={
            HTTPException: lambda _, e: JSONResponse({'error': e.detail}, status_code=e.status_code)
        })

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        uvicorn.run(self.__starlette, host=host, port=port)

    async def __solve(self, request: Request) -> JSONResponse:
        try:
            payload_text = (await request.body()).decode('utf-8')
            problem = io.import_json_problem_string(payload_text)
        except (UnicodeDecodeError, io.JsonImporterError) as e:
            raise HTTPException(400, detail=str(e)) from e

        model = SchedulingProblemModel(problem)
        jobid = uuid.uuid4()
        self.__jobs[jobid] = self.__executor.submit(model.solve)

        return JSONResponse({'jobid': str(jobid)})

    async def __solution(self, request: Request) -> JSONResponse:
        jobid = request.path_params['jobid']
        job = self.__jobs.get(jobid)

        if job is None:
            raise HTTPException(404, detail='Job not found or removed from cache')
        elif job.done():
            try:
                solution = job.result()
                solution_json_object = io.export_json_solution_object(solution)

                del self.__jobs[jobid]
                return JSONResponse({'schedules': solution_json_object})
            except SchedulingProblemModelError as e:
                del self.__jobs[jobid]
                raise HTTPException(500, detail=str(e)) from e

        elif job.running():
            return JSONResponse({'status': 'Running'})
        else:
            return JSONResponse({'status': 'Queued'})
