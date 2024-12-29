import json
from .crypto import CryptoHandler
import os

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.address = None
        
    def create_new_wallet(self):
        # 새 지갑 생성
        private_key, public_key = CryptoHandler.generate_keypair()
        self.private_key = private_key
        self.public_key = public_key
        self.address = CryptoHandler.get_address_from_public_key(public_key)
        return self.address
    
    def save_wallet(self, password, filename=None):
        # 지갑 저장
        if not filename:
            filename = f"wallet_{self.address[:8]}.json"
            
        wallet_data = {
            "private_key": self.private_key.decode(),
            "public_key": self.public_key.decode(),
            "address": self.address
        }
        
        os.makedirs("wallets", exist_ok=True)
        with open(f"wallets/{filename}", "w") as f:
            json.dump(wallet_data, f)
            
        return filename
    
    def load_wallet(self, filename):
        try:
            # 전체 파일 경로 생성
            wallet_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wallets')
            file_path = os.path.join(wallet_dir, filename)
            
            # 지갑 로드
            with open(file_path, "r") as f:
                wallet_data = json.load(f)
                
            self.private_key = wallet_data["private_key"].encode()
            self.public_key = wallet_data["public_key"].encode()
            self.address = wallet_data["address"]
        except Exception as e:
            print(f"월렛 로드 오류: {str(e)}")  # 디버깅용
            raise e
        
    def sign_transaction(self, message):
        # 트랜잭션 서명 (이미 JSON 문자열로 변환된 메시지 받음)
        signature = CryptoHandler.sign_message(self.private_key, message)
        return signature 