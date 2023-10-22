import pymysql

class mysql_helper:
    def __init__(self, dbName):
        self.dbName = dbName
        
    def __enter__(self):
        try:
            self.connection = pymysql.connect(
                host="db-jiabar.ceh6fst78slz.ap-northeast-1.rds.amazonaws.com",
                user="jiabar",
                passwd="jiabar10211022",
                database=self.dbName)
            self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            print('Connect db successful!')
            return self.cursor
        except Exception as e:
            raise Exception('Fail to connect db! {}'.format(str(e)))
        pass
    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.connection.close()

if __name__ == '__main__':
    with mysql_helper('JiaBar') as cur:
        cur.execute('SELECT * FROM User')
        result = cur.fetchall()
        import pprint
        pprint.pprint(result)
