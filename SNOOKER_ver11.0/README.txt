Design TODO:
	- Rever layouts e espaçamentos
	- Flow de configuração -> steps -> por no fim
	- Menu de ajuda -> abrir window
	- Shifts em vez das teams para poupar espaço

Icones
	+ Add -> <div>Icons made by <a href="https://www.flaticon.com/authors/pixel-perfect" title="Pixel perfect">Pixel perfect</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
	+ Remove -> <div>Icons made by <a href="https://icon54.com/" title="Pixel perfect">Pixel perfect</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
	+ Save -> <div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
	+ Load -> <div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
	+ https://folk.idi.ntnu.no/mlh/hetland_org/coding/python/levenshtein.py

Incluir futuro
	- Clientes -> açoes para determinados clientes
	- adaptar o load e save das teams para diferentes areas 
	- melhorar ficheiros de configuração (standard e custom)
	- diferentes açoes dos mesmos utilizadores para diferentes horarios
	- Diferentes distribuiçóes nas familias (cada familia terá um multiplicador - depende da area de trabalho)
	- Geração dos tickets (datas) -> metodo de geração de forma cumulativa a partir de data
	- Mitre Attack nos incidents
	- adicionar numero de teams
	- Mais features/meta-features
	- Optimização do scheduling dos tickets

		
Features Incluidas (podem não estar todas as features!):
	- load de teams que não estejam nos config
	- prevent actions with just numbers (actions with length 1)
	- Para cada operador ter um delta (% min 20 e max 200) para cada subtecnica (analistas usam sempre a mesma tecnica e demoram o mesmo tempo)
	- Operadores não acabam de resolver os tickets antes de serem escalados (a equipa seguinte termina)
	- Ajuste dos layouts
	- Incluido ips dos paises
		+ Ips fonte -> https://datahub.io/core/geoip2-ipv4#data
		+ Paises fonte (com timezones) -> https://gist.github.com/mlisovyi/e8df5c907a8250e14cc1e5933ed53ffd
	- Paises suspeitos -> os ips são provenientes do IPSUM
	- inputs speed de cada user
	- Subtecnicas
		+ inputs minimum e maximo de tempo
		+ inputs 50 a 200% da duração de cada subtecnica
	- Probabilidade de o analista usar a mesma ação da subfamilia ou mutar a ação
	- Probabilidade de o analista usar a mesma ação que resolveu o mesmo problema ou usar uma nova
	- id crescente no tempo
	- reformulada a forma como os tickets resolvidos -> devem ser resolvidos um a um e não todos de seguida -> problema com as açoes updated
	- ações do users -> agora parte das subfamilias -> pode-se adicionar, remover, manter ou modificar subtecnicas por outras subtecnicas da familia -> subtecnicas aleatorias em posições aleatorias
		 - 1-2 alterações nas ações dos users
	- Escalar ticket 
		- 20% max de escalar
		- corta o ultima passo do user
		- distancia entre action chosen e subfamily action escalar se for superior a threshold
		- Não se dá update à ação do utilizador
	- Portas
		- 50% well-known (destination) e 50% registered ports (destination)
	- Time range entre os eventos para deteção de eventos similares em pouco tempo
	- Casos suspeitos, similares, coordenados e prioridade devem ser tratados pelo Sistema de recomendação
	- Odd de ataques coordenados na interface assim como se devem contemplar um/vários tipo(s) de ataque -> tirei se queremos multiple detection
	- Counter e o timerange para cada subfamilia na interface
	- Networks alocadas aos clientes 
	- Info sobre a criação/operações nas ações dos users
	- Probabilidade para mes das familias - timeseries decomposition 
	- Mudar abordagem dos ips suspeitos -> adicionei um dos ips maus aos paises suspeitos
	- Percentis para avaliar os ratings dos eventos -> Pode haver resultados iguais
	- Seleção de utilizadores 
		- Queue
		- Execution Time (o mais rápido)
	- Sazonalidade nos Tickets
	- Tickets replicados, coordenados e similares
	- Timestamps incluidos
	- analise profunda sobre se ação do utilizador foi fechar o ticket ou se foi transferido
		+ Cada equipa e os seus analistas têm uma taxa de transferir os tickets
		+ Na análise exclui os tickets que são transferidos para não influenciar a escolha dos users
			+ Familias de ações para inicio e termino
			++ Retirar a ultima antes da final e colocar uma especial (caso tenham apenas duas subtécnicas apenas substituimos a ultima)
				++ Aplicamos a todos os tickets que são transferidos ou só aqueles que são previamente escalados (apenas fiz para os previamenete escalados) -> Apliquei a todos
					++ Dentro dos tickets transferidos, existem tickets que são transferidos por escalarem para outra equipa ou pq a distancia da ação escolhida para a da subfamilia é superior à distancia máxima indicada (2)
			++ As ações de inicio e fim tem as mesmas subtecnicas com a mesma duração para todas as familias
	
Profiling do projeto (Tempo e recursos gastos pelas funções dos projetos):
	- DatasetGenerator.py -> Commentar o main() -> Descomentar o __name__ == '__main__'
	- Utils.py -> função isTicketSuspicious -> Descomentar o comentado -> Comentar o seguinte:
	    day_off_list = Variables.suspicious_countries[country]["widget day off"].text()
            if (day_off_list.find(day) == -1):
                if Utils.isTimeBetween(Variables.suspicious_countries[country]["widget start date"].text(), Variables.suspicious_countries[country]["widget end date"].text(), ticket_time):
                    #print("Ticket id suspicious", ticket)
                    return True
	- Run Profiler (na barra em cima)