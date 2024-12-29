import hashlib
import time
import json
from typing import List, Dict
from wallet.crypto import CryptoHandler

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: float, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # 채굴 난이도
        self.pending_transactions = []
        self.mining_reward = 10  # 채굴 보상
        self.network = None  # P2P 네트워크 참조를 위한 속성 추가

    def create_genesis_block(self) -> Block:
        return Block(0, [], time.time(), "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address: str):
        # 채굴 보상 트랜잭션 추가
        self.pending_transactions.append({
            "from": "network",
            "to": miner_address,
            "amount": self.mining_reward
        })

        # 새 블록 생성
        block = Block(
            len(self.chain),
            self.pending_transactions,
            time.time(),
            self.get_latest_block().hash
        )
        
        # 작업증명(PoW) 수행
        self.proof_of_work(block)

        # 블록체인에 추가
        self.chain.append(block)
        
        # 새 블록을 네트워크에 브로드캐스트
        if self.network:
            message = {
                "type": "NEW_BLOCK",
                "data": {
                    "index": block.index,
                    "transactions": block.transactions,
                    "timestamp": block.timestamp,
                    "previous_hash": block.previous_hash,
                    "nonce": block.nonce,
                    "hash": block.hash
                }
            }
            print(f"새 블록 브로드캐스트: 인덱스 {block.index}")  # 디버깅 추가
            self.network.broadcast_message(json.dumps(message))
        
        # 보류 중인 트랜잭션 초기화
        self.pending_transactions = []

    def proof_of_work(self, block: Block):
        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.calculate_hash()

    def add_transaction(self, sender: str, recipient: str, amount: float, signature=None, public_key=None):
        # network에서 오는 채굴 보상 트랜잭션은 검증 제외
        if sender == "network":
            transaction = {
                "from": sender,
                "to": recipient,
                "amount": amount,
                "timestamp": time.time()
            }
            self.pending_transactions.append(transaction)
            return

        # 트랜잭션 데이터 생성 (timestamp 제외)
        transaction = {
            "from": sender,
            "to": recipient,
            "amount": amount
        }
        
        # 서명 검증
        try:
            message = json.dumps(transaction, sort_keys=True)
            print(f"검증 중인 메시지: {message}")  # 디버깅용
            print(f"서명: {signature}")  # 디버깅용
            print(f"공개키: {public_key}")  # 디버깅용
            
            if not CryptoHandler.verify_signature(public_key, message, signature):
                print("서명 검증 실패")  # 디버깅용
                raise Exception("Invalid transaction signature")
            print("서명 검증 성공")  # 디버깅용
            
            # 검증 성공 후 timestamp 추가
            transaction["timestamp"] = time.time()
            self.pending_transactions.append(transaction)
            
            # 새 트랜잭션을 네트워크에 브로드캐스트
            if self.network:
                message = {
                    "type": "NEW_TRANSACTION",
                    "data": transaction
                }
                self.network.broadcast_message(json.dumps(message))
                
        except Exception as e:
            print(f"서명 검증 실패: {str(e)}")
            raise Exception("Invalid transaction signature")

    def verify_transaction(self, transaction, signature, public_key):
        if not signature or not public_key:
            return False
        
        message = json.dumps(transaction, sort_keys=True)
        return CryptoHandler.verify_signature(public_key, message, signature)

    def get_balance(self, address: str) -> float:
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction["from"] == address:
                    balance -= transaction["amount"]
                if transaction["to"] == address:
                    balance += transaction["amount"]
        return balance

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 현재 블록의 해시 검증
            if current_block.hash != current_block.calculate_hash():
                return False

            # 이전 블록 해시 링크 검증
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def add_block_from_network(self, block_data: Dict):
        """네트워크에서 받은 블록을 추가"""
        block = Block(
            block_data["index"],
            block_data["transactions"],
            block_data["timestamp"],
            block_data["previous_hash"]
        )
        block.nonce = block_data["nonce"]
        block.hash = block_data["hash"]
        
        if self.is_valid_new_block(block, self.get_latest_block()):
            self.chain.append(block)
            return True
        return False

    def add_transaction_from_network(self, transaction: Dict):
        """네트워크에서 받은 트랜잭션을 추가"""
        self.pending_transactions.append(transaction)

    def to_dict(self) -> Dict:
        """블록체인을 딕셔너리로 변환"""
        return {
            "chain": [{
                "index": block.index,
                "transactions": block.transactions,
                "timestamp": block.timestamp,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "hash": block.hash
            } for block in self.chain],
            "pending_transactions": self.pending_transactions
        }

    def is_valid_new_block(self, new_block: Block, previous_block: Block) -> bool:
        """새로운 블록의 유효성 검증"""
        if previous_block.index + 1 != new_block.index:
            return False
        if previous_block.hash != new_block.previous_hash:
            return False
        if new_block.calculate_hash() != new_block.hash:
            return False
        return True

# 사용 예시
if __name__ == "__main__":
    # 블록체인 생성
    my_blockchain = Blockchain()

    # 트랜잭션 추가
    my_blockchain.add_transaction("Alice", "Bob", 50)
    my_blockchain.add_transaction("Bob", "Charlie", 30)

    # 블록 채굴
    my_blockchain.mine_pending_transactions("miner_address")

    # 잔액 확인
    print(f"Miner's balance: {my_blockchain.get_balance('miner_address')}")
    print(f"Alice's balance: {my_blockchain.get_balance('Alice')}")
    print(f"Bob's balance: {my_blockchain.get_balance('Bob')}")
    print(f"Charlie's balance: {my_blockchain.get_balance('Charlie')}")

    # 블록체인 유효성 검증
    print(f"Blockchain valid: {my_blockchain.is_chain_valid()}")
