from AHS_Classes import *
from itertools import combinations
import random

FINAL_CAP = 10000
FINAL_MIN_MATCHES = 5

class MatchGenerator:
    def __init__(self, date, P, team_size, skill_differences, skill_brackets, exclusiveMatch, trainers):
        self.date = date
        self.P = P
        self.PM = [0 for i in range(len(P))]
        self.CNM = [0 for i in range(len(P))]
        self.team_size = team_size

        self.skill_differences = skill_differences
        self.skill_brackets = skill_brackets
        self.exclusiveMatch = exclusiveMatch

        self.trainers = trainers  # trainer available at said date

    # find the lowest player (based on skill level) that the current player can be matched with
    def find_lowest_teampartner(self, curr_player_index):
        """
        finds the player with the lowest skill that is still matchable with the current player

        :param curr_player_index: Index of the current player
        :return: index of the lowest player that is still matchable
        """
        if curr_player_index <= 0:
            return curr_player_index
        teammate_index = curr_player_index
        while self.skill_difference_allowed(curr_player_index, teammate_index - 1):
            teammate_index -= 1
            if teammate_index <= 0:
                return 0

        return teammate_index

    # find the highest player (based on skill level) that the current player can be matched with
    def find_highest_teampartner(self, curr_player_index):
        """
        finds the player with the highest skill that is still matchable with the current player

        :param curr_player_index: Index of the current player
        :return: index of the highest player that is still matchable
        """
        if curr_player_index == len(self.P) - 1:
            return curr_player_index

        teammate_index = curr_player_index
        while self.skill_difference_allowed(curr_player_index, teammate_index + 1):
            teammate_index += 1
            if teammate_index >= len(self.P) - 1:
                return teammate_index

        return teammate_index

    # checks if the skill difference is possible
    def skill_difference_allowed(self, p1_index, p2_index):
        """
        checks whether the skill difference between 2 players is low enough for them to form a team

        :param p1_index: index of the first player
        :param p2_index: index of the second player
        :return: bool, True if skill difference is allowed
        """
        p1_skillbracket = self.find_skillbracket(p1_index)
        p2_skillbracket = self.find_skillbracket(p2_index)

        if self.is_bracket_exclusive(p1_skillbracket, p2_skillbracket):
            return False

        # find min skilldifference so that skill difference condition is true for all players
        min_skilldifference = min(self.skill_differences[p1_skillbracket], self.skill_differences[p2_skillbracket])

        return abs(self.P[p1_index].skillLevel - self.P[p2_index].skillLevel) <= min_skilldifference

    def is_bracket_exclusive(self, p1_skillbracket, p2_skillbracket):
        # if one of the brackets is exclusive, players cannot match
        if p1_skillbracket != p2_skillbracket:
            if self.exclusiveMatch[p1_skillbracket] == 1 or self.exclusiveMatch[p2_skillbracket] == 1:
                return True

        return False

    def possible_trainers(self, max_skill_level):
        possible_trainers = []
        for trainer in self.trainers:
            if trainer.skillLevel >= max_skill_level:
                possible_trainers.append(trainer)
        return possible_trainers

    # generates a match that satisfies all conditions
    def generate_match(self, matches, lowest_player_index, curr_player_index, highest_player_index):
        """
        generates a not yet chosen match which is possible according to the maximal skill difference

        :param matches: matches that have already been chosen
        :param lowest_player_index: index of the lowest player still matchable
        :param curr_player_index: index of current player to search match for
        :param highest_player_index: index of the highest player still matchable
        :return: the match that satisfies all conditions, None if not one can be found
        """

        final_team = None
        # generate player range without curr player

        skill_range = list(range(lowest_player_index, highest_player_index + 1))
        skill_range.remove(curr_player_index)

        # find all possible combinations
        for i in range(2000):
            # TODO choose randomized or complete version
            if len(skill_range) >= self.team_size - 1:
                random_players = self.pick_random(skill_range)
            else:
                continue
            curr_team = []
            for index in random_players:
                curr_team.append(skill_range[index])
            curr_team.append(curr_player_index)
            curr_team.sort()

            # check conditions
            if self.skill_difference_allowed(curr_team[0], curr_team[-1]):
                # check if match has already been chosen
                if self.match_exists(matches, curr_team):
                    continue
                # find possible trainers
                possible_trainers = self.possible_trainers(self.P[curr_team[-1]].skillLevel)
                # check if at least 1 possible trainers exist
                if possible_trainers:
                    final_team = TempMatch(curr_team, self.date, possible_trainers)
                    return final_team

        return final_team

    @staticmethod
    def match_exists(matches, curr_team):
        for match in matches:
            if match.player == curr_team:
                return True
        return False

    # Finds a match for a specific player
    def find_match(self, matches, curr_player_index):
        """
        finds a match for the current player, while considering all necessary constraints

        :param matches: matches that have already been chosen
        :param curr_player_index: index of current player to find match for
        :return: the legitimate match that has been found, None otherwise
        """

        # find the matchable players that surround the current player
        lowest_player_index = self.find_lowest_teampartner(curr_player_index)
        highest_player_index = self.find_highest_teampartner(curr_player_index)

        partition = range(lowest_player_index, highest_player_index + 1)
        """
        if (len(partition) <= 10):
            match = self.generate_match2(matches, lowest_player_index, curr_player_index, highest_player_index)

        else:
            match = self.generate_match(matches, lowest_player_index, curr_player_index, highest_player_index)

        # try to generate a match
        """
        match = self.generate_match2(matches, lowest_player_index, curr_player_index, highest_player_index)
        if match is not None:
            for player_index in match.player:
                self.PM[player_index] += 1

        return match

    # Generate all potential matches of an appointment
    def generate_matches(self, cap=FINAL_CAP, min_matches=FINAL_MIN_MATCHES):
        """
        generates cap amount of matches while trying to find at least
        min_matches for each player in this specific time slot
        :param cap: max amount of matches to be generated (can be exceeded if min_matches has not been reached)
        :param min_matches: minimum amount of matches per player
        :return: result - list of matches chosen for this timeslot
        """

        temp_result = []

        # loop to evenly distribute matches among players
        for amount in range(1, cap):
            for i in range(0, len(self.PM)):
                # checks if matches are available at all for player i
                if self.CNM[i] == 0:
                    if self.PM[i] <= amount:
                        i_match = self.find_match(temp_result, i)
                        if i_match is not None:
                            temp_result.append(i_match)
                            # checking if cap has been reached
                            if len(temp_result) >= cap and amount >= min_matches:
                                return self.generate_results(temp_result)
                        else:
                            # remove player from consideration4, because no possible match exists
                            self.CNM[i] = 1
        print("generate_matches completed")
        return self.generate_results(temp_result)

    def generate_results(self, temp_results):
        results = []
        for temp in temp_results:
            for trainer in temp.trainers:
                results.append(Match(temp.player, self.date, trainer))

        return results

    def find_skillbracket(self, player_index):
        for i in range(len(self.skill_brackets)):
            if self.skill_brackets[i][0] <= self.P[player_index].skillLevel <= self.skill_brackets[i][1]:
                return i
        return -1

    def pick_random(self, partition):

        return random.sample(range(len(partition)), self.team_size - 1)

    # this function is unused. unlike generate_match() it is not randomized, therefore more accurate, but the runtime
    # increases exponentially with the amount of players in a single skill group, therefore it should only be used in
    # specific environments
    def generate_match2(self, matches, lowest_player_index, curr_player_index, highest_player_index):
        """
        generates a not yet chosen match which is possible according to the maximal skill difference

        :param matches: matches that have already been chosen
        :param lowest_player_index: index of the lowest player still matchable
        :param curr_player_index: index of current player to search match for
        :param highest_player_index: index of the highest player still matchable
        :return: the match that satisfies all conditions, None if not one can be found
        """

        final_team = None
        # generate player range without curr player

        skill_range = list(range(lowest_player_index, highest_player_index + 1))
        skill_range.remove(curr_player_index)

        # find all possible combinations
        combination = list(combinations(skill_range, self.team_size - 1))
        random.shuffle(combination)

        # loop through combinations
        for i in range(len(combination)):
            curr_team = list(combination[i])
            # append the player that necessarily has to be part of the team

            curr_team.append(curr_player_index)
            curr_team.sort()

            # check conditions
            if self.skill_difference_allowed(curr_team[0], curr_team[-1]):
                # check if match has already been chosen
                if self.match_exists(matches, curr_team):
                    continue
                # find possible trainers
                possible_trainers = self.possible_trainers(self.P[curr_team[-1]].skillLevel)
                # check if at least 1 possible trainers exist
                if possible_trainers:
                    final_team = TempMatch(curr_team, self.date, possible_trainers)
                    return final_team

        return final_team