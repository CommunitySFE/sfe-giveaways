from structures.database import DatabaseObject


class Reward(DatabaseObject):

    def __init__(self):
        super().__init__()
        self.name = "unnamed reward"
        self.inform = False


class RoleReward(Reward):

    def __init__(self):
        super().__init__()
        self.role_id = 0
