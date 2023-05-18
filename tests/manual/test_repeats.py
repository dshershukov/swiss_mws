from random import randint, choice
from TM.tournament import Tournament, Fighter, Fight, FightStatus, TournamentRules
from TM.tournament.tournament import find_fighters
from TM.pairings import SwissPairings
import numpy as np

# Tournament size varaints
MIN_FIGHTERS = 8
MAX_FIGHTERS = 40

#Default (maximum) hp of a fighter
MAX_HP = 20
# Fight cap - maximum lost HP in a fight
CAP = 5


class ProxyApi:
    def __init__(self, cap):
        self.all_fights = []
        self.cap = cap
        self.pairs = []
        self.fighters = []

    def write(self,
              pairs,
              fighters,
              round_num: int,
              stage_name: str):
        self.pairs = pairs
        self.fighters = fighters

    def read(self, round_num):
        """
        Generates a random results, where one of the pair receives -cap, and the other a random number from -cap+1 to 0

        :param round_num: Not used here, inherited from interface
        :return: results as a list of tuples (fighter1, points1, fighter2, points2)
        """
        results = []
        for pair in self.pairs:
            res = [-self.cap, randint(-self.cap, 0)]
            if randint(0, 1) == 0:
                res = [res[1], res[0]]
            pair.rating_score_1 = res[0]
            pair.rating_score_2 = res[1]
            pair.status = FightStatus.finished
            results.append(pair)
        self.all_fights.append(results)
        return results


def remove(tournament: Tournament, v=True):
    """
    moves the fighters with negative score out of the list
    One lucky can stand if there is need for the additional fighter to complete the even number
    :return:
    """
    new_outs = []
    minHP = tournament.fightCap

    for f in tournament.fighters:
        if f.rating <= 0:
            new_outs.append(f)
        else:
            minHP = min(minHP, f.rating)

    # If there 6 fighters or less, we can make finals:
    if len(tournament.fighters) - len(new_outs) <= 2:
        finalists = [f for f in tournament.fighters if f.rating > 0]
        candidates = [f for f in tournament.fighters if f.rating <= 0]
        if v:
            print("We need to setup an additional round to choose finalists.",
                  "Ready finalists are:")

            print(finalists)
            print('Candidates for additional round:')
            print(candidates)
        return finalists, candidates
    elif len(tournament.fighters) - len(new_outs) <= 6:
        finalists = [f for f in tournament.fighters if f.rating > 0]
        if v:
            print("We have the finalists:")
            print(finalists)
        return finalists, []

    # We leave one lucky fighter from the list if there is uneven number left.
    # TODO: add coefficient to determine the lucky one.
    elif (len(tournament.fighters) - len(new_outs)) % 2 != 0:
        lucky = choice(new_outs)
        if v:
            print('Lucky one: {}'.format(lucky))
        lucky.rating = minHP
        new_outs.remove(lucky)

    for f in new_outs:
        tournament.remove_fighter(f)


def conduct_tournament(pairing_function, fighters_num, hp, cap):
    rules = TournamentRules(max_rating=0, min_rating=-cap, pairing_function=pairing_function, start_rating=hp)
    fighters = [Fighter(fighter_id=str(i), last_name='', first_name=str(i), rating=hp) for i in range(fighters_num)]
    tour = Tournament(fighters=fighters, rules=rules)
    api = ProxyApi(cap=cap)

    repeats = 0
    differences = []
    r = 0
    while remove(tour, v=False) is None:
        tour.make_pairs()
        # test no repeated fights - the only thing we really need here
        for p in tour.pairings:
            fighter1, fighter2 = find_fighters(p, tour.fighters)
            differences.append(np.abs(fighter1.rating - fighter2.rating))
            for fight in fighter1.fights:
                if p.repeats(fight):
                    repeats += 1
        tour.write_pairs(api, r)
        tour.read_results(api, r)
        r += 1
    return repeats//2, differences


def test_repeats_and_difference():
    """with low max_diff parameters which should ensure lower difference between fighters,
    but can lead to more repeats
    """
    attempts = 100
    MIN_FIGHTERS, MAX_FIGHTERS = 20, 21
    for max_diff in range(1,9):
        for fighters_num in range(MIN_FIGHTERS, MAX_FIGHTERS, 4):
            total_repeats = 0
            total_diffs = []
            for run in range(attempts):
                repeats, diffs = conduct_tournament(pairing_function=SwissPairings(candidates_to_keep=10, max_diff=max_diff),
                                          fighters_num=fighters_num, hp=35, cap=9)
                total_repeats += repeats
                total_diffs += diffs
            rel_repeats = total_repeats / (attempts)
            print(f'Fighters: {fighters_num}; Diff: {max_diff}')
            print(f'{rel_repeats} avg repeats per run;'
                  f' {np.mean(total_diffs)} avg rating diff,'
                   f'{np.max(total_diffs)} max rating diff,'
                   f' {np.median(total_diffs)} median rating diff')