# Python 3.9 베이스 이미지 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일만 복사 (민감 데이터 유출 방지)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY todo.json .
COPY templates/ templates/

# non-root 사용자 생성 및 전환 (보안 강화)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
