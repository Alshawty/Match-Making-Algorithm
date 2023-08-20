from MatchGenerator import *

# Pre-filter dates which have no available trainers
def date_filter_trainer(appointments, Trainers):
    posDates = []
    for i in range(len(appointments)):
        for j in range(len(Trainers)):
            for k in range(len(Trainers[j].potentialAppointments)):
                if appointments[i] == Trainers[j].potentialAppointments[k]:
                    appointments[i].myTrainers.append(Trainers[j])
                    if appointments[i] not in posDates:
                        posDates.append(appointments[i])
        appointments[i].update()

    print("date_filter_trainer completed")
    return posDates


# Pre-filter dates which have not enough players
def date_filter_players(players, team_size, minimum_teams, posDates):
    for i in range(len(posDates)):
        PlayersOnDate = []
        for j in range(len(players)):
            if posDates[i] in players[j].appointments:
                PlayersOnDate.append(players[j])
        if len(PlayersOnDate) < team_size * minimum_teams:
            posDates.delete(i)
    print("date_filter_players completed")
    return posDates


def team_maker(allPlayer):      # TODO this is temporary until we link the database to this shit
    Teams = []  # list of objects of type Match
    for player in allPlayer:
        if player.TeamId != -1:
            for team in Teams:
                if player.TeamId == team[0].TeamId:
                    team.append(player)
                    break
            newTeam = [player]
            Teams.append(newTeam)
    return Teams


# will make sure that all team members have the same appointments
def team_appointment_fix(team):
    for player in team:
        for appointment in player.appointments:
            for otherPlayer in team:
                if otherPlayer != player:
                    if appointment not in otherPlayer.appointments:
                        player.appointments.remove(appointment)


# ap_calc
"""
# this is an older function which has become mostly redundant due to the other approach within date_filter_player() changes to the classes
# Calculate the amounts of available players for all dates and returns the list
def ap_calc(players, appointments):         # todo review with team
    AP = []
    littleCounter = 0
    for appointment in appointments:
        AP.append(0)
        for player in players:
            if appointment in player.appointments:
                AP[littleCounter] += 1
        littleCounter += 1

    print("ap_calc completed")
    return AP
"""


# Deletes all matches which can not longer be formed, since the least impacting was picked. Returns the rest
def remove_impossible(matches, picked):
    to_delete = []
    index = 0
    if picked.appointment.location.capacity <= picked.appointment.occupying:       # if location is full
        for match in matches:
            if match.appointment == picked.appointment:
                to_delete.append(index)
                continue
            if picked.trainer.max_hours <= picked.trainer.hours:
                if match.trainer == picked.trainer:
                    to_delete.append(index)
                    continue
            for player in picked.player:
                if player in match:
                    to_delete.append(index)
                    break
            index += 1
    else:
        for match in matches:
            if picked.trainer.max_hours <= picked.trainer.hours:
                if match.trainer == picked.trainer:
                    to_delete.append(index)
                    continue
            for player in picked.player:
                if player in match.player:
                    to_delete.append(index)
                    break
            index += 1

    to_delete.sort()
    to_delete.reverse()
    for each in to_delete:
        del matches[each]
    print("remove_impossible completed")


# The main function responsible for finding out which match is the most optimal and
def distribution(P, teamSize, minimumTeams, appointments, trainers, skillStartStop, skillMaxDif, exclusiveMatch):
    # Course Variables
    # teamSize =4       # wanted amount of players in each team         #temp, and can be variable once implemented fully
    # minimumTeams = 2  # minimal amount of teams for each appointment  #temp, and can be variable once implemented fully
    # appointments = [] # will be provided by course creator
    # P = []            # is list of Player objects, with availability for all appointments, skill levels, and potentially team size
    P.sort()            # sorts all Players according to their skill level
    for i in range(len(P)):
        print(str(i) + ": " + str(P[i].skillLevel))
    # Trainers register for the course
    # trainers = []     # list of class objects Trainer, which will be provided
    # Skill range, max difference, and if it is a restricted skill group is exclusively matched within the skill group
    # skillStartStop = []
    # skillMaxDif = []
    # exclusiveMatch = []

    # Calculate the amounts of available players for all dates and save it as a variable
    # AP = ap_calc(P)

    # Pre-filter Dates for Trainer Availability and Potential player attendance
    possible_dates = date_filter_trainer(appointments, trainers)
    possible_dates = date_filter_players(P, teamSize, minimumTeams, possible_dates)

    # Initialize variables for matching Alg.
    # Finalized Matches
    result = []
    # Possible matches at date and time, listed after one another {{{1,2}},{{2,3},{1,2}}} 1&2 monday, 2&3 & 1&2 tuesday, for example
    possibleMatches = []

    teams = team_maker(P)

    for team in teams:
        team_appointment_fix(team)
        max_skillLevel = 0
        for teamPlayer in team:
            P.remove(teamPlayer)
            max_skillLevel = max(max_skillLevel, teamPlayer.skillLevel)
        possible_trainers = []
        for appointment in team[0].appointments:
            for trainer in appointment.myTrainers:
                if trainer.skillLevel >= max_skillLevel:
                    possible_trainers.append(trainer)
            for trainer in possible_trainers:
                possibleMatches.append(Match(team, appointment, trainer))

    # For each potential appointment, create a list of all potential matches
    for date in possible_dates:
        dateP = []
        for player in P:
            if date in player.appointments:
                dateP.append(player)    # "Players" in date, pre-made teams count as players(but multiple)
        """
        This is probably irrelevant for anything but the generate_matches() function, but we leave it here to keep in mind,
        that it might have algorithmic relevancy.
        PM = []     # PM = [0,1,2,0,3,0,....]
        CNM = []    # List of bool values, if player i has already got all his matches. 1 = ALL MATCHES FOUND, 0= there might be more
        """

        matchmaker = MatchGenerator(date, dateP, teamSize, skillMaxDif, skillStartStop, exclusiveMatch, trainers)
        possibleMatches += matchmaker.generate_matches()  # date needs to be stored in match information #array

    # Goes through all possibleMatches and figures out how many possible matches would be dropped for each match that is taken, and saves that value, to later pick the one with the lowest
    while possibleMatches:    # todo review & we might need to purge empty list within possible Matches at the end
        """
        List of removed matches for each match that is taken, how many matches are removed is one element,
        therefore index of a match, is index of removed_matches.
        Directly corresponds
        """
        min_match = possibleMatches[0]
        # find the number of matches that would be removed, when one match is picked
        for match in possibleMatches:
            if match.appointment.location.capacity <= (match.appointment.occupying+1):
                for otherMatch in possibleMatches:
                    if match.appointment == otherMatch.appointment:
                        match.lostMatches += 1
                        continue
                    if (match.trainer.hours + 1) == match.trainer.max_hours and match.trainer == otherMatch.trainer:
                        match.lostMatches += 1
                        continue
                    for member in match.player:
                        if member in otherMatch.player:
                            match.lostMatches += 1
                            break
            else:
                for otherMatch in possibleMatches:
                    if (match.trainer.hours + 1) == match.trainer.max_hours and match.trainer == otherMatch.trainer:
                        match.lostMatches += 1
                        continue
                    for member in match.player:
                        if member in otherMatch.player:
                            match.lostMatches += 1
                            break
            if match.lostMatches < min_match.lostMatches:
                # the matching with the smallest amount of removed matches
                min_match = match

        # add the chosen match to the final matches, and delete all matches which have now become impossible
        min_match.appointment.occupying += 1
        min_match.trainer.hours += 1
        print(min_match)
        result.append(min_match)
        remove_impossible(possibleMatches, min_match)       # remove now impossible matches

        # print("PossibleMatches: ")
        # print(possibleMatches)

    print("distribute completed")
    print("Result: ")
    for each in result:
        print(each)
    print(len(result))

    return result
