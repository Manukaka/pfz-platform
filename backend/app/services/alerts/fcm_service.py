"""
Firebase Cloud Messaging (FCM) push notification service.
Sends PFZ alerts, safety warnings, and cyclone alerts to fishermen.

Uses firebase-admin SDK.
Setup: set FIREBASE_SERVICE_ACCOUNT_JSON env var (JSON string or file path).
"""
import json
import os
import structlog
from typing import Optional

logger = structlog.get_logger()

_app_initialized = False
_messaging = None


def _init_firebase():
    global _app_initialized, _messaging
    if _app_initialized:
        return _messaging is not None

    try:
        import firebase_admin
        from firebase_admin import credentials, messaging

        service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
        if not service_account:
            logger.warning("FIREBASE_SERVICE_ACCOUNT_JSON not set — FCM disabled")
            _app_initialized = True
            return False

        if service_account.startswith("{"):
            cred_dict = json.loads(service_account)
        else:
            cred_dict = json.loads(open(service_account).read())

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

        _messaging = messaging
        _app_initialized = True
        logger.info("Firebase initialized")
        return True

    except ImportError:
        logger.warning("firebase-admin not installed — FCM disabled")
        _app_initialized = True
        return False
    except Exception as e:
        logger.error("Firebase init failed", error=str(e))
        _app_initialized = True
        return False


class FcmService:

    def __init__(self):
        self._ready = _init_firebase()

    async def send_pfz_alert(
        self,
        fcm_token: str,
        zone_state: str,
        zone_confidence: float,
        top_species: str,
        language: str = "mr",
    ) -> bool:
        """Send new PFZ zone alert to a specific device."""
        titles = {
            "mr": "नवीन PFZ क्षेत्र!", "gu": "નવો PFZ ઝોન!", "hi": "नया PFZ क्षेत्र!",
            "kn": "ಹೊಸ PFZ ವಲಯ!", "ml": "പുതിയ PFZ മേഖല!", "en": "New PFZ Zone!",
        }
        bodies = {
            "mr": f"{zone_state.title()} जवळ उच्च आत्मविश्वास PFZ ({int(zone_confidence*100)}%). {top_species} अपेक्षित.",
            "gu": f"{zone_state.title()} પास ઉચ્ચ PFZ ({int(zone_confidence*100)}%). {top_species} અપેક્ષિત.",
            "hi": f"{zone_state.title()} के पास उच्च PFZ ({int(zone_confidence*100)}%). {top_species} संभावित.",
            "en": f"High-confidence PFZ near {zone_state.title()} ({int(zone_confidence*100)}%). {top_species} expected.",
        }
        return await self._send_notification(
            token=fcm_token,
            title=titles.get(language, titles["en"]),
            body=bodies.get(language, bodies["en"]),
            data={
                "type": "pfz_alert",
                "state": zone_state,
                "confidence": str(zone_confidence),
                "species": top_species,
            },
        )

    async def send_safety_alert(
        self,
        fcm_token: str,
        safety_color: str,
        wave_height: float,
        state: str,
        language: str = "mr",
    ) -> bool:
        """Send safety warning — only for red/black conditions."""
        if safety_color not in ("red", "black"):
            return False

        is_extreme = safety_color == "black"
        titles = {
            "mr": "⚠️ अत्यंत धोका!" if is_extreme else "⚠️ धोका!",
            "gu": "⚠️ ભારે ખતરો!" if is_extreme else "⚠️ ખતરો!",
            "hi": "⚠️ अत्यंत खतरा!" if is_extreme else "⚠️ खतरा!",
            "en": "⚠️ EXTREME DANGER!" if is_extreme else "⚠️ DANGER!",
        }
        bodies = {
            "mr": f"समुद्र अत्यंत उग्र. लाटा {wave_height:.1f}m. बाहेर जाऊ नका!",
            "gu": f"સમુદ્ર ખૂબ ઉગ્ર. મોજા {wave_height:.1f}m. બહાર ન જાઓ!",
            "hi": f"समुद्र बहुत खराब. लहरें {wave_height:.1f}m. बाहर मत जाओ!",
            "en": f"Extremely rough sea. Waves {wave_height:.1f}m. Do NOT venture out!",
        }
        return await self._send_notification(
            token=fcm_token,
            title=titles.get(language, titles["en"]),
            body=bodies.get(language, bodies["en"]),
            data={
                "type": "safety_alert",
                "severity": safety_color,
                "wave_height": str(wave_height),
                "state": state,
            },
            priority="high",
        )

    async def send_cyclone_alert(
        self,
        fcm_tokens: list[str],
        cyclone_name: str,
        distance_km: float,
        state: str,
    ) -> int:
        """Broadcast cyclone warning to multiple devices."""
        if not fcm_tokens:
            return 0
        sent = 0
        for token in fcm_tokens:
            success = await self._send_notification(
                token=token,
                title=f"🌀 Cyclone Alert: {cyclone_name}",
                body=f"{distance_km:.0f}km from {state.title()} coast. Follow IMD instructions.",
                data={"type": "cyclone", "name": cyclone_name, "distance_km": str(distance_km)},
                priority="high",
            )
            if success:
                sent += 1
        return sent

    async def send_silent_pfz_refresh(self, fcm_tokens: list[str], state: str) -> int:
        """Silent data push to trigger app background sync."""
        if not self._ready or not _messaging:
            return 0
        try:
            message = _messaging.MulticastMessage(
                data={"type": "pfz_refresh", "state": state},
                tokens=fcm_tokens[:500],  # FCM limit
                android=_messaging.AndroidConfig(priority="normal"),
                apns=_messaging.APNSConfig(
                    headers={"apns-push-type": "background", "apns-priority": "5"},
                ),
            )
            response = _messaging.send_each_for_multicast(message)
            logger.info("Silent PFZ refresh sent", state=state, success=response.success_count)
            return response.success_count
        except Exception as e:
            logger.error("Silent push failed", error=str(e))
            return 0

    async def _send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal",
    ) -> bool:
        if not self._ready or not _messaging:
            logger.debug("FCM disabled, skipping notification", title=title)
            return False
        try:
            message = _messaging.Message(
                notification=_messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                token=token,
                android=_messaging.AndroidConfig(
                    priority="high" if priority == "high" else "normal",
                ),
                apns=_messaging.APNSConfig(
                    payload=_messaging.APNSPayload(
                        aps=_messaging.Aps(sound="default"),
                    ),
                ),
            )
            _messaging.send(message)
            return True
        except Exception as e:
            logger.warning("FCM send failed", error=str(e), token=token[:20])
            return False


fcm_service = FcmService()
