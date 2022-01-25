import copy
import csv
import random


class Person():
    def __init__(self, name, email, grad_year, gender, prefs, team):
        self.name = name
        self.email = email
        self.grad_year = grad_year
        self.gender = gender
        self.prefs = prefs
        self.team = team

        # created group number to identify people with same/different demographic group more quickly
        if grad_year == "2025":
            if gender == "male":
                self.group_number = 0
            else:
                self.group_number = 1
        elif grad_year == "2024":
            if gender == "male":
                self.group_number = 2
            else:
                self.group_number = 3
        elif grad_year == "2023":
            if gender == "male":
                self.group_number = 4
            else:
                self.group_number = 5
        else:
            if gender == "male":
                self.group_number = 6
            else:
                self.group_number = 7

    # use emails to determine if people are the same
    def __eq__(self, other):
        myName = self.email
        hisName = other.email
        if  myName == hisName:
            return True
        else:
            return False

    def print(self):
        return self.name + ", " + self.email


people = []
data = []

file = open('dmdata.csv')
type(file)
csvreader = csv.reader(file)
for i in csvreader:
    data.append(i)

data.pop(0)  # first row was column headers

# these indices are all hard-coded for the spreadsheet we were using

for i in data:
    name = i[3] + " " + i[4]
    email = i[41]
    grad_year = i[66]
    gender = i[73]
    prefs = []
    for j in range(84, 89):
        if i[j] != '':  # not all people used all of their prefs
            prefs.append(i[j])
    team = i[89]
    people.append(Person(name, email, grad_year, gender, prefs, team))

people_dict = {}
for i in people:
    people_dict[i.email] = i

teams = [[], [], [], []]

for i in range(len(people)):
    teams[int(people[i].team) - 1].append(people[i])  # put everyone in their initial team

# This is the main part of the algorithm, this function is run over 500 iterations to get the best teams
    # Starts by choosing a random demographic group (e.g freshman boy, senior girl) and two random teams
    # The function then chooses everyone on each of the two teams who fall under the chosen demographic
    # The function then attempts every possible swap between these two "sub-teams" and keeps the best one
    # The way we determined the best swap was by creating a scoring system
    # Each person got a score based on how many preferences were on their team, and the total score was the sum

def swap_teams(teams):
    new_teams = copy.deepcopy(teams)
    group = random.choice(range(8))
    team1, team2 = random.sample(range(4), 2)
    sub_team1, sub_team2 = [], []

    # create sub-teams

    for i in teams[team1]:
        if i.group_number == group:
            sub_team1.append(i)
    for i in teams[team2]:
        if i.group_number == group:
            sub_team2.append(i)

    # initialize best_team_score and best_team to current state

    best_team_score = calculate_score(teams)
    best_team = teams

    # This nested loop goes through all swaps and only retains the swap if it is

    for a in range(len(sub_team1)):
        for b in range(len(sub_team2)):
            new_teams = copy.deepcopy(teams)
            new_teams[team1].append(sub_team2[b])
            new_teams[team2].append(sub_team1[a])

            new_teams[team1].remove(sub_team1[a])
            new_teams[team2].remove(sub_team2[b])

            new_teams_score = calculate_score(new_teams)
            if (best_team_score < new_teams_score):
                best_team = copy.deepcopy(new_teams)

                # At the beginning, there are many swaps that increase score
                # We didn't think it was efficient to check every swap at this stage so we set a threshold
                # where if the score increased by enough, we would simply use that swap

                if (best_team_score <= new_teams_score - 5):
                    return best_team
                best_team_score = new_teams_score
    return best_team


max_score = 0
more = []

# This was our scoring system, the first index corresponds to how many preferences the person got
# The second index is total number of preferences
# We did not experiment a lot with this due to time-pressure, so feel free to tweak the scoring but make sure to scale
# the threshold in the swap_teams function

score_array = [["nil" for i in range(6)] for j in range(6)]
score_array[0][0] = 0
score_array[0][1] = -2
score_array[1][1] = 5
score_array[0][2] = -3
score_array[1][2] = 6.8
score_array[2][2] = 7.5
score_array[0][3] = -4
score_array[1][3] = 5.5
score_array[2][3] = 7.2
score_array[3][3] = 7.75
score_array[0][4] = -4.5
score_array[1][4] = 4.5
score_array[2][4] = 6.8
score_array[3][4] = 7.4
score_array[4][4] = 7.90
score_array[0][5] = -5
score_array[1][5] = 4
score_array[2][5] = 6
score_array[3][5] = 7
score_array[4][5] = 7.75
score_array[5][5] = 8

# This function found each individual person's score and summed them up to get a total score

def calculate_score(teams):
    global max_score
    score = 0
    pref_counter = 0
    for i in range(4):
        for j in range(len(teams[i])):
            pref_counter = 0
            for k in range(len(teams[i][j].prefs)):
                if teams[i][j].prefs[k] in people_dict and people_dict[teams[i][j].prefs[k]] in teams[i]:
                    pref_counter += 1
            score += score_array[pref_counter][len(teams[i][j].prefs)]
    return score

swaps = 0

# We ran swap teams 500 times but ran into timeout errors when increasing this number
# As we ran more and more iterations the algorithm started to stagnate, but we did run it on the Northwestern Moore
# machine for about 10,000 iterations with slightly better results

for i in range(500):
    print("current iteration: " + str(i) + "\n")
    teams = copy.deepcopy(swap_teams(teams))

# This prints each team after all swaps are done

for i in range(len(teams)):
    teams[i].sort(key=lambda x: x.name)
    print("Team " + str(i + 1))
    for j in teams[i]:
        print(j.print())
    print("\n")

# This prints each person with their prefs

for i in range(len(teams)):
    print("Team " + str(i + 1) + "\n")
    for j in range(len(teams[i])):
        prefs = 0
        for k in range(len(teams[i][j].prefs)):
            if teams[i][j].prefs[k] in people_dict and people_dict[teams[i][j].prefs[k]] in teams[i]:
                prefs += 1
        if prefs == 0 and len(teams[i][j].prefs) > 0:
            more.append(teams[i][j])
        print(str(teams[i][j].name) + ": " + str(prefs) + "/" + str(len(teams[i][j].prefs)) + "\n")

# This puts the new teams into an array

new_people = []
for i in range(len(teams)):
    for j in range(len(teams[i])):
        new_people.append(teams[i][j])

print(people.sort(key=lambda x: x.name) == new_people.sort(key=lambda x: x.name))

# Last print statement confirms that the original teams have the same people as the new teams (no dup or missing person)
