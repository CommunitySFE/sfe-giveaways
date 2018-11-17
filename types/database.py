
class DatabaseObject:

    # TODO eventually add a to_database_object

    @classmethod
    def from_database_object(cls, database_obj):
        """
        Returns the database object directly from a MongoDB data object.
        """
        obj = cls()
        for key, value in database_obj.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


    @classmethod
    def to_database_object(cls):
        """
        Returns the DatabaseObject as a dictionary.
        """
        return vars(cls)
    