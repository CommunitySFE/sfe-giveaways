

class DatabaseObject:

    def __init__(self):
        self.mongodb_id = None

    @classmethod
    def from_database_object(cls, database_obj):
        """
        Returns the database object directly from a MongoDB data object.
        """
        obj = cls()
        for key, value in database_obj.items():
            if key == "_id":
                key = "mongodb_id"
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

    def to_database_object(self):
        """
        Returns the DatabaseObject as a dictionary.

        This excludes the mongodb_id object.
        """
        database_object = vars(self)
        delete_keys = []
        for key in database_object.keys():
            if key.startswith("_") or key == "mongodb_id":
                delete_keys.append(key)
        for key in delete_keys:
            del database_object[key]
        return database_object
