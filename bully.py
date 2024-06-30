class Process:
    def __init__(self, id):
        self.id = id
        self.active = True
        self.leader = None

    def __str__(self):
        return f'Processo {self.id}'

def bully_election(processes, initiator_id):
    print(f'\n{processes[initiator_id]} detecta que o líder caiu e inicia uma eleição.')
    max_id = -1
    for process in processes:
        if process.active and process.id > initiator_id:
            print(f'{processes[initiator_id]} envia mensagem de eleição para {process}.')
            if process.id > max_id:
                max_id = process.id

    if max_id == -1:
        max_id = processes[initiator_id].id

    for process in processes:
        if process.active and process.id <= max_id:
            process.leader = max_id

    print(f'\nProcesso {max_id} é o novo líder.')

def main():
    processes = [Process(1), Process(2), Process(3), Process(4), Process(5)]

    while True:
        print("\nProcessos ativos:")
        for process in processes:
            if process.active:
                print(f'{process} (Líder: {process.leader})')

        # Simulação de falha do líder
        leader_down = input("\nO líder caiu? (s/n): ").strip().lower()
        if leader_down == 's':
            for process in processes:
                if process.leader == max(p.id for p in processes if p.active):
                    process.leader = None

            initiator = int(input("Qual processo inicia a eleição? (ID): ")) - 1
            bully_election(processes, initiator)

        print("\nEstado atual:")
        for process in processes:
            if process.active:
                print(f'{process} (Líder: {process.leader})')

        choice = input("\nDeseja continuar a simulação? (s/n): ").strip().lower()
        if choice != 's':
            break

        change = input("Deseja alterar o estado de algum processo? (s/n): ").strip().lower()
        if change == 's':
            for i, process in enumerate(processes):
                new_state = input(f"Ativar {process} (s/n): ").strip().lower()
                processes[i].active = (new_state == 's')

if __name__ == "__main__":
    main()
