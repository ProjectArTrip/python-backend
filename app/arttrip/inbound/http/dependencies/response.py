from fastapi import Response


def forbid_response_caching(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
