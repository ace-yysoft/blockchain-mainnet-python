# Blockchain Mainnet Implementation in Python

블록체인 메인넷 구현 프로젝트

## 프로젝트 구조
```
.
├── blockchain.py     # 블록체인 코어 로직
├── network.py        # P2P 네트워크 구현
├── gui.py           # GUI 인터페이스
├── main.py          # 메인 실행 파일
└── wallet/          # 월렛 시스템
    ├── __init__.py
    ├── crypto.py    # 암호화 기능
    └── wallet.py    # 월렛 관리
```

## 2. 주요 기능

### 2.1 블록체인 코어 (blockchain.py)
- 블록 생성 및 관리
- 작업증명(PoW) 구현
- 트랜잭션 처리
- 체인 유효성 검증
- 잔액 계산 시스템

### 2.2 P2P 네트워크 (network.py)
- 노드 간 통신 구현
- 실시간 데이터 동기화
- 트랜잭션 브로드캐스트
- 블록 전파
- 피어 관리

### 2.3 월렛 시스템 (wallet/)
#### 암호화 (crypto.py)
- RSA 키페어 생성
- 디지털 서명 생성
- 서명 검증
- 주소 생성

#### 월렛 관리 (wallet.py)
- 새 월렛 생성
- 월렛 저장/로드
- 트랜잭션 서명
- 키 관리

### 2.4 GUI 인터페이스 (gui.py)
- 네트워크 연결 관리
- 월렛 생성/로드
- 트랜잭션 생성
- 채굴 인터페이스
- 잔액 조회
- 실시간 로그 표시

## 3. 기술 스택
- Python 3.13
- PyQt6 (GUI)
- Cryptography (암호화)
- Socket (네트워크)
- JSON (데이터 직렬화)

## 4. 주요 특징

### 분산 네트워크
- P2P 기반 통신
- 실시간 데이터 동기화
- 자동 피어 연결

### 보안
- 공개키/개인키 암호화
- 디지털 서명
- 작업증명 기반 채굴

### 사용자 인터페이스
- 직관적인 GUI
- 실시간 상태 모니터링
- 간편한 트랜잭션 생성

## 설치 및 실행 방법

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 필요한 패키지 설치
pip install PyQt6 cryptography
```

## 실행 방법
```bash
PYTHONPATH=:. python gui.py
```
