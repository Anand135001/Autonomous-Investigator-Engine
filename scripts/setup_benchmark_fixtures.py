import subprocess
from pathlib import Path

FIXTURE_RELATIVE_PATH = Path(
    "benchmark",
    "fixtures",
    "checkout-service",
)

ORDERS_RELATIVE_PATH = Path(
    "src",
    "checkout",
    "orders.py",
)


GOOD_VERSION = """\
def load_orders(cart_items, db):
    ids = [item.id for item in cart_items]

    return db.query_orders(ids)
"""


BAD_VERSION = """\
def load_orders(cart_items, db):
    orders = []

    for item in cart_items:
        orders.append(
            db.query_orders(item.id)
        )

    return orders
"""


def run_git(
    fixture_path: Path,
    *arguments: str,
) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture_path),
            *arguments,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> None:
    project_root = (
        Path(__file__).resolve().parents[1]
    )


    fixture_path = (
        project_root / FIXTURE_RELATIVE_PATH
    )

    orders_path = (
        fixture_path / ORDERS_RELATIVE_PATH
    )

    fixture_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    orders_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if (fixture_path / ".git").exists():
        print(
            "Benchmark fixture repository already exists."
        )
        return

    orders_path.write_text(
        GOOD_VERSION,
        encoding="utf-8",
    )

    run_git(
        fixture_path,
        "init",
    )

    run_git(
        fixture_path,
        "config",
        "user.name",
        "Benchmark Fixture",
    )

    run_git(
        fixture_path,
        "config",
        "user.email",
        "benchmark@example.com",
    )

    run_git(
        fixture_path,
        "add",
        ".",
    )

    run_git(
        fixture_path,
        "commit",
        "-m",
        "add efficient order loading",
    )

    orders_path.write_text(
        BAD_VERSION,
        encoding="utf-8",
    )

    run_git(
        fixture_path,
        "add",
        ".",
    )

    run_git(
        fixture_path,
        "commit",
        "-m",
        "introduce query regression",
    )

    print(
        "Benchmark fixture initialized:"
    )

    print(
        fixture_path
    )


if __name__ == "__main__":
    main()