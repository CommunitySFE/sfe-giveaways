import time

class Giveaway:

    active = False
    name = "unnamed giveaway"
    ends = time.ctime()

    @classmethod
    def from_database_object(cls, database_obj):
        """
        Returns a Giveaway object directly from a MongoDB data object.

        All values beginning with "_" are ignored.
        """
        obj = cls()
        for key, value in database_obj:
            if key.startswith("_"):
                continue
            if hasattr(obj, key):
                setattr(obj, value)
        return obj
