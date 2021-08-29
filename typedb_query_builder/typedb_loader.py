from typedb.client import TypeDB, SessionType, TransactionType
import time
from typing import Callable, List
from datetime import datetime
from typedb_query_builder.utils import LoadingLogger
from typedb_query_builder.typedb_query_builder import TypeDBQueryBuilder
import multiprocessing


class TypeDBDataLoader:
    """Class used to load TypeDB queries from TypeDBQueryBuilder.
    """
    def __init__(
        self,
        data: List[TypeDBQueryBuilder],
        uri: str,
        keyspace: str,
        loads_per_transaction: int = 50,
        cpus: int = 1,
        logs_directory: str = None
    ) -> None:
        self.data = data
        self.uri = uri
        self.keyspace = keyspace
        self.loads_per_transaction = loads_per_transaction
        self.cpus = cpus
        self.logs_directory = logs_directory

    def load_data(self):
        """Loads data from list of TypeDBQueryBuilder objects.
        """
        queries = self._get_queries()
        self._load_in_parallel(
            function=self._load_queries,
            data=queries,
            num_threads=self.cpus,
            ctn=self.loads_per_transaction,
            logs_directory=self.logs_directory)

    def _get_queries(self) -> List[str]:
        """Extracts queries from list of TypeDBQueryBuilder objects.

        Returns:
            List[str]: List of valid TypeDB queries.
        """
        queries = []
        for gqb in self.data:
            gqb.compile_query()
            queries.append(gqb.get_query())
        return queries

    def _load_queries(
        self,
        queries_list,
        cnt: int = 50,
        process_id: int = 0,
        logs_directory=None
    ):
        """Inserts queries into TypeDB database.

        Args:
            queries_list ([type]): List of valid grakn quries
                to run in Grakn server.
            cnt (int, optional): Number of threads to use for data load.
                Defaults to 50.
            process_id (int, optional): Id of a process which executes
                the function. Used when run in paralell.
                Defaults to 0.
            logs_directory (str, optional): [description]. Defaults to None.
        """
        if logs_directory:
            logger = LoadingLogger(directory=logs_directory)
        start = time.time()
        with TypeDB.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                counter = 0
                transaction = session.transaction(TransactionType.WRITE)
                # Insert queries
                for uc_query in queries_list:
                    counter += 1
                    transaction.query().insert(uc_query)
                    if counter % cnt == 0:
                        transaction.commit()
                        transaction.close()
                        transaction = session.transaction(
                            TransactionType.WRITE
                            )
                        message = f"{counter},{datetime.now()}"
                        if logs_directory:
                            logger.log_loading(
                                process_id=process_id,
                                message=message
                            )
                    if counter % 1000 == 0:
                        print("Process: {}; {} queries added".format(
                                process_id,
                                counter
                            )
                            )
                transaction.commit()
                transaction.close()
        end = time.time()
        print(end-start)

    def _load_in_parallel(
        self,
        function: Callable,
        data: List[TypeDBQueryBuilder],
        num_threads: int,
        ctn: int,
        logs_directory: str = None
    ):
        """Runs a specific function to load data to Grakn several time
            in paralell.

        Args:
            function (Callable): function name to run in paralell
            data (List[TypeDBQueryBuilder]): List of TypeDBQueryBuilder
                objects used to load the data.
            num_threads (int): Number of threads to use for data load.
            ctn (int): Number of queries to load withing one trtanscation.
        """

        start_time = time.time()

        chunk_size = int(len(data)/num_threads)
        processes = []

        for i in range(num_threads):

            if i == num_threads - 1:
                chunk = data[i*chunk_size:]

            else:
                chunk = data[i*chunk_size:(i+1)*chunk_size]

            process = multiprocessing.Process(
                target=function,
                args=(chunk, ctn, i, logs_directory)
                )

            process.start()
            processes.append(process)

        for process in processes:
            process.join()

        end_time = time.time()
        print("-------------\nTime taken: {}".format(end_time - start_time))
