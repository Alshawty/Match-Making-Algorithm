from distribution_functions import *

def test():
    bigLocation = Location(1, 10000)
    appointments = [Appointment(1, 1400, bigLocation)]

    teamSize = 4
    minimumTeams = 2

    skillStartStop = [(1, 2), (2.01, 7.99), (8, 10)]
    skillMaxDif = [1, 1, 1.5]
    exclusiveMatch = [1, 0, 0]

    trainer = [Trainer(1, 10, appointments, 0, 10000)]

    player = []
    for i in range(0, 20):
        skill = random.randint(10, 10)/10
        player.append(Player(i, skill, appointments))

    distribution(player, teamSize, minimumTeams, appointments, trainer, skillStartStop, skillMaxDif, exclusiveMatch)