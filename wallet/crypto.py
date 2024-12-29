from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
import base64

class CryptoHandler:
    @staticmethod
    def generate_keypair():
        # RSA 키페어 생성
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # 직렬화
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def get_address_from_public_key(public_key):
        # 공개키로부터 주소 생성
        digest = hashes.Hash(hashes.SHA256())
        digest.update(public_key)
        hash_result = digest.finalize()
        return base64.b64encode(hash_result).decode('utf-8')[:40]
    
    @staticmethod
    def sign_message(private_key, message):
        # 메시지 서명
        private_key = serialization.load_pem_private_key(
            private_key,
            password=None
        )
        
        signature = private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(public_key, message, signature):
        try:
            print(f"검증 시도 - 메시지: {message}")  # 디버깅용
            public_key = serialization.load_pem_public_key(public_key)
            signature = base64.b64decode(signature)
            
            public_key.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"서명 검증 실패 상세: {str(e)}")  # 디버깅용
            return False 