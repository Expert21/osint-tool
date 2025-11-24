import os
from pathlib import Path
import logging
import json
import hmac
import hashlib
from typing import Optional, Dict

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("cryptography module not available - credential encryption disabled")

logger = logging.getLogger("OSINT_Tool")


class SecretsManager:
    """
    Secure credential management using encryption and environment variables.
    
    Priority order for credential retrieval:
    1. Environment variables (most secure for production)
    2. Encrypted local file (development/testing)
    """
    
    def __init__(self):
        self.secrets_dir = Path.home() / ".osint_secrets"
        self.secrets_dir.mkdir(mode=0o700, exist_ok=True)
        
        self.key_file = self.secrets_dir / ".key"
        self.creds_file = self.secrets_dir / "credentials.enc"

        self.hmac_salt = self._get_or_create_hmac_salt()
        self._cipher = None
    
    def _get_cipher(self):
        """Get or create Fernet cipher for encryption."""
        if not CRYPTO_AVAILABLE:
            logger.error("cryptography module not installed - cannot encrypt credentials")
            return None
        
        if self._cipher:
            return self._cipher
        
        # Get or create encryption key
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            self.key_file.touch(mode=0o600)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info(f"Created new encryption key at {self.key_file}")
        
        self._cipher = Fernet(key)
        return self._cipher
    
    # def _get_hmac_key(self):
    #     """Derive HMAC key from encryption key."""
    #     if not self.key_file.exists():
    #         return None
    #     with open(self.key_file, 'rb') as f:
    #         key = f.read()
    #     return hashlib.sha256(key).digest()
    def _get_or_create_hmac_salt(self) -> bytes:
        """Get existing HMAC salt or create new one."""
        import os

        salt_file = self.key_file.parent / '.hmac_salt'

        if salt_file.exists():
            with open(salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(32)
            with open(salt_file, 'wb') as f:
                f.write(salt)
            return salt

    def _get_hmac_key(self):
        """Derive HMAC key from encryption key using HKDF."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF

        if not self.key_file.exists():
            return None

        with open(self.key_file, 'rb') as f:
            master_key = f.read()

        # Derive separate keys for encryption and HMAC
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.hmac_salt,
            info=b'hmac-key'
        )
        return hkdf.derive(master_key)

    def _read_all_encrypted(self) -> Dict[str, str]:
        """Read all encrypted credentials with HMAC verification."""
        if not CRYPTO_AVAILABLE or not self.creds_file.exists():
            return {}
            
        try:
            cipher = self._get_cipher()
            if not cipher:
                return {}
            
            with open(self.creds_file, 'rb') as f:
                file_content = f.read()
            
            if not file_content:
                return {}

            # Try HMAC verification first
            hmac_verification_attempted = False
            hmac_verification_failed = False
            
            if len(file_content) >= 32:
                stored_hmac = file_content[:32]
                encrypted_data = file_content[32:]
                
                hmac_key = self._get_hmac_key()
                if hmac_key:
                    hmac_verification_attempted = True
                    calculated_hmac = hmac.new(hmac_key, encrypted_data, hashlib.sha256).digest()
                    if hmac.compare_digest(stored_hmac, calculated_hmac):
                        try:
                            decrypted = cipher.decrypt(encrypted_data)
                            data = json.loads(decrypted.decode())
                            if isinstance(data, dict):
                                return data
                        except Exception as decrypt_error:
                            logger.error(f"HMAC verification passed but decryption failed: {decrypt_error}")
                            hmac_verification_failed = True
                    else:
                        hmac_verification_failed = True
            
            # Fallback to legacy format (no HMAC)
            try:
                decrypted = cipher.decrypt(file_content)
                data = json.loads(decrypted.decode())
                if isinstance(data, dict):
                    logger.warning("Legacy credentials file format detected. Will migrate on next save.")
                    return data
            except Exception as legacy_error:
                # If HMAC verification was attempted but failed, provide detailed guidance
                if hmac_verification_failed:
                    logger.error("=" * 70)
                    logger.error("CRITICAL: Unable to decrypt credentials file!")
                    logger.error("=" * 70)
                    logger.error("HMAC verification failed. This may indicate:")
                    logger.error("  1. The encryption key has been modified or corrupted")
                    logger.error("  2. The credentials file has been tampered with")
                    logger.error("  3. A critical security file (.hmac_salt) was deleted")
                    logger.error("")
                    logger.error("Recovery options:")
                    logger.error("  • If you have a backup of your secrets directory, restore it:")
                    logger.error(f"    Backup location: {self.secrets_dir}")
                    logger.error("  • If this is a fresh setup, delete the corrupted files:")
                    logger.error(f"    rm {self.key_file}")
                    logger.error(f"    rm {self.creds_file}")
                    logger.error("    Then re-add your credentials using --store-credential")
                    logger.error("  • Check if .hmac_salt file exists in secrets directory")
                    logger.error("=" * 70)
                elif hmac_verification_attempted:
                    logger.error(f"Failed to decrypt credentials (legacy fallback also failed): {legacy_error}")
                # If no HMAC was attempted, just log the error normally
                pass
                
            logger.error("Credentials file integrity check failed or invalid format.")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to read credentials: {e}")
            return {}
    
    def get_credential(self, key_name: str) -> Optional[str]:
        """
        Retrieve credential with priority:
        1. Environment variable
        2. Encrypted file
        
        Args:
            key_name: Credential key name (e.g., 'google_api_key')
            
        Returns:
            Credential value or None if not found
        """
        # Priority 1: Environment variable
        env_var = key_name.upper().replace('-', '_')
        env_value = os.getenv(env_var)
        if env_value:
            logger.debug(f"Loaded credential '{key_name}' from environment variable")
            return env_value
        
        # Priority 2: Encrypted file
        value = self._read_encrypted(key_name)
        if value:
            logger.debug(f"Loaded credential '{key_name}' from encrypted file")
        return value
    
    def store_credential(self, key_name: str, value: str):
        """
        Store credential in encrypted file.
        
        Args:
            key_name: Credential key name
            value: Credential value to store
        """
        if not CRYPTO_AVAILABLE:
            logger.error("Cannot store credential - cryptography module not installed")
            logger.info("Please install: pip install cryptography")
            return
        
        self._write_encrypted(key_name, value)
        logger.info(f"✓ Credential '{key_name}' stored securely in {self.creds_file}")
    
    def _read_encrypted(self, key_name: str) -> Optional[str]:
        """Read from encrypted credentials file."""
        credentials = self._read_all_encrypted()
        return credentials.get(key_name)
    
    def _write_encrypted(self, key_name: str, value: str):
        """Write to encrypted credentials file with HMAC."""
        try:
            cipher = self._get_cipher()
            if not cipher:
                return
            
            # Read existing credentials
            credentials = self._read_all_encrypted()
            
            # Update credentials
            credentials[key_name] = value
            
            # Encrypt
            plaintext = json.dumps(credentials).encode()
            encrypted_data = cipher.encrypt(plaintext)
            
            # Calculate HMAC
            hmac_key = self._get_hmac_key()
            if not hmac_key:
                logger.error("Could not get HMAC key")
                return
                
            calculated_hmac = hmac.new(hmac_key, encrypted_data, hashlib.sha256).digest()
            
            # Write HMAC + EncryptedData
            self.creds_file.touch(mode=0o600)
            with open(self.creds_file, 'wb') as f:
                f.write(calculated_hmac + encrypted_data)
                
        except Exception as e:
            logger.error(f"Failed to write credential '{key_name}': {e}")
    
    def list_stored_credentials(self) -> list:
        """
        List all stored credential keys (not values).
        
        Returns:
            List of credential key names
        """
        if not CRYPTO_AVAILABLE or not self.creds_file.exists():
            return []
        
        try:
            cipher = self._get_cipher()
            if not cipher:
                return []
            
            with open(self.creds_file, 'rb') as f:
                encrypted = f.read()
            
            if not encrypted:
                return []
            
            decrypted = cipher.decrypt(encrypted)
            credentials = json.loads(decrypted.decode())
            
            return list(credentials.keys())
            
        except Exception as e:
            logger.error(f"Failed to list credentials: {e}")
            return []
