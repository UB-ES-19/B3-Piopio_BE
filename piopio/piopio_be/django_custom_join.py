from django.db.models.fields.related import ForeignObject
from django.db.models.options import Options
from django.db.models.sql.constants import LOUTER
from django.db.models.sql.datastructures import Join
from django.db.models.sql.where import ExtraWhere
from django.db import models

class CustomJoin(Join):
    def __init__(self, subquery, subquery_params, parent_alias, table_alias, join_type, join_field, nullable):
        self.subquery_params = subquery_params
        super(CustomJoin, self).__init__(subquery, parent_alias, table_alias, join_type, join_field, nullable)

    def as_sql(self, compiler, connection):
        """
        Generates the full
           LEFT OUTER JOIN (somequery) alias ON alias.somecol = othertable.othercol, params
        clause for this join.
        """
        params = []
        sql = []
        alias_str = '' if self.table_alias == self.table_name else (' %s' % self.table_alias)
        params.extend(self.subquery_params)
        qn1 = compiler.quote_name_unless_alias
        qn2 = connection.ops.quote_name

        sql.append('%s (%s)%s ON (' % (self.join_type, self.table_name, alias_str))
        for index, (lhs_col, rhs_col) in enumerate(self.join_cols):
            if index != 0:
                sql.append(' AND ')
            sql.append('%s.%s = %s.%s' % (
                qn1(self.parent_alias),
                qn2(lhs_col),
                qn1(self.table_alias),
                qn2(rhs_col),
            ))
        extra_cond = self.join_field.get_extra_restriction(
            compiler.query.where_class, self.table_alias, self.parent_alias)
        if extra_cond:
            extra_sql, extra_params = compiler.compile(extra_cond)
            extra_sql = 'AND (%s)' % extra_sql
            params.extend(extra_params)
            sql.append('%s' % extra_sql)
        sql.append(')')
        return ' '.join(sql), params


def join_to_queryset(
        table, subquery, table_field, subquery_field, queryset, alias, is_raw=False,
        extra_restriction_func=lambda where_class, alias, related_alias: None
):
    """
    Add a join on `subquery` to `queryset` (having table `table`).
    """
    foreign_object = ForeignObject(to=subquery, from_fields=[None], to_fields=[None], rel=None, on_delete=models.CASCADE)
    foreign_object.opts = Options(table._meta)
    foreign_object.opts.model = table
    foreign_object.get_joining_columns = lambda: ((table_field, subquery_field),)
    foreign_object.get_extra_restriction = extra_restriction_func

    subquery_sql, subquery_params = (subquery.query, []) if is_raw else subquery.query.sql_with_params()

    join = CustomJoin(subquery_sql, subquery_params, table._meta.db_table, alias, LOUTER, foreign_object, True)

    queryset.query.join(join)

    # hook for set alias
    join.table_alias = alias
    queryset.query.external_aliases.add(alias)

    return queryset


def join_to_table(
        table, table2, table_field, table2_field, queryset, alias,
        extra_restriction_func=lambda where_class, alias, related_alias: None
):
    """
    Add a join on `table2` to `queryset` (having table `table`).
    """
    foreign_object = ForeignObject(to=table2, from_fields=[None], to_fields=[None], rel=None)
    foreign_object.opts = Options(table._meta)
    foreign_object.opts.model = table
    foreign_object.get_joining_columns = lambda: ((table_field, table2_field),)
    foreign_object.get_extra_restriction = extra_restriction_func

    join = Join(table2._meta.db_table, table._meta.db_table, alias, LOUTER, foreign_object, True)
    queryset.query.join(join)

    # hook for set alias
    join.table_alias = alias
    queryset.query.external_aliases.add(alias)

    return queryset


def get_active_extra_restriction(where_class, alias, related_alias):
    where = '{alias}.active = True'.format(
        alias=alias
    )
    children = [ExtraWhere([where], ())]
    return where_class(children)