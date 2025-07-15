def dataframe_to_tale(table_name, data, conn, **kwargs):
    
    if 'table_name_suffix' in kwargs:
        table_name = table_name + '_' + kwargs['table_name_suffix']

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