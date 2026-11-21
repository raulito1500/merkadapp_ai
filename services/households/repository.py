import psycopg

from shared.config import SUPABASE_DATABASE_URL


def create_household(name: str, admin_user_id: str) -> str:
    with psycopg.connect(SUPABASE_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into households (name, admin_user_id) values (%s, %s) returning id
                """,
                (name, admin_user_id),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("El INSERT no devolvió ninguna fila")
            household_id = str(row[0])
            cur.execute(
                """
                insert into household_members (household_id, user_id, role) values (%s, %s, 'admin')
                """,
                (household_id, admin_user_id),
            )
    return household_id


if __name__ == "__main__":
    try:
        create_household("Wohnung", "c8aafd63-7477-4a81-a359-7b99af52d8a6")
    except Exception as e:
        print(e)
