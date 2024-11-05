# Dockerfile 작성
# 이 파일을 사용하여 Docker 이미지를 빌드할 수 있습니다.

# 베이스 이미지 설정 (Python 3.9 사용)
FROM python:3.9

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 패키지 복사 및 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 애플리케이션 실행 명령어
CMD ["python", "bybit_ta_integration.py"]
