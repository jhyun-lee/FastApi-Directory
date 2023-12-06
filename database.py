import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker , Session
from sqlalchemy import text




from users import User



database_url = "mysql+pymysql://root:keti@localhost:3306/resort_users" ## resort_users 데이터 베이스 사용



class engineconn:
    def __init__(self):
        self.engine = create_engine(database_url, pool_recycle=500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session


    def connection(self):
        conn = self.engine.connect()
        return conn
    

# ---------------------------------------------  SQL문  --------------------------------------------------------------------------------------

    def CheckTable(self, Session): # 조회
        
        check_query = text("SELECT * FROM idDatabase")
        result =Session.execute(check_query)
        return result


    def Create(self, Session, username, id, password, memo=""): 

        db_user=Session.execute(select(User).filter(User.id==id)).scalars().first()
        db_user_name=Session.execute(select(User).filter(User.username==username)).scalars().first()
        
        print("몇번실행?")

        if db_user==None and db_user_name==None: # id중복 체크
            db_user= User(username=username,id=id,password=password,memo=memo)
            Session.add(db_user)
            Session.commit()
            Session.refresh(db_user)
            return db_user
        
        else:
            print("이미 존재")



    def Delete(self,Session,num): # 데이터 받아와서 삭제 할 것  1번은 삭제 안됨

        db_user=Session.execute(select(User).filter(User.num==num)).scalars().first()

        if db_user:
            Session.delete(db_user)
            Session.commit()


    def modify(self,Session,username,link):
        try:
            query = text("UPDATE idDatabase SET memo = :link WHERE username = :username")
            Session.execute(query, {"link": link, "username": username})
            Session.commit()
        except Exception as e:
            Session.rollback()
            raise e
        finally:
            Session.close()



    def memoCheck(self,Session,usernametxt):
        print("조회시작")
        user = Session.query(User).filter_by(username=usernametxt).first()
        
        if user:
            Session.close()
            return user.memo
        else:
            Session.close()
            return ""
        
        

if __name__ == "__main__":

    engine = engineconn()
    Session_engine=engine.sessionmaker()
    
    #engine.Delete(Session_engine,6)
    engine.Create(Session_engine,'keti111','keti111','12341234',"dsfa")