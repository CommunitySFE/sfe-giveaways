

class DatabaseObject:

    mongodb_id = None

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


    @classmethod
    def to_database_object(cls):
        """
        Returns the DatabaseObject as a dictionary.

        This excludes the mongodb_id object.
        """
        database_object = dict(vars(cls))
        del database_object["mongodb_id"]
        return database_object
    