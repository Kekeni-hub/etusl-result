import os
import threading
from typing import Optional, Dict, Any

try:
    import firebase_admin  # type: ignore
    from firebase_admin import credentials, auth, messaging  # type: ignore
    _FIREBASE_AVAILABLE = True
except Exception:
    # Allow test runs without firebase-admin installed; functions will raise at runtime
    firebase_admin = None
    credentials = None
    auth = None
    messaging = None
    _FIREBASE_AVAILABLE = False


FIREBASE_APP_LOCK = threading.Lock()
FIREBASE_APP = None


def init_firebase(cred_path: Optional[str] = None):
    """Initialize Firebase Admin SDK with provided service account JSON path.

    If already initialized, returns existing app.
    """
    global FIREBASE_APP
    with FIREBASE_APP_LOCK:
        if FIREBASE_APP is not None:
            return FIREBASE_APP

        if cred_path is None:
            cred_path = os.environ.get('FIREBASE_CREDENTIALS')

        if not cred_path:
            raise RuntimeError('Firebase credentials path not provided. Set FIREBASE_CREDENTIALS env var or pass cred_path.')
        if not _FIREBASE_AVAILABLE:
            raise RuntimeError('firebase-admin package is not installed in this environment.')

        cred = credentials.Certificate(cred_path)
        FIREBASE_APP = firebase_admin.initialize_app(cred)
        return FIREBASE_APP


def verify_id_token(id_token: str) -> Dict[str, Any]:
    """Verify Firebase ID token and return decoded token payload.

    Raises firebase_admin.auth.InvalidIdTokenError or other exceptions on failure.
    """
    # In tests the verify function may be mocked; if not, ensure firebase is available
    if not _FIREBASE_AVAILABLE:
        raise RuntimeError('firebase-admin not available; cannot verify token in this environment')
    init_firebase()
    decoded = auth.verify_id_token(id_token)
    return decoded


def send_fcm_message(token: str, title: str, body: str, data: Optional[Dict[str, str]] = None):
    """Send a push notification via Firebase Cloud Messaging to a device token.

    Returns the send response object.
    """
    if not _FIREBASE_AVAILABLE:
        raise RuntimeError('firebase-admin not available; cannot send message in this environment')
    init_firebase()
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
    )
    response = messaging.send(message)
    return response


def send_multicast(tokens: list, title: str, body: str, data: Optional[Dict[str, str]] = None):
    if not _FIREBASE_AVAILABLE:
        raise RuntimeError('firebase-admin not available; cannot send multicast in this environment')
    init_firebase()
    message = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
    )
    response = messaging.send_multicast(message)
    return response
