from sqlalchemy import create_engine, MetaData, Table
import json
from datetime import datetime
from .constants_db import CONNECTION_STR

class DataDAO():
    """
    Classe de conexão com o banco de dados dentro da beaglebone. Implementa métodos CRUD para as diferentes tabelas contidas na database.
    """
    def __init__(self, computer_name=''):
        """
        Este método inicializa a conexão com o banco de dados.

        Method that initialize the database connection.

        Args:
            None
        Returns:
            None
        """
        self.engine = create_engine(CONNECTION_STR)
        
        self.table_name = computer_name
        if computer_name == 'embed_computers':
            self.table_name = 'comp_data'
        
        self.metadata = MetaData(self.engine)
        self.metadata.reflect(self.engine)
        self.list_tables = self.__init_tables()

    def __init_tables(self):
        """
        Este método obtém os metadados de todas as tabelas criadas na database.

        Method that get all tables created in the database.

        Args:
            None
        Returns:
            A dictionary containning all tables of the database.
        """
        tables_dict = dict()
        tables = list(self.metadata.tables)
        for t in tables:
            tables_dict[t] = Table(t,self.metadata, autoload=True)
        return tables_dict

    def retrieve_data(self, id_number, number_rows=None):
        """
        Este método retorna a quantidade de linhas de uma tabela. Caso o número de linhas seja None,
        o método retorna toda a tabela.
        
        Method that retrieves a number of rows from the table. Case the number of rows is None,
        the method returns all the table.

        Args:
            number_rows:: The number of rows. If None, retrieve all table.
        Returns:
            A dictionary containig the data from the table.
        """
        data = list()
        table = self.list_tables[self.table_name]
        if self.table_name in list(self.metadata.tables):
            conn = self.engine.connect()
            if number_rows is not None:
                # output = conn.execute(table.select().where(table.c.sent==0).order_by(table.c.timestamp).limit(number_rows))
                output = conn.execute(table.select().where(table.c.id>id_number).order_by(table.c.timestamp).limit(number_rows))
            else:
                output = conn.execute(table.select())
            conn.close()
            for item in output:
                zip_obj = zip(item.keys(), item.values())
                zip_data = dict(zip_obj)
                zip_data["timestamp"] = zip_data["timestamp"].isoformat()
                data.append(dict(zip_data))
        return data

    def insert_data(self,data, timestamp, gps_data):
        """
        Este método cria um novo registro em uma tabela. O método recebe os dados já processados de todos os
        computadores, um timestamp e dados de gps para criar um novo registro.

        Method that creates a new registry in the table. It receives a compiled data from all the computers, 
        a timestamp and gps data to create a new registry.

        Args:
            data:: Dictionary containing the compilated data from the computers
            timestamp:: timestamp of when the data was generated.
            gps_data:: gps information about when and where the data was generated.
        Returns:
            None
        """
        # print("timestamp in database: {}".format(timestamp))
        insertion_str = {'data': json.dumps(data), 'timestamp': timestamp, 'gps': json.dumps(gps_data)}
        table = self.list_tables[self.table_name]
        conn = self.engine.connect()
        conn.execute(table.insert(), insertion_str)
        conn.close()

    def delete_data(self,id_number):
        """
        Este método deleta registros do banco de dados. Deleta apenas os registros enviados para o webservice.
        Não somente os registros enviados, mas confirmados que foram recebidos pelo webservice.


        Method that delete registries from the database, only when they are sent to the webservice and the webservice confirms that received
        the data.

        Args:
            None
        Returns:
            None
        """
        table = self.list_tables[self.table_name]
        conn = self.engine.connect()
        query = table.delete().where(table.c.id <= id_number)
        conn.execute(query)
        conn.close()

    def update_data(self,list_data):
        """
        Este método atualiza um registro, indicando que o registro foi recebido pelo webservice.

        Method that update a registry, pointing that the registry was received by the webservice.

        Args:
            list_data:: A list containing all registries received by the webservice.
        Returns:
            None
        """
        table = self.list_tables[self.table_name]
        conn = self.engine.connect()
        for data in list_data:
            query = table.update().where(table.c.id == data["id"]).values(sent=1)
            conn.execute(query)
        conn.close()

def main():
    """
    Função que testa a execução dos códigos DAO.

    Function to test the execution of the DAO codes.

    Args:
        None
    Returns:
        None
    """
    db_con = DataDAO('embed_computers')

    my_data = db_con.retrieve_data()
    with open('dump_comp_data_db.txt','w') as db_dump:
        for item in my_data:
            print(json.loads(item['data']))
            item['timestamp'] = str(item['timestamp'])
            db_dump.write(json.dumps(item))
            db_dump.write('\n')

if __name__ == "__main__":
    main()
