from fastapi import APIRouter, Request, Response, HTTPException, Depends
from auth import verify_token, require_instructor
import httpx
import schemas

router = APIRouter()

USER_SERVICE_URL = "http://127.0.0.1:8010"
COURSE_SERVICE_URL = "http://127.0.0.1:8011"
ENROLLMENT_SERVICE_URL = "http://127.0.0.1:8012"
REVIEW_SERVICE_URL = "http://127.0.0.1:8013"


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

@router.post("/auth/register")
async def register_user(payload: schemas.UserRegister, request: Request):
    return await forward_request(request, USER_SERVICE_URL, "auth/register")


@router.post("/auth/login")
async def login_user(payload: schemas.UserLogin, request: Request):
    return await forward_request(request, USER_SERVICE_URL, "auth/login")


@router.get("/users")
async def get_users(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users")


@router.get("/users/me")
async def get_me(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users/me")

# Protected
@router.put("/users/me")
async def update_my_profile(
    payload: schemas.UserUpdate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users/me")

@router.get("/users/me/courses")
async def get_my_courses(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users/me/courses")

@router.get("/users/me/enrolled-courses")
async def get_my_enrolled_courses(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, "users/me/enrolled-courses")

@router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, USER_SERVICE_URL, f"users/{user_id}")


@router.delete("/users/{user_id}")
async def delete_user_by_id(
    user_id: int,
    request: Request,
    current_user: dict = Depends(require_instructor)
):
    return await forward_request(request, USER_SERVICE_URL, f"users/{user_id}")


# ---------------- COURSE SERVICE ----------------

@router.post("/courses/")
async def create_course(
    payload: schemas.CourseCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, COURSE_SERVICE_URL, "courses/")


@router.get("/courses/")
async def get_courses(request: Request):
    return await forward_request(request, COURSE_SERVICE_URL, "courses/")


@router.get("/courses/instructor/{instructor_id}")
async def get_courses_by_instructor(
    instructor_id: int,
    request: Request
):
    return await forward_request(
        request,
        COURSE_SERVICE_URL,
        f"courses/instructor/{instructor_id}"
    )


@router.get("/courses/{course_id}/students")
async def get_course_students(
    course_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(
        request,
        COURSE_SERVICE_URL,
        f"courses/{course_id}/students"
    )


@router.get("/courses/{course_id}")
async def get_course_by_id(course_id: int, request: Request):
    return await forward_request(request, COURSE_SERVICE_URL, f"courses/{course_id}")


@router.put("/courses/{course_id}")
async def update_course(
    course_id: int,
    payload: schemas.CourseCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, COURSE_SERVICE_URL, f"courses/{course_id}")


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, COURSE_SERVICE_URL, f"courses/{course_id}")


# ---------------- ENROLLMENT SERVICE ----------------

@router.post("/enrollments")
async def create_enrollment(
    payload: schemas.EnrollmentCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, ENROLLMENT_SERVICE_URL, "enrollments")


@router.get("/enrollments")
async def list_enrollments(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, ENROLLMENT_SERVICE_URL, "enrollments")


@router.get("/enrollments/check")
async def check_enrollment(
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, ENROLLMENT_SERVICE_URL, "enrollments/check")


@router.get("/enrollments/course/{course_id}")
async def get_enrollments_by_course(
    course_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(
        request,
        ENROLLMENT_SERVICE_URL,
        f"enrollments/course/{course_id}"
    )


@router.get("/enrollments/{enrollment_id}")
async def get_enrollment(
    enrollment_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(
        request,
        ENROLLMENT_SERVICE_URL,
        f"enrollments/{enrollment_id}"
    )


@router.put("/enrollments/{enrollment_id}")
async def update_enrollment(
    enrollment_id: int,
    payload: schemas.EnrollmentCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(
        request,
        ENROLLMENT_SERVICE_URL,
        f"enrollments/{enrollment_id}"
    )


@router.delete("/enrollments/{enrollment_id}")
async def delete_enrollment(
    enrollment_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(
        request,
        ENROLLMENT_SERVICE_URL,
        f"enrollments/{enrollment_id}"
    )

# ---------------- REVIEW SERVICE ----------------

@router.post("/reviews/")
async def create_review(
    payload: schemas.ReviewCreate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, REVIEW_SERVICE_URL, "reviews/")


@router.get("/reviews/")
async def get_reviews(request: Request):
    return await forward_request(request, REVIEW_SERVICE_URL, "reviews/")


@router.put("/reviews/{review_id}")
async def update_review(
    review_id: int,
    payload: schemas.ReviewUpdate,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, REVIEW_SERVICE_URL, f"reviews/{review_id}")


@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: int,
    request: Request,
    current_user: dict = Depends(verify_token)
):
    return await forward_request(request, REVIEW_SERVICE_URL, f"reviews/{review_id}")