import socket
import threading
import json
import time
from typing import List, Dict
from blockchain import Blockchain, Block

class P2PNetwork:
    def __init__(self, host: str, port: int, blockchain: Blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers: List[Dict] = []  # 연결된 피어들의 목록
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 소켓 재사용 옵션 추가
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        # 서버 시작
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"P2P 네트워크 시작됨 - {self.host}:{self.port}")
        
        # 연결 수신 대기 스레드 시작
        threading.Thread(target=self.listen_for_connections).start()

    def listen_for_connections(self):
        while True:
            client, address = self.server_socket.accept()
            print(f"새로운 피어 연결됨: {address}")
            self.peers.append({"socket": client, "address": address})
            
            # 각 피어에 대한 메시지 수신 스레드 시작
            threading.Thread(target=self.handle_peer, args=(client, address)).start()

    def connect_to_peer(self, host: str, port: int):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((host, port))
            self.peers.append({"socket": peer_socket, "address": (host, port)})
            print(f"피어에 연결됨: {host}:{port}")
            
            # 연결된 피어의 메시지 수신 스레드 시작
            threading.Thread(target=self.handle_peer, args=(peer_socket, (host, port))).start()
            
            # 새로 연결된 피어와 블록체인 동기화
            self.sync_blockchain(peer_socket)
            
        except Exception as e:
            print(f"피어 연결 실패: {e}")

    def handle_peer(self, peer_socket: socket.socket, address):
        while True:
            try:
                message = peer_socket.recv(4096).decode()
                if not message:
                    break
                
                self.process_message(message, peer_socket)
                
            except Exception as e:
                print(f"피어 {address} 처리 중 오류: {e}")
                break
        
        self.remove_peer(peer_socket)

    def process_message(self, message: str, sender_socket: socket.socket):
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "CHAIN_RESPONSE":
                # 블록체인 응답 수신
                chain_data = data.get("data")
                print(f"체인 데이터 수신: 길이 {len(chain_data['chain'])}")
                
                # 받은 체인이 현재 체인보다 길거나 같으면 업데이트
                if len(chain_data["chain"]) >= len(self.blockchain.chain):
                    print("새로운 체인 발견, 업데이트 중...")
                    new_chain = []
                    for block_data in chain_data["chain"]:
                        block = Block(
                            block_data["index"],
                            block_data["transactions"],
                            block_data["timestamp"],
                            block_data["previous_hash"]
                        )
                        block.nonce = block_data["nonce"]
                        block.hash = block_data["hash"]
                        new_chain.append(block)
                    
                    # 새 체인이 유효한지 확인
                    is_valid = True
                    for i in range(1, len(new_chain)):
                        if not self.blockchain.is_valid_new_block(new_chain[i], new_chain[i-1]):
                            is_valid = False
                            print(f"블록 {i}가 유효하지 않음")
                            break
                    
                    if is_valid:
                        print(f"유효한 체인 발견. 현재 길이: {len(self.blockchain.chain)}, 새 체인 길이: {len(new_chain)}")
                        self.blockchain.chain = new_chain
                        self.blockchain.pending_transactions = chain_data["pending_transactions"]
                        print("체인 업데이트 완료")
                    else:
                        print("받은 체인이 유효하지 않음")
            
            # 나머지 message_type 처리는 그대로 유지
            elif message_type == "NEW_BLOCK":
                block_data = data.get("data")
                if self.blockchain.add_block_from_network(block_data):
                    print(f"새 블록 추가됨: {block_data['index']}")  # 디버깅용
                    self.broadcast_message(message, sender_socket)
                
            elif message_type == "NEW_TRANSACTION":
                transaction = data.get("data")
                self.blockchain.add_transaction_from_network(transaction)
                print(f"새 트랜잭션 추가됨: {transaction}")  # 디버깅용
                self.broadcast_message(message, sender_socket)
                
            elif message_type == "REQUEST_CHAIN":
                chain_data = self.blockchain.to_dict()
                response = {
                    "type": "CHAIN_RESPONSE",
                    "data": chain_data
                }
                sender_socket.send(json.dumps(response).encode())
                print("체인 데이터 전송됨")  # 디버깅용
                
        except Exception as e:
            print(f"메시지 처리 중 오류: {e}")

    def broadcast_message(self, message: str, exclude_socket=None):
        for peer in self.peers:
            if peer["socket"] != exclude_socket:
                try:
                    peer["socket"].send(message.encode())
                except Exception as e:
                    print(f"메시지 브로드캐스트 중 오류: {e}")

    def sync_blockchain(self, peer_socket: socket.socket):
        try:
            # 블록체인 데이터 요청
            request = {
                "type": "REQUEST_CHAIN",
                "data": None
            }
            print("체인 동기화 요청 전송")  # 디버깅 추가
            peer_socket.send(json.dumps(request).encode())
        except Exception as e:
            print(f"체인 동기화 중 오류: {e}")

    def remove_peer(self, peer_socket: socket.socket):
        self.peers = [peer for peer in self.peers if peer["socket"] != peer_socket]
        try:
            peer_socket.close()
        except:
            pass

    def close(self):
        for peer in self.peers:
            try:
                peer["socket"].close()
            except:
                pass
        self.server_socket.close() 