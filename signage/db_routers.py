"""
Database Router for Digital Signage

Routes queries for SalesBoardSummary to the data_connect database.
All other models use the default database.
"""


class DataConnectRouter:
    """
    Database router that routes SalesBoardSummary model to data_connect database.

    The SalesBoardSummary table is an external read-only table populated by
    an ETL process. Django should not create/modify this table.
    """

    # Models that should use the data_connect database
    DATA_CONNECT_MODELS = {'salesboardsummary', 'employeesalessummary'}

    def db_for_read(self, model, **hints):
        """Route reads for SalesBoardSummary to data_connect."""
        if model._meta.model_name in self.DATA_CONNECT_MODELS:
            return 'data_connect'
        return None

    def db_for_write(self, model, **hints):
        """
        Route writes for SalesBoardSummary to data_connect.
        Note: We shouldn't be writing to this table, but if we do,
        route it to the correct database.
        """
        if model._meta.model_name in self.DATA_CONNECT_MODELS:
            return 'data_connect'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database.
        Prevent relations between data_connect models and default models.
        """
        db1 = self._get_db_for_model(obj1)
        db2 = self._get_db_for_model(obj2)

        if db1 and db2:
            return db1 == db2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Never run migrations on data_connect database.
        Never run migrations for SalesBoardSummary on any database.
        """
        if db == 'data_connect':
            # Don't run any migrations on data_connect
            return False

        if model_name and model_name.lower() in self.DATA_CONNECT_MODELS:
            # Don't migrate SalesBoardSummary anywhere
            return False

        return None

    def _get_db_for_model(self, obj):
        """Helper to determine which database a model belongs to."""
        if obj._meta.model_name in self.DATA_CONNECT_MODELS:
            return 'data_connect'
        return 'default'
