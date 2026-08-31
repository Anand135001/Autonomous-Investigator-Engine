from __future__ import annotations

import os


class FleetStateStore:
    """
    Investigation state store.

    Uses Firestore when USE_FIRESTORE=true.
    Falls back to process-local memory for local development.
    """

    _memory: dict[str, dict] = {}

    def __init__(
        self,
        client=None,
    ) -> None:

        self.client = None

        use_firestore = (
            os.getenv(
                "USE_FIRESTORE",
                "false",
            ).lower()
            == "true"
        )

        if client is not None:
            self.client = client

        elif use_firestore:
            from google.cloud import firestore

            self.client = firestore.Client(
                project=os.getenv(
                    "GOOGLE_CLOUD_PROJECT"
                )
            )

        if self.client is not None:
            self.collection = (
                self.client.collection(
                    "investigations"
                )
            )
        else:
            self.collection = None

    def save(
        self,
        investigation_id: str,
        data: dict,
    ) -> None:

        if self.client is not None:
            self.collection.document(
                investigation_id
            ).set(
                data,
                merge=True,
            )
            return

        current = self._memory.get(
            investigation_id,
            {},
        )

        current.update(data)

        self._memory[
            investigation_id
        ] = current

    def get(
        self,
        investigation_id: str,
    ) -> dict | None:

        if self.client is not None:
            snapshot = (
                self.collection
                .document(
                    investigation_id
                )
                .get()
            )

            if not snapshot.exists:
                return None

            return snapshot.to_dict()

        return self._memory.get(
            investigation_id
        )