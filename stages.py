from TM.tournament import Tournament, TournamentRules
from TM.pairings import PlayoffPairings, RoundPairings
from calc_rating import calc_rating_selections, calc_rating_playoff


# ============ IO ================ #
def update(t: Tournament, api, round_num):
    t.read_results(api, round_num)
    print("Results imported\n".format(round_num))
    return


def set_group(t, apis, group_num):
    # Automatic file name
    t.make_pairs()
    try:
        filename = ''
        for api in apis:
            filename = t.write_pairs(api, group_num, )
        # t.pairs_to_csv(filename + '_pairs.csv')
        # t.standings_to_txt(filename + '_standings.txt')
        print("Pairs calculated, saved to file " + filename)
    except Exception as e:
        print("Failed to write to file \n" + str(e))


def set_round(t, apis, round_num=None):

    if len(t.fighters) in [8, 16, 32]:
        # Remove the fighters who lost previous playoff round
        removed = []
        for f in t.fighters:
            if f.rating < 0:
                removed.append(f)
        if len(removed) > 0:
            print('Removing fighters:')
            for f in removed:
                t.remove_fighter(f)
                print(f'{f.name}')

    t.make_pairs()
    try:
        filename = ''
        # We encode the playoff stage in the sheet ID as 10 + 4/2 = 1/2; 10+8/2 = 1/4, 10+32/2 = 1/16
        if not round_num:
            round_num = 10 + len(t.fighters) // 2

        for api in apis:
            filename = t.write_pairs(api, round_num)
        # t.pairs_to_csv(filename + '_pairs.csv')
        # t.standings_to_txt(filename + '_standings.txt')
        print("Pairs calculated, saved to file " + filename)
    except Exception as e:
        print("Failed to write to file \n" + str(e))

    return round_num

# ================================================= #
# =========== Stage definitions =================== #

def group_stage(tournaments, api):

    while True:
        command = input()
        split = command.split(' ')

        if command == 'exit':
            return
        # ignore accidental 'enter' without warnings
        elif command == '':
            continue

        elif split[0] == 'final':
            try:
                for group_num, t in enumerate(tournaments):
                    update(t, api, group_num+1)
            except Exception as e:
                print('Failed to read results. Format results correctly and try again')
                print(str(e))
                continue

            playoff = set_playoff(tournaments)
            return playoff

        elif split[0] == 'list':
            for group_num, t in enumerate(tournaments):
                print(f'Group {group_num+1}')
                print(t.list_fighters())

        else:
            print('Unknown command, only \'list\', \'final\' and \'exit\'  can be used')


def set_playoff(groups):
    print('Setting playoff')
    all_fighters = []

    for group in groups:
        # We normalize the rating on the number of fights in a group
        fighters = group.fighters
        for f in fighters:
            f.rating = f.rating/(len(fighters) - 1)

        all_fighters += fighters
    all_fighters.sort(key=lambda x: x.rating, reverse=True)

    if len(all_fighters) >= 32:
        finalists = all_fighters[:32]
    elif len(all_fighters) >= 16:
        finalists = all_fighters[:16]
    elif len(all_fighters) >= 8:
        finalists = all_fighters[:8]
    elif len(all_fighters) >= 4:
        finalists = all_fighters[:4]
    else:
        raise ValueError('We need at least 4 fighters to start the playoff!')

    print(f'Selected {len(finalists)} finalists from len{all_fighters} participants')

    # We assign each finalist a known rating depending on their position
    for position, f in enumerate(finalists):
        f.rating = len(finalists) - position


    #print(final.list_fighters())

    return finalists


def playoff_stage(finalists, api):

    playoff = Tournament(rules=TournamentRules(pairing_function=PlayoffPairings(finalists),
                                             start_rating=0,
                                             max_rating=0,
                                             min_rating=-1000,
                                             round_points_cap=8, rating_fn=calc_rating_playoff,
                                             rounds_num=1,
                                             time=90),
                       fighters=finalists)

    round_num = set_round(playoff, [api])
    while True:
        command = input()
        split = command.split(' ')

        if command == 'exit':
            return
        # ignore accidental 'enter' without warnings
        elif command == '':
            continue

        elif split[0] == 'round':
            try:
                update(playoff, api, round_num)
                if len(playoff.fighters) > 4:
                    round_num = set_round(playoff, [api])
                else:
                    finalists = playoff.fighters

                    return finalists
            except Exception as e:
                print('Failed to update round {}. Format round results correctly and try again'.format(round_num))
                print(str(e))
                continue

        elif split[0] == 'list':
            print(playoff.list_fighters())

        else:
            print('Unknown com mand, only \'list\', \'round\' and \'exit\' can be used')


def final_stage(finalists, api):
    final = Tournament(rules=TournamentRules(pairing_function=PlayoffPairings(finalists),
                                             start_rating=0,
                                             max_rating=0,
                                             min_rating=-1000,
                                             round_points_cap=8, rating_fn=calc_rating_playoff,
                                             rounds_num=3,
                                             time=90),
                       fighters=finalists)

    api.num_rounds = final.rules.rounds_num
    print(f'Final fights are: {final.fighters[0].name} vs {final.fighters[1].name}, '
          f'{final.fighters[2].name} vs {final.fighters[3].name}')
    set_round(final, [api], 100)
    return