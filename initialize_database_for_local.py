import os

if __name__ == '__main__':
    #データベースファイルの削除
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(*[APP_ROOT, 'iStand', 'test.db'])
    try:
        os.remove(db_file)
    except:
        print('WARNING: {} does not exist.'.format(db_file))

    from iStand import db
    from iStand.models import *

    #データベース作成
    CREATE_DATABASE()

    #初期データ挿入
    Block1 = Block(position=0)
    Block2 = Block(position=0)
    Block3 = Block(position=1)
    Block4 = Block(position=1)
    Block5 = Block(position=3)
    Block6 = Block(position=3)
    db.session.add(Block1)
    db.session.add(Block2)
    db.session.add(Block3)
    db.session.add(Block4)
    db.session.add(Block5)
    db.session.add(Block6)

    Motor = Motor(frequency=100000, dutycycle=500000, speed=100)
    db.session.add(Motor)

    db.session.commit()
