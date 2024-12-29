from blockchain import Blockchain
from network import P2PNetwork
import time
import sys

def main():
    # 커맨드 라인 인자로 포트 번호 받기
    if len(sys.argv) != 2:
        print("Usage: python main.py <port>")
        return
    
    port = int(sys.argv[1])
    
    # 블록체인 및 P2P 네트워크 초기화
    blockchain = Blockchain()
    network = P2PNetwork("localhost", port, blockchain)
    blockchain.network = network
    
    # 네트워크 시작
    network.start()
    
    while True:
        print("\n1. 피어 연결")
        print("2. 트랜잭션 생성")
        print("3. 채굴하기")
        print("4. 잔액 확인")
        print("5. 종료")
        
        choice = input("선택: ")
        
        if choice == "1":
            peer_host = input("피어 호스트: ")
            peer_port = int(input("피어 포트: "))
            network.connect_to_peer(peer_host, peer_port)
            
        elif choice == "2":
            sender = input("보내는 사람: ")
            recipient = input("받는 사람: ")
            amount = float(input("금액: "))
            blockchain.add_transaction(sender, recipient, amount)
            
        elif choice == "3":
            miner_address = input("채굴자 주소: ")
            blockchain.mine_pending_transactions(miner_address)
            
        elif choice == "4":
            address = input("주소: ")
            balance = blockchain.get_balance(address)
            print(f"잔액: {balance}")
            
        elif choice == "5":
            network.close()
            break

if __name__ == "__main__":
    main() 