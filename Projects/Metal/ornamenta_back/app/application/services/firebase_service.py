import logging

import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self, credential_path: str):
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(credential_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
                raise

    def verify_token(self, token: str):
        try:
            return auth.verify_id_token(token)
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            return None

    def create_user(self, email, password):
        try:
            user = auth.create_user(email=email, password=password)
            return user.uid
        except Exception as e:
            logger.error(f"Failed to create user in Firebase: {e}")
            raise

    def set_custom_claims(self, uid: str, claims: dict):
        """
        Setea claims personalizados (como tenant_id) en el user de Firebase.
        """
        try:
            auth.set_custom_user_claims(uid, claims)
            logger.info(f"Custom claims set for user {uid}: {claims}")
        except Exception as e:
            logger.error(f"Failed to set custom claims for user {uid}: {e}")
            raise
