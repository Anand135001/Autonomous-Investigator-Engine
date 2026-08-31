from investigator.fleet.firestore_state import (
    FleetStateStore,
)


class FakeDocument:
    def __init__(self):
        self.data = None

    def set(
        self,
        data,
        merge=False,
    ):
        self.data = data

    def get(self):
        return FakeSnapshot(
            self.data
        )


class FakeSnapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class FakeCollection:
    def __init__(self):
        self.documents = {}

    def document(
        self,
        document_id,
    ):
        if document_id not in self.documents:
            self.documents[
                document_id
            ] = FakeDocument()

        return self.documents[
            document_id
        ]


class FakeClient:
    def __init__(self):
        self.collection_ref = (
            FakeCollection()
        )

    def collection(
        self,
        name,
    ):
        return self.collection_ref


def test_save_and_get() -> None:

    client = FakeClient()

    store = FleetStateStore(
        client=client
    )

    store.save(
        "INV-1",
        {
            "status": "running",
            "agent": "fleet_commander",
        },
    )

    result = store.get(
        "INV-1"
    )

    assert result == {
        "status": "running",
        "agent": "fleet_commander",
    }