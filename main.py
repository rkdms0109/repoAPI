from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from decimal import Decimal, ROUND_HALF_UP

app = FastAPI()

# ─── Pydantic 모델 정의 ─────────────────────────────────────────
class Course(BaseModel):
    course_code: str
    course_name: str
    credits: int
    grade: str

class StudentRequest(BaseModel):
    student_id: str
    name: str
    courses: List[Course]

class StudentSummary(BaseModel):
    student_id: str
    name: str
    gpa: float
    total_credits: int

class StudentResponse(BaseModel):
    student_summary: StudentSummary

# ─── 성적 → 점수 매핑 (A+를 4.5점 만점으로 처리) ────────────────────
GRADE_POINTS = {
    "A+": Decimal('4.5'),
    "A":  Decimal('4.0'),
    "B+": Decimal('3.5'),
    "B":  Decimal('3.0'),
    "C+": Decimal('2.5'),
    "C":  Decimal('2.0'),
    "D+": Decimal('1.5'),
    "D":  Decimal('1.0'),
    "F":  Decimal('0.0'),
}

# ─── POST 엔드포인트 ───────────────────────────────────────────────
@app.post("/student_summary", response_model=StudentResponse)
def summarize(request: StudentRequest):
    # 1) 총 이수 학점
    total_credits = sum(c.credits for c in request.courses)

    # 2) (학점 × 점수) 합계
    weighted_sum = sum(
        Decimal(c.credits) * GRADE_POINTS.get(c.grade, Decimal('0.0'))
        for c in request.courses
    )

    # 3) GPA 계산 및 소수점 둘째 자리까지 반올림 (셋째 자리에서 반올림)
    if total_credits == 0:
        gpa = Decimal('0.00')
    else:
        raw = weighted_sum / Decimal(total_credits)
        gpa = raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # 4) JSON 응답 생성
    return {
        "student_summary": {
            "student_id": request.student_id,
            "name":       request.name,
            "gpa":        float(gpa),
            "total_credits": total_credits
        }
    }
