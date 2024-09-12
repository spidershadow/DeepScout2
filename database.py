import os
import psycopg2
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential

def drop_tables(conn):
    queries = [
        "DROP TABLE IF EXISTS startup_assessments",
        "DROP TABLE IF EXISTS startups",
        "DROP TABLE IF EXISTS sectors"
    ]
    with conn.cursor() as cur:
        for query in queries:
            cur.execute(query)
    conn.commit()

def create_tables(conn):
    queries = [
        '''
        CREATE TABLE IF NOT EXISTS sectors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS startups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            sector_id INTEGER REFERENCES sectors(id),
            sub_sector VARCHAR(255),
            funding DECIMAL,
            technology TEXT
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS startup_assessments (
            id SERIAL PRIMARY KEY,
            startup_id INTEGER REFERENCES startups(id) UNIQUE,
            risk_score INTEGER,
            comments TEXT
        )
        '''
    ]
    
    with conn.cursor() as cur:
        for query in queries:
            cur.execute(query)
    conn.commit()

def populate_sectors(conn):
    sectors = [
        "Artificial Intelligence",
        "Quantum Computing",
        "Biotechnology",
        "Renewable Energy",
        "Nanotechnology"
    ]
    check_query = "SELECT id FROM sectors WHERE name = %s"
    insert_query = "INSERT INTO sectors (name) VALUES (%s) RETURNING id"
    with conn.cursor() as cur:
        for sector in sectors:
            cur.execute(check_query, (sector,))
            result = cur.fetchone()
            if result is None:
                cur.execute(insert_query, (sector,))
                result = cur.fetchone()
                print(f"Inserted new sector: {sector} with id {result['id']}")  # Debug log
    conn.commit()
    print("Sectors population completed")  # Debug log

def populate_startups(conn):
    startups = [
        ("SolarTech", "Solar panel manufacturer", "Renewable Energy", "Solar Energy", 1000000, "Advanced photovoltaic cells"),
        ("WindPower", "Wind turbine developer", "Renewable Energy", "Wind Energy", 2000000, "High-efficiency turbine blades"),
        ("HydroFlow", "Hydroelectric solutions provider", "Renewable Energy", "Hydropower", 1500000, "Micro-hydro generators"),
        ("BioFuel Innovations", "Biofuel research and production", "Renewable Energy", "Bioenergy", 3000000, "Algae-based biofuels"),
        ("GeoTherm Solutions", "Geothermal energy systems", "Renewable Energy", "Geothermal Energy", 2500000, "Deep drilling techniques"),
        ("AI Assistant", "AI-powered virtual assistant", "Artificial Intelligence", "Natural Language Processing", 5000000, "Advanced language models"),
        ("QuantumBit", "Quantum computing hardware", "Quantum Computing", "Quantum Hardware", 10000000, "Superconducting qubits"),
        ("BioGene", "Gene therapy solutions", "Biotechnology", "Genetic Engineering", 7000000, "CRISPR-Cas9 gene editing"),
        ("NanoMed", "Nanoparticle drug delivery", "Nanotechnology", "Nanomedicine", 4000000, "Targeted drug delivery systems")
    ]
    
    query = """
    INSERT INTO startups (name, description, sector_id, sub_sector, funding, technology)
    VALUES (%s, %s, (SELECT id FROM sectors WHERE name = %s), %s, %s, %s)
    ON CONFLICT (name) DO NOTHING
    """
    
    with conn.cursor() as cur:
        for startup in startups:
            cur.execute(query, startup)
    conn.commit()
    print("Startups population completed")  # Debug log

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def init_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ["PGHOST"],
            database=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            port=os.environ["PGPORT"],
            cursor_factory=RealDictCursor
        )
        drop_tables(conn)
        create_tables(conn)
        populate_sectors(conn)
        populate_startups(conn)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        raise

def execute_query(conn, query, params=None):
    with conn.cursor() as cur:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError:
            return None

def get_sectors(conn):
    query = "SELECT * FROM sectors"
    return execute_query(conn, query)

def get_startups_by_sector(conn, sector, sub_sector):
    query = """
    SELECT s.* FROM startups s
    JOIN sectors sec ON s.sector_id = sec.id
    WHERE sec.name = %s AND s.sub_sector = %s
    """
    return execute_query(conn, query, (sector, sub_sector))

def save_startup_assessment(conn, startup_id, risk_score, comments):
    query = """
    INSERT INTO startup_assessments (startup_id, risk_score, comments)
    VALUES (%s, %s, %s)
    ON CONFLICT (startup_id) DO UPDATE
    SET risk_score = EXCLUDED.risk_score, comments = EXCLUDED.comments
    """
    execute_query(conn, query, (startup_id, risk_score, comments))
    conn.commit()

def get_curated_startups(conn):
    query = """
    SELECT s.*, sa.risk_score, sa.comments
    FROM startups s
    JOIN startup_assessments sa ON s.id = sa.startup_id
    ORDER BY sa.risk_score DESC
    LIMIT 10
    """
    return execute_query(conn, query)
