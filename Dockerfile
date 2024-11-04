# 베이스 이미지로 Python 3.10 슬림 버전 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일을 복사하고 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY bybit_info.py .

# 컨테이너가 시작될 때 실행될 명령어 설정
CMD ["python", "bybit_info.py"]
