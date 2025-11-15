# Firebase Integration Guide

This document explains how to integrate Firebase (Authentication & FCM) with the ETU Student Result Management System.

## Server-side (already implemented)

Files added:

- `Etu_student_result/firebase_service.py` - Initializes Firebase Admin SDK and exposes helpers: `verify_id_token`, `send_fcm_message`, `send_multicast`.
- Management command: `admin_hierarchy/management/commands/send_test_notification.py` - sends a test FCM message to a device token.
- Endpoint: `POST /firebase/verify-token/` - Verify a Firebase ID token and create/login a Django user.

Environment variables required:

- `FIREBASE_CREDENTIALS` - Full path to your Firebase service account JSON on the server.
- `ENABLE_FIREBASE_NOTIFICATIONS` - Set to `'true'` to allow sending notifications from server-side.

Security notes:

- Keep the service account JSON file safe (restrict file permissions, do not commit to git).
- Use environment variables in production (systemd unit, container secret, or hosting provider secrets).

## Client-side (web or mobile)

1. Obtain Firebase credentials for your app (web/mobile) from Firebase Console.
2. On client login, obtain the Firebase ID token (user.getIdToken()) and send it to the server:

POST /firebase/verify-token/
Body:
```json
{ "id_token": "<FIREBASE_ID_TOKEN>" }
```

The server will validate the token and return user information.

## Push Notifications (FCM)

- On the client, obtain an FCM device registration token. For web this is via `getToken()` from the Firebase Messaging SDK.
- Store that device token on your backend (associate with the user) and use `Etu_student_result/firebase_service.py` to send notifications.

Test sending notification (server):

```powershell
python manage.py send_test_notification <FCM_DEVICE_TOKEN> --title "Test" --body "Hello from ETU"
```

## Example (Web)

1. Initialize Firebase in web app using Firebase config.
2. After successful sign-in, get the ID token and device token:

```javascript
const idToken = await firebase.auth().currentUser.getIdToken();
const fcmToken = await messaging.getToken({ vapidKey: '<VAPID_KEY>' });

// send idToken to server for verification
fetch('/firebase/verify-token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id_token: idToken })
});

// send fcmToken to server to be stored for notifications
fetch('/api/save-device-token/', { ... })
```

## Next steps

- Add endpoint to store device tokens associated with users.
- Optionally implement topic subscriptions for groups of users.

