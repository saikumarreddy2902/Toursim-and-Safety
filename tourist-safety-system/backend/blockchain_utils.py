"""
Enhanced Blockchain simulation and data encryption utilities
for Tourist Safety System with Authority-Level Security
"""

import hashlib
import json
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
import base64
import os
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class AuthorityEncryption:
    """Handle high-security encryption for authority-level data protection"""
    
    def __init__(self, admin_key: Optional[str] = None) -> None:
        # Authority-level master key (would be provided by government authorities)
        if admin_key is None:
            admin_key = os.environ.get('AUTHORITY_MASTER_KEY', 'GOVT_TOURISM_AUTHORITY_MASTER_KEY_2025')
        
        self.admin_key: bytes = admin_key.encode()
        self.salt: bytes = os.environ.get('AUTHORITY_SALT', 'govt_tourism_authority_salt_2025').encode()
        
        # Generate strong encryption key for authority access
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=200000,  # Higher iterations for authority-level security
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.admin_key))
        self.authority_cipher = Fernet(key)
        
        # Generate RSA key pair for additional security layer
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
    
    def encrypt_tourist_data(self, tourist_data: Union[Dict[str, Any], str, Any]) -> str:
        """Encrypt tourist data with authority-level security"""
        if isinstance(tourist_data, dict):
            # Add security metadata
            tourist_data['encrypted_timestamp'] = datetime.now().isoformat()
            tourist_data['security_level'] = 'AUTHORITY_ENCRYPTED'
            data_json = json.dumps(tourist_data, default=str)
        else:
            data_json = str(tourist_data)
        
        # First layer: Fernet encryption
        encrypted_data = self.authority_cipher.encrypt(data_json.encode())
        
        # Second layer: Base64 encoding for blockchain storage
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_tourist_data(self, encrypted_data: str, admin_verified: bool = False) -> Union[Dict[str, Any], str]:
        """Decrypt tourist data - only for verified admins"""
        if not admin_verified:
            raise PermissionError("Access denied: Admin verification required")
        
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt with authority cipher
            decrypted_data = self.authority_cipher.decrypt(encrypted_bytes)
            
            # Parse JSON if possible
            try:
                return json.loads(decrypted_data.decode())
            except json.JSONDecodeError:
                return decrypted_data.decode()
                
        except Exception as e:
            raise SecurityError(f"Decryption failed: {str(e)}")
    
    def generate_admin_token(self, admin_id: str, permissions: Union[List[str], Dict[str, Any]]) -> str:
        """Generate secure admin access token"""
        token_data: Dict[str, Any] = {
            'admin_id': admin_id,
            'permissions': permissions,
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now().timestamp() + 3600 * 8),  # 8 hours
            'token_id': secrets.token_hex(16)
        }
        
        return self.encrypt_tourist_data(token_data)
    
    def verify_admin_token(self, token: str) -> Tuple[bool, Union[str, Dict[str, Any]]]:
        """Verify admin access token"""
        try:
            token_data = self.decrypt_tourist_data(token, admin_verified=True)
            
            # Check expiration
            if not isinstance(token_data, dict):
                return False, "Invalid token payload"
            if datetime.now().timestamp() > token_data.get('expires_at', 0):
                return False, "Token expired"
            
            return True, token_data
        except:
            return False, "Invalid token"

class TouristEncryption:
    """Handle encryption and decryption of sensitive tourist data (legacy compatibility)"""
    
    def __init__(self, password: Optional[str] = None) -> None:
        if password is None:
            password = os.environ.get('TOURIST_ENCRYPTION_KEY', 'default_tourist_safety_key_2025')
        
        self.password: bytes = password.encode()
        self.salt: bytes = b'tourist_safety_salt_2025'  # In production, use random salt per user
        
        # Derive encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self.cipher_suite = Fernet(key)
    
    def encrypt_data(self, data: Union[Dict[str, Any], str, Any]) -> str:
        """Encrypt sensitive data"""
        if isinstance(data, dict):
            data = json.dumps(data, default=str)
        elif not isinstance(data, str):
            data = str(data)
        
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Optional[Union[Dict[str, Any], str]]:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted_data.decode())
            except json.JSONDecodeError:
                return decrypted_data.decode()
                
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

class Block:
    """Enhanced blockchain block with authority-level security"""
    
    def __init__(self, index: int, timestamp: float, data: str, previous_hash: str) -> None:
        self.index: int = index
        self.timestamp: float = timestamp
        self.data: str = data  # This will be encrypted tourist data
        self.previous_hash: str = previous_hash
        self.nonce: int = 0
        self.hash: str = self.calculate_hash()
        
        # Authority metadata
        self.authority_signature: Optional[str] = None
        self.access_level: str = 'AUTHORITY_ONLY'
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """Mine block with proof of work"""
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"Block mined: {self.hash}")

class SecureBlockchain:
    """Enhanced blockchain for tourist safety with authority-level access control"""
    
    def __init__(self) -> None:
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty: int = 4
        self.pending_transactions: List[Dict[str, Any]] = []
        self.mining_reward: int = 10
        
        # Authority encryption instance
        self.authority_encryption = AuthorityEncryption()
        self.legacy_encryption = TouristEncryption()
        
        # Admin access tracking
        self.active_admin_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Authority-provided admin credentials (in production, this would be a secure database)
        self.authority_admins: Dict[str, Dict[str, Any]] = {
            'TOURISM_AUTHORITY_ADMIN_001': {
                'password_hash': hashlib.sha256('TourismAuth2025!@#'.encode()).hexdigest(),
                'permissions': ['VIEW_ALL_TOURISTS', 'DECRYPT_DATA', 'GENERATE_REPORTS'],
                'authority_level': 'NATIONAL_TOURISM_BOARD',
                'created_by': 'MINISTRY_OF_TOURISM',
                'active': True
            },
            'STATE_TOURISM_ADMIN_001': {
                'password_hash': hashlib.sha256('StateTourism2025!@#'.encode()).hexdigest(),
                'permissions': ['VIEW_STATE_TOURISTS', 'DECRYPT_DATA'],
                'authority_level': 'STATE_TOURISM_BOARD',
                'created_by': 'STATE_TOURISM_DEPARTMENT',
                'active': True
            }
        }
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain"""
        genesis_data: Dict[str, Any] = {
            'message': 'Tourist Safety Blockchain Genesis Block',
            'authority': 'MINISTRY_OF_TOURISM_INDIA',
            'created': datetime.now().isoformat(),
            'security_level': 'AUTHORITY_ENCRYPTED'
        }
        
        authority_encryption = AuthorityEncryption()
        encrypted_genesis: str = authority_encryption.encrypt_tourist_data(genesis_data)
        
        return Block(0, time.time(), encrypted_genesis, "0")
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def add_encrypted_tourist_data(self, tourist_data: Dict[str, Any], admin_verified: bool = False) -> int:
        """Add tourist data to blockchain with authority-level encryption"""
        if not admin_verified:
            # For regular tourist registration, encrypt with authority key
            encrypted_data: str = self.authority_encryption.encrypt_tourist_data(tourist_data)
        else:
            # If admin is adding data, use enhanced encryption
            tourist_data['admin_added'] = True
            tourist_data['admin_timestamp'] = datetime.now().isoformat()
            encrypted_data = self.authority_encryption.encrypt_tourist_data(tourist_data)
        
        # Create new block
        new_block = Block(
            len(self.chain),
            time.time(),
            encrypted_data,
            self.get_latest_block().hash
        )
        
        # Mine the block
        new_block.mine_block(self.difficulty)
        
        # Add to chain
        self.chain.append(new_block)
        
        return new_block.index
    
    def authenticate_authority_admin(self, admin_id: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticate admin with authority-provided credentials"""
        if admin_id not in self.authority_admins:
            return False, "Invalid admin credentials", None
        
        admin_info = self.authority_admins[admin_id]
        
        if not admin_info['active']:
            return False, "Admin account deactivated", None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != admin_info['password_hash']:
            return False, "Invalid password", None
        
        # Generate admin token
        token = self.authority_encryption.generate_admin_token(admin_id, admin_info['permissions'])
        
        # Store active session
        self.active_admin_sessions[admin_id] = {
            'token': token,
            'login_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'permissions': admin_info['permissions']
        }
        
        return True, "Authentication successful", {
            'token': token,
            'permissions': admin_info['permissions'],
            'authority_level': admin_info['authority_level']
        }
    
    def verify_admin_access(self, admin_token: str) -> Tuple[bool, Union[str, Dict[str, Any]]]:
        """Verify admin token and permissions"""
        is_valid, token_data = self.authority_encryption.verify_admin_token(admin_token)
        
        if not is_valid:
            return False, "Invalid or expired token"
        
        if isinstance(token_data, dict):
            admin_id = token_data.get('admin_id')
        else:
            return False, "Invalid token payload"

        if admin_id in self.active_admin_sessions:
            # Update last activity
            self.active_admin_sessions[admin_id]['last_activity'] = datetime.now().isoformat()
            return True, token_data
        
        return False, "Session not found"
    
    def get_all_tourist_data_for_admin(self, admin_token: str) -> List[Dict[str, Any]]:
        """Get all decrypted tourist data - only for verified admins"""
        is_valid, _ = self.verify_admin_access(admin_token)
        
        if not is_valid:
            raise PermissionError("Access denied: Invalid admin token")
        
        decrypted_tourists: List[Dict[str, Any]] = []
        
        for block in self.chain[1:]:  # Skip genesis block
            try:
                # Decrypt block data with admin verification
                decrypted_data = self.authority_encryption.decrypt_tourist_data(
                    block.data, 
                    admin_verified=True
                )
                
                if isinstance(decrypted_data, dict) and 'security_level' not in decrypted_data:
                    # This is tourist data
                    decrypted_data['block_index'] = block.index
                    decrypted_data['block_timestamp'] = block.timestamp
                    decrypted_data['block_hash'] = block.hash
                    decrypted_tourists.append(decrypted_data)
                    
            except Exception as e:
                print(f"Error decrypting block {block.index}: {e}")
                continue
        
        return decrypted_tourists
    
    def get_tourist_by_id_for_admin(self, tourist_id: Any, admin_token: str) -> Optional[Dict[str, Any]]:
        """Get specific tourist data - only for verified admins"""
        is_valid, _ = self.verify_admin_access(admin_token)
        
        if not is_valid:
            raise PermissionError("Access denied: Invalid admin token")
        
        all_tourists = self.get_all_tourist_data_for_admin(admin_token)
        
        for tourist in all_tourists:
            if tourist.get('tourist_id') == tourist_id:
                return tourist
        
        return None
    
    def is_chain_valid(self) -> bool:
        """Validate the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True

# Global blockchain instance with authority-level security
secure_blockchain: SecureBlockchain = SecureBlockchain()

# Legacy compatibility functions
def encrypt_tourist_data(data: Union[Dict[str, Any], str, Any]) -> str:
    """Legacy function for compatibility"""
    return secure_blockchain.authority_encryption.encrypt_tourist_data(data)

def decrypt_tourist_data(encrypted_data: str, admin_verified: bool = False) -> Union[Dict[str, Any], str]:
    """Legacy function for compatibility"""
    return secure_blockchain.authority_encryption.decrypt_tourist_data(encrypted_data, admin_verified)