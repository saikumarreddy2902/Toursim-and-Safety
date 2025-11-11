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

class AuthorityEncryption:
    """Handle high-security encryption for authority-level data protection"""
    
    def __init__(self, admin_key: Optional[str] = None) -> None:
        # Authority-level master key (would be provided by government authorities)
        if admin_key is None:
            admin_key = os.environ.get('AUTHORITY_MASTER_KEY', 'GOVT_TOURISM_AUTHORITY_MASTER_KEY_2025')
        
        # Store as bytes for KDF
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
            data_json = json.dumps(tourist_data)
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

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


class TouristEncryption:
    """Symmetric encryption for tourist data used in blockchain records."""

    def __init__(self, secret: Optional[str] = None) -> None:
        # Derive a stable Fernet key from a secret (env or default)
        base_secret = secret or os.environ.get('TOURIST_ENCRYPTION_SECRET', 'TOURIST_ENCRYPTION_DEFAULT_2025')
        salt = os.environ.get('TOURIST_ENCRYPTION_SALT', 'tourist_encryption_salt_2025').encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(base_secret.encode()))
        self.cipher_suite = Fernet(key)

    def encrypt_data(self, data: Union[Dict[str, Any], str, Any]) -> str:
        """Encrypt sensitive data."""
        if isinstance(data, dict):
            data = json.dumps(data)
        elif not isinstance(data, str):
            data = str(data)
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data; returns None on failure."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def encrypt_file_content(self, file_content: bytes) -> str:
        """Encrypt file content (binary data)."""
        encrypted_content = self.cipher_suite.encrypt(file_content)
        return base64.urlsafe_b64encode(encrypted_content).decode()

    def decrypt_file_content(self, encrypted_content: str) -> Optional[bytes]:
        """Decrypt file content; returns None on failure."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_content.encode())
            return self.cipher_suite.decrypt(encrypted_bytes)
        except Exception as e:
            print(f"File decryption error: {e}")
            return None

class SimpleBlockchain:
    """Simple blockchain implementation for tourist digital IDs"""
    
    def __init__(self) -> None:
        self.chain: List[Dict[str, Any]] = []
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block in the blockchain"""
        genesis_block: Dict[str, Any] = {
            'index': 0,
            'timestamp': time.time(),
            'data': 'Genesis Block - Tourist Safety Blockchain',
            'previous_hash': '0',
            'nonce': 0
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
    
    def calculate_hash(self, block: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of a block"""
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'data': block['data'],
            'previous_hash': block['previous_hash'],
            'nonce': block['nonce']
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def get_latest_block(self) -> Dict[str, Any]:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def mine_block(self, block: Dict[str, Any], difficulty: int = 2) -> Dict[str, Any]:
        """Simple proof-of-work mining (for demonstration)"""
        target = "0" * difficulty
        
        while block['hash'][:difficulty] != target:
            block['nonce'] += 1
            block['hash'] = self.calculate_hash(block)
        
        print(f"Block mined: {block['hash']}")
        return block
    
    def add_block(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new block to the blockchain"""
        previous_block: Dict[str, Any] = self.get_latest_block()
        
        new_block: Dict[str, Any] = {
            'index': previous_block['index'] + 1,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': previous_block['hash'],
            'nonce': 0
        }
        
        # Mine the block (find valid hash)
        new_block = self.mine_block(new_block)
        
        # Add to chain
        self.chain.append(new_block)
        return new_block
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if current block's hash is valid
            if current_block['hash'] != self.calculate_hash(current_block):
                return False
            
            # Check if current block points to previous block
            if current_block['previous_hash'] != previous_block['hash']:
                return False
        
        return True
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a block by its hash"""
        for block in self.chain:
            if block['hash'] == block_hash:
                return block
        return None
    
    def get_blocks_by_data_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Find blocks containing specific data pattern"""
        matching_blocks: List[Dict[str, Any]] = []
        for block in self.chain:
            if pattern in str(block['data']):
                matching_blocks.append(block)
        return matching_blocks

class TouristBlockchainID:
    """Manage tourist digital IDs on blockchain"""
    
    def __init__(self) -> None:
        self.blockchain = SimpleBlockchain()
        self.encryption = TouristEncryption()
    
    def create_digital_id(self, tourist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tamper-proof digital ID on blockchain"""
        
        # Separate sensitive and non-sensitive data
        sensitive_data: Dict[str, Any] = {
            'passport_number': tourist_data.get('passport_number'),
            'visa_number': tourist_data.get('visa_number'),
            'medical_info': {
                'blood_type': tourist_data.get('blood_type'),
                'allergies': tourist_data.get('allergies'),
                'medications': tourist_data.get('medications'),
                'medical_conditions': tourist_data.get('medical_conditions'),
                'emergency_instructions': tourist_data.get('emergency_instructions')
            },
            'emergency_contacts': {
                'primary': {
                    'name': tourist_data.get('emergency_name_1'),
                    'phone': tourist_data.get('emergency_phone_1'),
                    'email': tourist_data.get('emergency_email_1'),
                    'relationship': tourist_data.get('emergency_relationship_1')
                },
                'secondary': {
                    'name': tourist_data.get('emergency_name_2'),
                    'phone': tourist_data.get('emergency_phone_2'),
                    'email': tourist_data.get('emergency_email_2'),
                    'relationship': tourist_data.get('emergency_relationship_2')
                }
            }
        }
        
        # Non-sensitive data for blockchain
        public_data: Dict[str, Any] = {
            'tourist_id': tourist_data.get('tourist_id'),
            'full_name': tourist_data.get('full_name'),
            'nationality': tourist_data.get('nationality'),
            'registration_date': datetime.now().isoformat(),
            'registration_type': 'enhanced',
            'verification_status': 'pending'
        }
        
        # Encrypt sensitive data
        encrypted_sensitive: str = self.encryption.encrypt_data(sensitive_data)
        
        # Create blockchain record
        blockchain_data: Dict[str, Any] = {
            'type': 'tourist_digital_id',
            'tourist_id': tourist_data.get('tourist_id'),
            'public_data': public_data,
            'encrypted_data_hash': hashlib.sha256(encrypted_sensitive.encode()).hexdigest(),
            'created_timestamp': time.time(),
            'version': '1.0'
        }
        
        # Add to blockchain
        block: Dict[str, Any] = self.blockchain.add_block(blockchain_data)
        
        return {
            'blockchain_hash': block['hash'],
            'block_index': block['index'],
            'encrypted_data': encrypted_sensitive,
            'verification_hash': hashlib.sha256(
                f"{tourist_data.get('tourist_id')}{block['hash']}".encode()
            ).hexdigest()
        }
    
    def verify_digital_id(self, tourist_id: Any, blockchain_hash: str) -> Dict[str, Any]:
        """Verify a tourist's digital ID using blockchain"""
        
        # Find the block
        block = self.blockchain.get_block_by_hash(blockchain_hash)
        if not block:
            return {'valid': False, 'error': 'Block not found'}
        
        # Check if the block contains the tourist ID
        block_data = block.get('data', {})
        if block_data.get('tourist_id') != tourist_id:
            return {'valid': False, 'error': 'Tourist ID mismatch'}
        
        # Verify blockchain integrity
        if not self.blockchain.verify_chain():
            return {'valid': False, 'error': 'Blockchain integrity compromised'}
        
        return {
            'valid': True,
            'block_index': block['index'],
            'registration_date': block_data.get('created_timestamp'),
            'verification_status': block_data.get('public_data', {}).get('verification_status'),
            'tamper_proof': True
        }
    
    def get_tourist_data(self, tourist_id: Any, blockchain_hash: str, encrypted_data: str) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt tourist data"""
        
        # Verify the ID first
        verification = self.verify_digital_id(tourist_id, blockchain_hash)
        if not verification['valid']:
            return None
        
        # Decrypt sensitive data
        decrypted_data = self.encryption.decrypt_data(encrypted_data)
        if decrypted_data:
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return None
        
        return None
    
    def update_verification_status(self, tourist_id: Any, blockchain_hash: str, new_status: str) -> Optional[Dict[str, Any]]:
        """Update verification status (creates new block)"""
        
        # Verify current ID
        verification = self.verify_digital_id(tourist_id, blockchain_hash)
        if not verification['valid']:
            return None
        
        # Create update record
        update_data: Dict[str, Any] = {
            'type': 'status_update',
            'tourist_id': tourist_id,
            'original_block_hash': blockchain_hash,
            'new_verification_status': new_status,
            'updated_timestamp': time.time(),
            'updated_by': 'system'
        }
        
        # Add update block to blockchain
        block: Dict[str, Any] = self.blockchain.add_block(update_data)
        
        return {
            'update_hash': block['hash'],
            'block_index': block['index'],
            'new_status': new_status
        }

# Global blockchain instance
tourist_blockchain: TouristBlockchainID = TouristBlockchainID()

def encrypt_tourist_data(data: Union[Dict[str, Any], str, Any]) -> str:
    """Convenience function to encrypt tourist data"""
    encryption = TouristEncryption()
    return encryption.encrypt_data(data)

def decrypt_tourist_data(encrypted_data: str) -> Optional[str]:
    """Convenience function to decrypt tourist data"""
    encryption = TouristEncryption()
    return encryption.decrypt_data(encrypted_data)

def create_blockchain_id(tourist_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to create blockchain ID"""
    return tourist_blockchain.create_digital_id(tourist_data)

def verify_blockchain_id(tourist_id: Any, blockchain_hash: str) -> Dict[str, Any]:
    """Convenience function to verify blockchain ID"""
    return tourist_blockchain.verify_digital_id(tourist_id, blockchain_hash)