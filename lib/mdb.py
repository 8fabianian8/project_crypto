class Mdb():
    """Класс для работы с базой данных mongodb"""
    def __init__(self, db_users, db_diary, db_portfolio):
        self._db_users = db_users
        self._db_diary = db_diary
        self._db_portfolio = db_portfolio


    def is_user(self, cid: str) -> bool:
        """Получение пользовотеля по cid (ID пользователя) """

        user = self._db_users.find_one({"cid": cid}) 

        if not user:
            return False 
        return True