class Player:
    def __init__(self, Pid, skillLevel, appointments, prefPartner=[], TeamId=-1):  # todo temp appointments instead of availability
        self.Pid = Pid
        self.skillLevel = skillLevel
        # self.availability = availability
        self.appointments = appointments             # TODO  need to properly assign the availabilities with a function. This depends on the for which they are provided in
        self.prefPartner = prefPartner      # Array of preferred Partners
        self.TeamId = TeamId

    def __lt__(self, other):
        return self.skillLevel < other.skillLevel

    def __eq__(self, other):
        if type(self) is type(other):
            return self.skillLevel == other.skillLevel
        else:
            return False

    def __gt__(self, other):
        return self.skillLevel > other.skillLevel


class Trainer:
    def __init__(self, Tid, skillLevel, appointments, hours, max_hours):    # todo temp appointments instead of availability
        self.Tid = Tid
        self.skillLevel = skillLevel
        # self.availability = availability
        self.potentialAppointments = appointments     # TODO  need to properly assign the availabilities with a function. This depends on the for which they are provided in
        self.ownMatches = []
        self.hours = hours
        self.max_hours = max_hours


class Appointment:
    def __init__(self, day, time, location):
        self.day = day
        self.time = time
        self.daytime = day + time/10000
        self.location = location
        self.maxTrainerSkill = 0
        self.occupying = 0
        self.myTrainers = []                # Trainer which are available for the appointment

    def test_update(self, lostTrainer):
        maxTrainerSkill = 0
        for trainer in self.myTrainers and not lostTrainer:
            maxTrainerSkill = max(self.maxTrainerSkill, trainer.skillLevel)
        return maxTrainerSkill

    def update(self):
        self.maxTrainerSkill = 0
        for trainer in self.myTrainers:
            self.maxTrainerSkill = max(self.maxTrainerSkill, trainer.skillLevel)

    def __lt__(self, other):
        return self.daytime < other.daytime

    def __eq__(self, other):
        if type(self) is type(other):
            return self.daytime == other.daytime
        else:
            return False

    def __gt__(self, other):
        return self.daytime > other.daytime


class Location:
    def __init__(self, Lid, capacity):
        self.Lid = Lid
        self.capacity = capacity


class Match:
    """ Player is the match of players as list, appointment obvious, trainer the trainer for the match"""
    def __init__(self, player, appointment, trainer):
        self.player = player
        self.appointment = appointment
        self.trainer = trainer
        self.lostMatches = 0

    def __str__(self):
        string = ""
        for each in self.player:
            string += str(each)
            string += ", "
        return string


class TempMatch:
    """ Player is the match of players as list, appointment obvious, trainer the trainer for the match"""
    def __init__(self, player, appointment, trainers):
        self.player = player
        self.appointment = appointment
        self.trainers = trainers        # list of trainers
        self.lost_Matches = 0