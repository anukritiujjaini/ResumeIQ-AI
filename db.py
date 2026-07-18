from sqlalchemy import create_engine,text
from sqlalchemy.orm import declarative_base,sessionmaker
#can also add sessionmaker if needed

DATABASE_URL = "mysql+pymysql://2qjT3spWq2onr3A.root:eFjvHMea4YVdJpMG@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/test?ssl_ca=C:\\Users\\ASUS\\Downloads\\isrgrootx1.pem&ssl_verify_cert=true&ssl_verify_identity=true"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "ca": r"C:\Users\ASUS\Downloads\isrgrootx1.pem"
        }
    }
)
base=declarative_base()
sessionlocal= sessionmaker(autocommit=False,autoflush=False,bind=engine)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connected successfully!")
        print(result.fetchall())
except Exception as e:
    print("❌ Connection failed")
    print(type(e).__name__)
    print(e)

print("base object =", base)    