import pymysql
import yaml
import pyodbc
from tabulate import tabulate


class sql:
    """Run a predetermined SQL command"""

    def __init__(self):

        with open('sql.yaml', 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise Exception(exc)

        self.connections = config['connections']
        self.commands = config['sql_commands']

    def __run__(self, params=None):

        # check a sql command has been passed
        try:
            sql_command = params[0]
        except IndexError:
            print("missing sql command, type 'sql help' for options")
            return()

        if sql_command == 'help':
            for command in self.commands:
                desc = self.commands[command]['description']
                print(f"{command} : {desc}")
            return()

        # query details for query and connection details for where to run it
        query_details = self.commands[sql_command]
        conn_details = self.connections[query_details['connection']]

        # check parameter passed if required
        try:
            sql_param = ' '.join(params[1:])
        except IndexError:
            sql_param = None

        if query_details['parameter'] == True and sql_param == None:
            raise Exception('missing query parameter')

        for query in query_details['queries']:

            sql_i = SQL_Conn()
            results = sql_i.run_query(conn_details, query, sql_param)

            formatted = ', '.join(results['tables'])

            print(f'\ntables: {formatted}')
            print(tabulate(results['results'],
                           headers=results['columns'],
                           tablefmt="pretty"))


class SQL_Conn:

    def get_connection(self, conn):
        self.type = conn['type']

        server = conn['server']
        database = conn['database']
        if self.type == 'mysql':
            self.connection = pymysql.connect(host=conn['server'],
                                              user=conn['username'],
                                              password=conn['password'],
                                              database=conn['database'],
                                              cursorclass=pymysql.cursors.DictCursor)
        elif self.type == 'sqlserver':
            self.connection = pyodbc.connect(
                f'DRIVER=SQL Server; SERVER={server}; DATABASE={database};Trusted_Connection=yes;')
        elif self.type == 'azure':
            username = conn['username']
            password = conn['password']
            self.connection = pyodbc.connect(
                f'DRIVER=SQL Server; SERVER={server}; DATABASE={database}; UID={username}; PWD={password}')
        else:
            raise Exception(f"type {self.type} not recognised")

    def run_query(self, conn, query, param):

        results = {}

        self.get_connection(conn)

        with self.connection:
            with self.connection.cursor() as cursor:

                cursor.execute(query,
                               {
                                   'input': param
                               })

                content = cursor.fetchall()
                if self.type == 'mysql':
                    results['results'] = [i.values() for i in content]
                else:
                    results['results'] = [i for i in content]

                results['columns'] = [i[0] for i in cursor.description]
                results['tables'] = self.tables_used(query)

            self.connection.commit()

        return results

    def tables_used(self, query):

        query_list = [word for word in query.split(' ') if word]

        tables = []

        for index, word in enumerate(query_list):

            if word in ('FROM', 'JOIN', 'from', 'join') and query_list[index+1] not in tables:

                table = query_list[index+1].lower()
                formatted_table = table.split('.')[-1]

                remove_characters = ['(', ')', '[', ']']

                for char in remove_characters:
                    formatted_table = formatted_table.replace(char, "")

                tables.append(formatted_table)
        return(set(tables))
