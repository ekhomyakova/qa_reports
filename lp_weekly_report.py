import os
import copy
import datetime
from prettytable import PrettyTable
from launchpadlib.launchpad import Launchpad

project = os.getenv('LAUNCHPAD_PROJECT')
team_name = os.getenv('LAUNCHPAD_TEAM')
additional_team = os.getenv('LAUNCHPAD_TEAM_2', None)
milestone = os.getenv('LAUNCHPAD_MILESTONE', None)
tags = os.getenv('LAUNCHPAD_TAGS', None)
one_week_ago_date = datetime.datetime.now() - datetime.timedelta(weeks=1)

cachedir = "~/.launchpadlib/cache/"
launchpad = Launchpad.login_anonymously('just testing', 'production', cachedir)
lp_team = launchpad.people(team_name).members_details
lp_project = launchpad.projects(project)

table = PrettyTable(["Title", "Milestone", "Importance", "Status", "Assigned To", "Link"])
table.padding_width = 1 # One space between column edges and contents (default)
table.align["Title"] = "l"

def trim_milestone(milestone):
    return str(milestone).replace('https://api.launchpad.net/1.0/fuel/+milestone/', '')

def get_lp_bugs(**kwargs):
    table_lp = copy.deepcopy(table)
    counter = 0
    for people in lp_team:
        p = launchpad.people[people.member.name]
        bug_list = p.searchTasks(assignee=p, **kwargs)
        for bug in bug_list:
            table_lp.add_row([bug.title, trim_milestone(bug.milestone), bug.importance, bug.status, bug.assignee.name, bug.web_link])
            counter += 1
    # + bugs assigned to whole team
    team = launchpad.people[team_name]
    team_bugs = team.searchTasks(assignee=team, **kwargs)
    for bug in team_bugs:
        table_lp.add_row([bug.title, trim_milestone(bug.milestone), bug.importance, bug.status, bug.assignee.name, bug.web_link])
        counter += 1
    if additional_team is not None:
        team2 = launchpad.people[additional_team]
        team2_bugs = team2.searchTasks(assignee=team2, **kwargs)
        for bug in team2_bugs:
            table_lp.add_row([bug.title, trim_milestone(bug.milestone), bug.importance, bug.status, bug.assignee.name, bug.web_link])
            counter += 1
    return table_lp, counter

print "\n\n\nList of bugs found during the last week\n"
tbl, counter = get_lp_bugs(created_since=one_week_ago_date, milestone=milestone, tags=tags)
print tbl.get_string(sortby="Importance")
print "Total bugs found during the last week: {0}".format(counter)

print "\n\n\nList of bugs verified during the last week\n"
tbl, counter = get_lp_bugs(modified_since=one_week_ago_date, status='Fix Released', milestone=milestone, tags=tags)
print tbl.get_string(sortby="Importance")
print "Total bugs verified during the last week: {0}".format(counter)

print "\n\n\nList of bugs that need to be fixed:\n"
tbl, counter = get_lp_bugs(status=['New', 'Incomplete', 'Triaged', 'Confirmed', 'In Progress'], milestone=milestone, tags=tags)
print tbl.get_string(sortby="Status")
print "Total bugs need to be fixed: {0}".format(counter)

print "\n\n\nList of bugs that need to be verified\n"
tbl, counter = get_lp_bugs(status='Fix Committed', milestone=milestone, tags=tags)
print tbl.get_string(sortby="Importance")
print "Total bugs need to be verified: {0}".format(counter)
