# app/crud.py

from psycopg2.extras import RealDictCursor
from uuid import UUID
from typing import List
from schemas import (
    UserCreate, UserRead,
    CourseCreate, CourseRead,
    EnrollmentCreate, EnrollmentRead,
    CourseMaterialCreate, CourseMaterialRead,
    AssignmentCreate, AssignmentRead,
    MaterialFileCreate, MaterialFileRead,
    SubmissionCreate, SubmissionRead
)

def create_user(conn, user_in: UserCreate) -> UserRead:
    sql = """
    INSERT INTO users (name, email, password_hash, role)
    VALUES (%s, %s, %s, %s)
    RETURNING user_id, name, email, role, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (user_in.name, user_in.email, user_in.password_hash, user_in.role))
        row = cur.fetchone()
    conn.commit()
    return UserRead(**row)

def get_user(conn, user_id: UUID) -> UserRead:
    sql = """
    SELECT user_id, name, email, role, created_at, updated_at
      FROM users
     WHERE user_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (user_id,))
        row = cur.fetchone()
    return UserRead(**row) if row else None

def create_course(conn, c: CourseCreate) -> CourseRead:
    sql = """
    INSERT INTO courses (code, title, description, teacher_id)
    VALUES (%s, %s, %s, %s)
    RETURNING course_id, code, title, description, teacher_id, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (c.code, c.title, c.description, c.teacher_id))
        row = cur.fetchone()
    conn.commit()
    return CourseRead(**row)

def list_courses_by_teacher(conn, teacher_id: UUID) -> List[CourseRead]:
    sql = """
    SELECT course_id, code, title, description, teacher_id, created_at, updated_at
      FROM courses
     WHERE teacher_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (teacher_id,))
        rows = cur.fetchall()
    return [CourseRead(**r) for r in rows]

def create_enrollment(conn, e: EnrollmentCreate) -> EnrollmentRead:
    sql = """
    INSERT INTO enrollments (student_id, course_id, details)
    VALUES (%s, %s, %s)
    RETURNING student_id, course_id, details, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (e.student_id, e.course_id, e.details))
        row = cur.fetchone()
    conn.commit()
    return EnrollmentRead(**row)

def create_course_material(conn, m: CourseMaterialCreate) -> CourseMaterialRead:
    sql = """
    INSERT INTO course_materials (course_id, type, title, description)
    VALUES (%s, %s, %s, %s)
    RETURNING material_id, course_id, type, title, description, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (m.course_id, m.type, m.title, m.description))
        row = cur.fetchone()
    conn.commit()
    return CourseMaterialRead(**row)

def list_course_materials(conn, course_id: UUID) -> List[CourseMaterialRead]:
    sql = """
    SELECT material_id, course_id, type, title, description, created_at, updated_at
      FROM course_materials
     WHERE course_id = %s
     ORDER BY created_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (course_id,))
        rows = cur.fetchall()
    return [CourseMaterialRead(**r) for r in rows]

def create_assignment(conn, a: AssignmentCreate) -> AssignmentRead:
    sql = """
    INSERT INTO assignments (material_id, due_date, max_grade)
    VALUES (%s, %s, %s)
    RETURNING assignment_id, material_id, due_date, max_grade, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (a.material_id, a.due_date, a.max_grade))
        row = cur.fetchone()
    conn.commit()
    return AssignmentRead(**row)

def add_material_file(conn, f: MaterialFileCreate) -> MaterialFileRead:
    sql = """
    INSERT INTO material_files (material_id, name, url, file_type, file_size)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING file_id, material_id, name, url, file_type, file_size, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (f.material_id, f.name, str(f.url), f.file_type, f.file_size))
        row = cur.fetchone()
    conn.commit()
    return MaterialFileRead(**row)

def list_material_files(conn, material_id: UUID) -> List[MaterialFileRead]:
    sql = """
    SELECT file_id, material_id, name, url, file_type, file_size, created_at, updated_at
      FROM material_files
     WHERE material_id = %s
     ORDER BY updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (material_id,))
        rows = cur.fetchall()
    return [MaterialFileRead(**r) for r in rows]

def get_material_file(conn, file_id: UUID) -> MaterialFileRead:
    sql = """
    SELECT file_id, material_id, name, url, file_type, file_size, created_at, updated_at
      FROM material_files
     WHERE file_id = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (file_id,))
        row = cur.fetchone()
    return MaterialFileRead(**row) if row else None

def create_submission(conn, s: SubmissionCreate) -> SubmissionRead:
    sql = """
    INSERT INTO submissions (assignment_id, student_id, content_url)
    VALUES (%s, %s, %s)
    RETURNING submission_id, assignment_id, student_id, content_url, status, grade, feedback, created_at, updated_at;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (s.assignment_id, s.student_id, str(s.content_url)))
        row = cur.fetchone()
    conn.commit()
    return SubmissionRead(**row)