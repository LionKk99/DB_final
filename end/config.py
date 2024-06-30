class BaseConfig(object):

    # 数据库的配置
    DIALCT = "mysql"
    DRITVER = "pymysql"
    HOST = '127.0.0.1'
    PORT = "3306"
    USERNAME = "root"
    PASSWORD = "HJA20040810" # 你自己电脑数据库的密码
    DBNAME = 'db_n'

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:HJA20040810@localhost:3306/db_n"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

# # 密钥，可随意修改
# SECRET_KEY = '你猜'

