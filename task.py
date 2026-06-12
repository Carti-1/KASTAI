import datetime

class Tarefa:
    status_pendente = "Pendente" 
    status_em_andamento = "Em Andamento" 
    status_concluida = "Concluída" 

    def __init__(self, id_tarefa, titulo, descricao, usuario_associado, prioridade="Média"):
        self.id_tarefa = id_tarefa
        self.titulo = titulo
        self.descricao = descricao
        self.status = Tarefa.status_pendente #Tarefa é criada como pendente
        self.usuario_associado = usuario_associado
        self.prioridade = prioridade
        self._data_limite = None
    
    def mudar_status(self, novo_status):
        if novo_status in [Tarefa.status_pendente, Tarefa.status_em_andamento, Tarefa.status_concluida]:
            self.status = novo_status
        else:
            raise ValueError("Esse status não existe!")

    def definir_data_limite(self, data):
        if isinstance(data, datetime.date):
            self._data_limite = data
        else:
            raise ValueError("Data deve ser válida!")
