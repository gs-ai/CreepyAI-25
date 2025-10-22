"""Email data extraction plugin."""

from __future__ import annotations

import email
import email.policy
import email.utils
from email.message import EmailMessage
import logging
import mailbox
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint
from app.plugins.geocoding_helper import GeocodingHelper

logger = logging.getLogger(__name__)


class EmailPlugin(BasePlugin):
    """Parse mail archives and extract basic geolocation hints."""

    def __init__(self) -> None:
        super().__init__(
            name="Email Analysis",
            description="Extract location references from email headers",
        )
        self.geocoder = GeocodingHelper()

    def get_configuration_options(self) -> List[dict]:
        return [
            {
                "name": "data_directory",
                "display_name": "Email directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": (
                    "Directory containing .mbox, Maildir folders or loose .eml files."
                ),
            },
            {
                "name": "target_email",
                "display_name": "Target email address",
                "type": "string",
                "default": "",
                "required": False,
                "description": "Only analyse messages sent to or from this address.",
            },
        ]

    def is_configured(self) -> tuple[bool, str]:
        directory = self.config.get("data_directory")
        if not directory:
            return False, "No email directory configured"
        if not Path(directory).expanduser().exists():
            return False, f"Email directory does not exist: {directory}"
        return True, "EmailPlugin is configured"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        configured, message = self.is_configured()
        if not configured:
            logger.warning("EmailPlugin not configured: %s", message)
            return []

        directory = Path(self.config["data_directory"]).expanduser()
        target_email = (self.config.get("target_email") or target or "").lower()

        points: List[LocationPoint] = []
        points.extend(self._process_maildir(directory, target_email, date_from, date_to))
        points.extend(self._process_mbox(directory, target_email, date_from, date_to))
        points.extend(self._process_eml(directory, target_email, date_from, date_to))
        return points

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _process_maildir(
        self,
        directory: Path,
        target_email: str,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        maildir = directory / "cur"
        if not maildir.exists():
            return []
        results: List[LocationPoint] = []
        try:
            mdir = mailbox.Maildir(str(directory), factory=None)
        except Exception as exc:  # pragma: no cover - fallback path
            logger.error("Failed to open maildir %s: %s", directory, exc)
            return results
        for _, message in mdir.iteritems():
            results.extend(
                self._extract_locations(message, target_email, date_from, date_to)
            )
        return results

    def _process_mbox(
        self,
        directory: Path,
        target_email: str,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        results: List[LocationPoint] = []
        for path in directory.glob("*.mbox"):
            try:
                mbox = mailbox.mbox(path)
            except Exception as exc:  # pragma: no cover - fallback path
                logger.error("Failed to open mbox %s: %s", path, exc)
                continue
            for message in mbox:
                results.extend(
                    self._extract_locations(message, target_email, date_from, date_to)
                )
        return results

    def _process_eml(
        self,
        directory: Path,
        target_email: str,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        results: List[LocationPoint] = []
        for path in directory.rglob("*.eml"):
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as handle:
                    message = email.message_from_file(handle, policy=email.policy.default)
            except Exception as exc:  # pragma: no cover - fallback path
                logger.error("Failed to parse %s: %s", path, exc)
                continue
            results.extend(
                self._extract_locations(message, target_email, date_from, date_to)
            )
        return results

    def _extract_locations(
        self,
        message: EmailMessage,
        target_email: str,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> List[LocationPoint]:
        sender = email.utils.parseaddr(message.get("From", ""))[1].lower()
        recipients = email.utils.getaddresses(message.get_all("To", []) + message.get_all("Cc", []))
        recipient_emails = {addr.lower() for _, addr in recipients}

        if target_email:
            if target_email != sender and target_email not in recipient_emails:
                return []

        message_date = self._parse_date(message.get("Date")) or datetime.utcnow()
        if date_from and message_date < date_from:
            return []
        if date_to and message_date > date_to:
            return []

        points: List[LocationPoint] = []

        for header in message.get_all("Received", []):
            ip = self._extract_ip(header)
            if not ip:
                continue
            location = self.geocoder.lookup_ip(ip)
            if not location:
                continue
            points.append(
                LocationPoint(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    timestamp=message_date,
                    source="Email Received header",
                    context=f"Hop via {ip}",
                )
            )

        if not points:
            detected = self._extract_location_from_body(message)
            if detected:
                geo = self.geocoder.geocode_text(detected)
                if geo:
                    points.append(
                        LocationPoint(
                            latitude=geo.latitude,
                            longitude=geo.longitude,
                            timestamp=message_date,
                            source="Email body",
                            context=detected,
                        )
                    )

        return points

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = email.utils.parsedate_to_datetime(value)
            if parsed and parsed.tzinfo:
                return parsed.astimezone(datetime.utcnow().tzinfo)  # type: ignore[arg-type]
            return parsed
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_ip(header: str) -> Optional[str]:
        import re

        match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", header)
        return match.group(1) if match else None

    @staticmethod
    def _extract_location_from_body(message: EmailMessage) -> Optional[str]:
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        return part.get_content().strip().splitlines()[0]
                    except Exception:  # pragma: no cover - defensive guard
                        continue
            return None
        try:
            return message.get_content().strip().splitlines()[0]
        except Exception:  # pragma: no cover - defensive guard
            return None


Plugin = EmailPlugin
