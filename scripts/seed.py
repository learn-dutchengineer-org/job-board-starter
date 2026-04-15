"""Seed the job board database with sample data.

Run after the migration:
    psql $DATABASE_URL -f migrations/001_create_tables.sql
    python scripts/seed.py
"""

import os

import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://jobboard:jobboard@localhost:5432/jobboard"
)

COMPANIES = [
    {
        "name": "Acme Corp",
        "website": "https://acme.example.com",
        "description": "A software company building developer tools.",
    },
    {
        "name": "Globex Systems",
        "website": "https://globex.example.com",
        "description": "Enterprise data infrastructure and analytics.",
    },
    {
        "name": "Initech Solutions",
        "website": "https://initech.example.com",
        "description": "Cloud-native platform for financial services.",
    },
]

LISTINGS = [
    {
        "company": "Acme Corp",
        "title": "Senior Python Engineer",
        "description": "Build and maintain our core data pipeline infrastructure.",
        "location": "Remote",
        "salary_min": 130000,
        "salary_max": 160000,
        "employment_type": "full-time",
    },
    {
        "company": "Acme Corp",
        "title": "ML Engineer",
        "description": "Design and deploy machine learning models at scale.",
        "location": "San Francisco, CA",
        "salary_min": 150000,
        "salary_max": 190000,
        "employment_type": "full-time",
    },
    {
        "company": "Globex Systems",
        "title": "Data Engineer",
        "description": "Build ETL pipelines and maintain our data warehouse.",
        "location": "New York, NY",
        "salary_min": 120000,
        "salary_max": 150000,
        "employment_type": "full-time",
    },
    {
        "company": "Globex Systems",
        "title": "Backend Engineer",
        "description": "Develop APIs and services for our analytics platform.",
        "location": "Remote",
        "salary_min": 110000,
        "salary_max": 140000,
        "employment_type": "full-time",
    },
    {
        "company": "Initech Solutions",
        "title": "Platform Engineer",
        "description": "Own the Kubernetes infrastructure and CI/CD pipelines.",
        "location": "Austin, TX",
        "salary_min": 125000,
        "salary_max": 155000,
        "employment_type": "full-time",
    },
]


def seed(conn: psycopg2.extensions.connection) -> None:
    cur = conn.cursor()

    # Insert companies, get IDs back
    company_ids: dict[str, int] = {}
    for company in COMPANIES:
        cur.execute(
            "INSERT INTO companies (name, website, description) VALUES (%s, %s, %s)"
            " ON CONFLICT DO NOTHING RETURNING id, name",
            (company["name"], company["website"], company["description"]),
        )
        row = cur.fetchone()
        if row:
            company_ids[row[1]] = row[0]

    # Look up any that already existed
    cur.execute("SELECT id, name FROM companies")
    for row in cur.fetchall():
        company_ids[row[1]] = row[0]

    # Insert listings
    for listing in LISTINGS:
        company_id = company_ids.get(listing["company"])
        if not company_id:
            print(f"Skipping listing '{listing['title']}': company not found")
            continue
        cur.execute(
            """
            INSERT INTO listings
                (company_id, title, description, location, salary_min, salary_max, employment_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (
                company_id,
                listing["title"],
                listing["description"],
                listing["location"],
                listing["salary_min"],
                listing["salary_max"],
                listing["employment_type"],
            ),
        )

    conn.commit()
    print(f"Seeded {len(COMPANIES)} companies and {len(LISTINGS)} listings.")


if __name__ == "__main__":
    conn = psycopg2.connect(DATABASE_URL)
    try:
        seed(conn)
    finally:
        conn.close()
