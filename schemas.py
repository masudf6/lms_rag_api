# app/schemas.py

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Literal, List
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password_hash: str
    role: Literal['teacher', 'student']

class UserRead(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    role: Literal['teacher', 'student']
    created_at: datetime
    updated_at: datetime

class CourseCreate(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    teacher_id: UUID

class CourseRead(CourseCreate):
    course_id: UUID
    created_at: datetime
    updated_at: datetime

class EnrollmentCreate(BaseModel):
    student_id: UUID
    course_id: UUID
    details: Optional[str] = None

class EnrollmentRead(EnrollmentCreate):
    created_at: datetime
    updated_at: datetime

class CourseMaterialCreate(BaseModel):
    course_id: UUID
    type: Literal['lecture', 'lab', 'announcement', 'assignment', 'reading']
    title: str
    description: Optional[str] = None

class CourseMaterialRead(CourseMaterialCreate):
    material_id: UUID
    created_at: datetime
    updated_at: datetime

class AssignmentCreate(BaseModel):
    material_id: UUID
    due_date: datetime
    max_grade: int = Field(..., ge=0)

class AssignmentRead(AssignmentCreate):
    assignment_id: UUID
    created_at: datetime
    updated_at: datetime

class MaterialFileCreate(BaseModel):
    material_id: UUID
    name: str
    url: HttpUrl
    file_type: Optional[str] = None
    file_size: Optional[int] = None

class MaterialFileRead(MaterialFileCreate):
    file_id: UUID
    created_at: datetime
    updated_at: datetime

class CourseMaterialWithFiles(CourseMaterialRead):
    files: List[MaterialFileRead]

class SubmissionCreate(BaseModel):
    assignment_id: UUID
    student_id: UUID
    content_url: HttpUrl

class SubmissionRead(BaseModel):
    submission_id: UUID
    assignment_id: UUID
    student_id: UUID
    content_url: HttpUrl
    status: Literal['pending', 'graded', 'submitted']
    grade: Optional[int]
    feedback: Optional[str]
    created_at: datetime
    updated_at: datetime