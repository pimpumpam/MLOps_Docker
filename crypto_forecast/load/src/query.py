def is_exists(database_name, table_name):
    
    return f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE 1=1
                AND TABLE_SCHEMA = '{database_name}' 
                AND TABLE_NAME = '{table_name}'
            ;
            """


def get_recent_timestamp(table_name, **kwargs):
            
    time_col = kwargs['time_col'] if 'time_col' in kwargs else 'candle_date_time_utc'    
    
    return f"SELECT max({time_col}) FROM {table_name}"


def dataframe_to_tale(table_name, data, conn, **kwargs):
    
    if 'table_name_suffix' in kwargs:
        table = table + '_' + kwargs['table_name_suffix']

    if 'table_exists_handling' not in kwargs:
        exist_handling = 'append'
    else:
        exist_handling = kwargs['table_exists_handling']

    data.to_sql(
        f'{table_name}', 
        conn, 
        if_exists=exist_handling, 
        index=True,
        index_label='id'
    )