from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QMessageBox, QGroupBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from blockchain import Blockchain
from network import P2PNetwork
import sys
import time
import os
import json

class MiningThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, blockchain, miner_address):
        super().__init__()
        self.blockchain = blockchain
        self.miner_address = miner_address
        
    def run(self):
        self.blockchain.mine_pending_transactions(self.miner_address)
        self.finished.emit(self.miner_address)

class BlockchainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.blockchain = Blockchain()
        self.network = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('블록체인 네트워크')
        self.setGeometry(100, 100, 800, 600)
        
        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 네트워크 연결 그룹
        network_group = QGroupBox('네트워크 연결')
        network_layout = QHBoxLayout()
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText('포트')
        self.port_input.setText('5000')
        
        start_network_btn = QPushButton('네트워크 시작')
        start_network_btn.clicked.connect(self.start_network)
        
        network_layout.addWidget(QLabel('포트:'))
        network_layout.addWidget(self.port_input)
        network_layout.addWidget(start_network_btn)
        network_layout.addStretch()
        network_group.setLayout(network_layout)
        
        # 피어 연결 그룹
        peer_group = QGroupBox('피어 연결')
        peer_layout = QHBoxLayout()
        
        self.peer_host_input = QLineEdit()
        self.peer_host_input.setPlaceholderText('호스트')
        self.peer_host_input.setText('localhost')
        
        self.peer_port_input = QLineEdit()
        self.peer_port_input.setPlaceholderText('포트')
        
        connect_peer_btn = QPushButton('피어 연결')
        connect_peer_btn.clicked.connect(self.connect_to_peer)
        
        peer_layout.addWidget(QLabel('호스트:'))
        peer_layout.addWidget(self.peer_host_input)
        peer_layout.addWidget(QLabel('포트:'))
        peer_layout.addWidget(self.peer_port_input)
        peer_layout.addWidget(connect_peer_btn)
        peer_layout.addStretch()
        peer_group.setLayout(peer_layout)
        
        # 트랜잭션 그룹
        transaction_group = QGroupBox('트랜잭션 생성')
        transaction_layout = QHBoxLayout()
        
        self.sender_input = QLineEdit()
        self.sender_input.setPlaceholderText('보내는 사람')
        
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText('받는 사람')
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('금액')
        
        send_btn = QPushButton('전송')
        send_btn.clicked.connect(self.create_transaction)
        
        transaction_layout.addWidget(QLabel('보내는 사람:'))
        transaction_layout.addWidget(self.sender_input)
        transaction_layout.addWidget(QLabel('받는 사람:'))
        transaction_layout.addWidget(self.recipient_input)
        transaction_layout.addWidget(QLabel('금액:'))
        transaction_layout.addWidget(self.amount_input)
        transaction_layout.addWidget(send_btn)
        transaction_group.setLayout(transaction_layout)
        
        # 채굴 그룹
        mining_group = QGroupBox('채굴')
        mining_layout = QHBoxLayout()
        
        self.miner_input = QLineEdit()
        self.miner_input.setPlaceholderText('채굴자 주소')
        
        mine_btn = QPushButton('채굴 시작')
        mine_btn.clicked.connect(self.start_mining)
        
        mining_layout.addWidget(QLabel('채굴자 주소:'))
        mining_layout.addWidget(self.miner_input)
        mining_layout.addWidget(mine_btn)
        mining_layout.addStretch()
        mining_group.setLayout(mining_layout)
        
        # 잔액 조회 그룹
        balance_group = QGroupBox('잔액 조회')
        balance_layout = QHBoxLayout()
        
        self.balance_address_input = QLineEdit()
        self.balance_address_input.setPlaceholderText('주소')
        
        check_balance_btn = QPushButton('잔액 확인')
        check_balance_btn.clicked.connect(self.check_balance)
        
        self.balance_label = QLabel('잔액: 0')
        
        balance_layout.addWidget(QLabel('주소:'))
        balance_layout.addWidget(self.balance_address_input)
        balance_layout.addWidget(check_balance_btn)
        balance_layout.addWidget(self.balance_label)
        balance_layout.addStretch()
        balance_group.setLayout(balance_layout)
        
        # 로그 영역
        log_group = QGroupBox('로그')
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        # 월렛 그룹
        wallet_group = QGroupBox('월렛')
        wallet_layout = QVBoxLayout()
        
        # 월렛 생성/로드 버튼
        wallet_buttons_layout = QHBoxLayout()
        create_wallet_btn = QPushButton('새 월렛 생성')
        create_wallet_btn.clicked.connect(self.create_wallet)
        load_wallet_btn = QPushButton('월렛 불러오기')
        load_wallet_btn.clicked.connect(self.load_wallet)
        
        wallet_buttons_layout.addWidget(create_wallet_btn)
        wallet_buttons_layout.addWidget(load_wallet_btn)
        
        # 월렛 정보 표시
        self.wallet_info = QLabel('월렛이 로드되지 않음')
        
        wallet_layout.addLayout(wallet_buttons_layout)
        wallet_layout.addWidget(self.wallet_info)
        wallet_group.setLayout(wallet_layout)
        
        # 레이아웃에 위젯 추가
        layout.addWidget(network_group)
        layout.addWidget(peer_group)
        layout.addWidget(transaction_group)
        layout.addWidget(mining_group)
        layout.addWidget(balance_group)
        layout.addWidget(log_group)
        layout.insertWidget(1, wallet_group)
        
    def log(self, message):
        self.log_text.append(message)
        
    def start_network(self):
        try:
            port = int(self.port_input.text())
            self.network = P2PNetwork("localhost", port, self.blockchain)
            self.blockchain.network = self.network
            self.network.start()
            self.log(f"네트워크 시작됨 - 포트: {port}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"네트워크 시작 실패: {str(e)}")
            
    def connect_to_peer(self):
        try:
            host = self.peer_host_input.text()
            port = int(self.peer_port_input.text())
            if self.network:
                self.network.connect_to_peer(host, port)
                self.log(f"피어 연결됨 - {host}:{port}")
            else:
                QMessageBox.warning(self, "오류", "먼저 네트워크를 시작하세요")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"피어 연결 실패: {str(e)}")
            
    def create_transaction(self):
        try:
            if not hasattr(self, 'wallet'):
                QMessageBox.warning(self, "경고", "먼저 월렛을 로드하세요")
                return
            
            sender = self.wallet.address
            recipient = self.recipient_input.text()
            amount = float(self.amount_input.text())
            
            # 트랜잭션 데이터 생성 (timestamp 제외)
            transaction_data = {
                "from": sender,
                "to": recipient,
                "amount": amount
            }
            
            # 메시지 생성
            message = json.dumps(transaction_data, sort_keys=True)
            print(f"서명할 메시지: {message}")  # 디버깅용
            
            # 트랜잭션 서명
            signature = self.wallet.sign_transaction(message)
            print(f"생성된 서명: {signature}")  # 디버깅용
            
            # 트랜잭션 추가
            self.blockchain.add_transaction(
                sender, recipient, amount, 
                signature=signature, 
                public_key=self.wallet.public_key
            )
            
            self.log(f"트랜잭션 생성: {sender} -> {recipient}: {amount}")
            
            # 입력 필드 초기화
            self.recipient_input.clear()
            self.amount_input.clear()
        except Exception as e:
            print(f"트랜잭션 생성 오류: {str(e)}")  # 디버깅용
            QMessageBox.critical(self, "오류", f"트랜잭션 생성 실패: {str(e)}")
            
    def start_mining(self):
        try:
            miner = self.miner_input.text()
            self.mining_thread = MiningThread(self.blockchain, miner)
            self.mining_thread.finished.connect(self.mining_finished)
            self.mining_thread.start()
            self.log("채굴 시작...")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"채굴 실패: {str(e)}")
            
    def mining_finished(self, miner):
        self.log(f"채굴 완료: {miner}")
            
    def check_balance(self):
        try:
            address = self.balance_address_input.text()
            balance = self.blockchain.get_balance(address)
            self.balance_label.setText(f"잔액: {balance}")
            self.log(f"잔액 조회: {address} - {balance}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"잔액 조회 실패: {str(e)}")

    def create_wallet(self):
        try:
            import sys
            print("Python 경로:", sys.path)  # 디버깅용
            
            from wallet.wallet import Wallet
            self.wallet = Wallet()
            address = self.wallet.create_new_wallet()
            filename = self.wallet.save_wallet(None)
            self.wallet_info.setText(f'월렛 주소: {address}\n파일: {filename}')
            self.log(f"새 월렛 생성됨: {address}")
        except Exception as e:
            print(f"월렛 생성 오류 상세: {str(e)}")  # 디버깅용
            QMessageBox.critical(self, "오류", f"월렛 생성 실패: {str(e)}")

    def load_wallet(self):
        try:
            from wallet.wallet import Wallet
            filename, _ = QFileDialog.getOpenFileName(
                self, "월렛 파일 선택", "wallets", "JSON Files (*.json)")
            if filename:
                self.wallet = Wallet()
                self.wallet.load_wallet(os.path.basename(filename))
                self.wallet_info.setText(f'월렛 주소: {self.wallet.address}')
                self.log(f"월렛 로드됨: {self.wallet.address}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"월렛 로드 실패: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BlockchainGUI()
    window.show()
    sys.exit(app.exec()) 