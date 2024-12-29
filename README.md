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

## 설치 방법
```bash
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
