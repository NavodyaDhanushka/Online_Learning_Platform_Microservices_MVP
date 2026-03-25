from fastapi import APIRouter, Request, Response, HTTPException
import httpx

router = APIRouter()

USER_SERVICE_URL = "http://127.0.0.1:8001"
COURSE_SERVICE_URL = "http://127.0.0.1:8002"



async def forward_request(request: Request, target_url: str, path: str = ""):
    url = f"{target_url}/{path}" if path else target_url

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            body = await request.body()

            headers = dict(request.headers)
            headers.pop("host", None)

            response = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=request.query_params
            )

            excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
            response_headers = {
                key: value for key, value in response.headers.items()
                if key.lower() not in excluded_headers
            }

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )


# ---------------- USER SERVICE ----------------

@router.api_route("/auth/register", methods=["POST"])
async def register_user(request: Request):
    return await forward_request(request, USER_SERVICE_URL, "auth/register")


@router.api_route("/auth/login", methods=["POST"])
async def login_user(request: Request):
    return await forward_request(request, USER_SERVICE_URL, "auth/login")


@router.api_route("/users", methods=["GET"])
async def get_users(request: Request):
    return await forward_request(request, USER_SERVICE_URL, "users")


@router.api_route("/users/me", methods=["GET"])
async def get_me(request: Request):
    return await forward_request(request, USER_SERVICE_URL, "users/me")


@router.api_route("/users/{user_id}", methods=["GET", "DELETE"])
async def user_by_id(user_id: int, request: Request):
    return await forward_request(request, USER_SERVICE_URL, f"users/{user_id}")


# ---------------- COURSE SERVICE ----------------

@router.api_route("/courses/", methods=["POST"])
async def create_course(request: Request):
    return await forward_request(request, COURSE_SERVICE_URL, "courses/")


@router.api_route("/courses/", methods=["GET"])
async def get_courses(request: Request):
    return await forward_request(request, COURSE_SERVICE_URL, "courses/")

