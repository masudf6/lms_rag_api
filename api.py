from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from uuid import UUID
from psycopg2.extras import RealDictCursor
import os
from starlette.responses import RedirectResponse

from database import get_db_connection

from schemas import (
    UserCreate, UserRead,
    CourseCreate, CourseRead,
    EnrollmentCreate, EnrollmentRead,
    CourseMaterialCreate, CourseMaterialRead, CourseMaterialWithFiles,
    AssignmentCreate, AssignmentRead,
    MaterialFileCreate, MaterialFileRead,
    SubmissionCreate, SubmissionRead
)
from crud import (
    create_user, get_user,
    create_course, list_courses_by_teacher,
    create_enrollment,
    create_course_material,
    list_course_materials, list_material_files, get_material_file,
    create_assignment,
    add_material_file,
    create_submission
)

app = FastAPI()

# Allow requests from frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users/", response_model=UserRead)
async def api_create_user(user: UserCreate, conn=Depends(get_db_connection)):
    return create_user(conn, user)

@app.get("/users/{user_id}", response_model=UserRead)
async def api_get_user(user_id: UUID, conn=Depends(get_db_connection)):
    db_user = get_user(conn, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/courses/", response_model=CourseRead)
async def api_create_course(course: CourseCreate, conn=Depends(get_db_connection)):
    return create_course(conn, course)

@app.get("/teachers/{teacher_id}/courses", response_model=List[CourseRead])
async def api_list_teacher_courses(teacher_id: UUID, conn=Depends(get_db_connection)):
    return list_courses_by_teacher(conn, teacher_id)

@app.post("/enrollments/", response_model=EnrollmentRead)
async def api_create_enrollment(enrollment: EnrollmentCreate, conn=Depends(get_db_connection)):
    return create_enrollment(conn, enrollment)

@app.post("/materials/", response_model=CourseMaterialRead)
async def api_create_material(mat: CourseMaterialCreate, conn=Depends(get_db_connection)):
    return create_course_material(conn, mat)

@app.get("/courses/{course_id}/materials", response_model=List[CourseMaterialWithFiles])
async def api_list_course_materials(course_id: UUID, conn = Depends(get_db_connection)):
    materials = list_course_materials(conn, course_id)
    if not materials:
        raise HTTPException(404, f"No materials found for course {course_id}")
    
    # attach files to each material
    # 2. for each, fetch files and build the 'withFiles' model
    result: List[CourseMaterialWithFiles] = []
    for m in materials:
        files = list_material_files(conn, m.material_id)
        # Option A: unpack dict + files into the richer model
        result.append(CourseMaterialWithFiles(**m.dict(), files=files))

        # —or—
        # Option B: use .copy(update=…),
        # result.append(m.copy(update={"files": files}))

    return result

@app.post("/materials/{material_id}/files/", response_model=MaterialFileRead)
async def api_add_file(material_id: UUID, file: MaterialFileCreate, conn=Depends(get_db_connection)):
    # ensuring material_id matches
    if file.material_id != material_id:
        raise HTTPException(status_code=400, detail="Material ID mismatch")
    return add_material_file(conn, file)

@app.get("/files/{file_id}/open")
async def api_open_file(file_id: UUID, conn = Depends(get_db_connection)):
    """
    Redirects the client to the underlying file URL (so PDFs open in-browser).
    """
    mf = get_material_file(conn, file_id)
    if not mf:
        raise HTTPException(404, "File not found")
    return RedirectResponse(url=mf.url)

@app.post("/assignments/", response_model=AssignmentRead)
async def api_create_assignment(assign: AssignmentCreate, conn=Depends(get_db_connection)):
    return create_assignment(conn, assign)

@app.post("/submissions/", response_model=SubmissionRead)
async def api_create_submission(sub: SubmissionCreate, conn=Depends(get_db_connection)):
    return create_submission(conn, sub)

@app.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionRead])
async def api_list_submissions(assignment_id: UUID, conn=Depends(get_db_connection)):
    sql = "SELECT * FROM submissions WHERE assignment_id = %s;"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (assignment_id,))
        rows = cur.fetchall()
    return [SubmissionRead(**r) for r in rows]