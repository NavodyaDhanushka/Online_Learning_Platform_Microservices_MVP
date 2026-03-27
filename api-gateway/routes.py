from fastapi import APIRouter, Request, Response, HTTPException, Depends
from auth import verify_token
import httpx
import schemas

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

            excluded_headers = {
                "content-encoding",
                "content-length",
                "transfer-encoding",
                "connection"
            }

            response_headers = {
                key: value
                for key, value in response.headers.items()
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

# Public
@router.post("/auth/register")
async def register_user(payload: schemas.UserRegister, request: Request):
    return await forward_request(request, USER_SERVICE_URL, "auth/register")


# Public
@router.post("/auth/login")
async def login_user(payload: schemas.UserLogin, request: Request):
    return await forward_request(request, USER_SERVICE_URL, "auth/login")


# Protected
@router.api_route("/users", methods=["GET"])
async def get_users(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users")


# Protected
@router.api_route("/users/me", methods=["GET"])
async def get_me(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users/me")


# Protected
@router.api_route("/users/{user_id}", methods=["GET", "DELETE"])
async def user_by_id(
    user_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, f"users/{user_id}")


# ---------------- COURSE SERVICE ----------------

# Protected - only logged in users can try; course service will still check instructor role
@router.post("/courses/")
async def create_course(
    payload: schemas.CourseCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, COURSE_SERVICE_URL, "courses/")


# Public
@router.api_route("/courses/", methods=["GET"])
async def get_courses(request: Request):
    return await forward_request(request, COURSE_SERVICE_URL, "courses/")


# Public
@router.api_route("/courses/{course_id}", methods=["GET"])
async def get_course_by_id(course_id: int, request: Request):
    return await forward_request(request, COURSE_SERVICE_URL, f"courses/{course_id}")


# Protected
@router.put("/courses/{course_id}")
async def update_course(
    course_id: int,
    payload: schemas.CourseCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, COURSE_SERVICE_URL, f"courses/{course_id}")


# Protected
@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, COURSE_SERVICE_URL, f"courses/{course_id}")