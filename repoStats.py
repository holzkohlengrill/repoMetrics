import gitlab
import pypiscout as sc
import pandas
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer

from constants_settings import *


def main():
    gl = authenticate()
    project = getProject(gl)

    # Issues
    issueData = issuesAnalysis(project)
    issueData.to_csv(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "issueData.csv"), sep=";")

    # Commits
    commitData = commitAnalysis(project)
    commitData.to_csv(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "commitData.csv"), sep=";")

    # plt.show()


def issuesAnalysis(project):
    ##############################
    # Issues
    ##############################
    issueList = getIssuesAsList(project)
    issueData = pandas.DataFrame(issueList)

    # Convert date to datetime format
    issueData[LabelsIssue.created_at] = pandas.to_datetime(issueData[LabelsIssue.created_at], format="%Y-%m-%dT%H:%M:%S", utc=True)
    issueData[LabelsIssue.closed_at] = pandas.to_datetime(issueData[LabelsIssue.closed_at], format="%Y-%m-%dT%H:%M:%S", utc=True)
    issueData[LabelsIssue.due_date] = pandas.to_datetime(issueData[LabelsIssue.due_date], format="%Y-%m-%d", utc=True)

    # Add dates as calendar weeks
    issueData[LabelsIssue.created_at_CW] = issueData[LabelsIssue.created_at].dt.week
    issueData["created_at_year"] = issueData[LabelsIssue.created_at].dt.year

    issueData[LabelsIssue.closed_at_CW] = issueData[LabelsIssue.closed_at].dt.week
    issueData["closed_at_year"] = issueData[LabelsIssue.closed_at].dt.year

    ##############################
    # Opened issues per CW (stacked: closed/opened (which one are already opened/closed))
    cwIssuesOpenedGrouped = issueData[["created_at_year", LabelsIssue.created_at_CW, LabelsIssue.state]].groupby(["created_at_year", LabelsIssue.created_at_CW, LabelsIssue.state])[LabelsIssue.created_at_CW].count().unstack()
    ax_cwIssuesOpenedGrouped = cwIssuesOpenedGrouped.plot(kind='bar', stacked=True, cmap='Pastel2')
    ax_cwIssuesOpenedGrouped.set_title("Opened issues per CW (opened/closed)")
    plt.tight_layout()
    # plt.gcf().subplots_adjust(bottom=0.13)
    ax_cwIssuesOpenedGrouped.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "cwIssuesOpenedGrouped.png"), dpi=300)

    ##############################
    # Closed issues per CW
    cwIssuesClosedGrouped = issueData[["closed_at_year", LabelsIssue.closed_at_CW, LabelsIssue.state]].groupby(["closed_at_year", LabelsIssue.closed_at_CW, LabelsIssue.state])[LabelsIssue.closed_at_CW].count().unstack()
    ax_cwIssuesClosedGrouped = cwIssuesClosedGrouped.plot(kind='bar', stacked=True, cmap='Accent')
    ax_cwIssuesClosedGrouped.set_title("Closed issues per CW")
    # plt.gcf().subplots_adjust(bottom=0.13)
    plt.tight_layout()
    ax_cwIssuesClosedGrouped.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "cwIssuesClosedGrouped.png"), dpi=300)

    ##############################
    # Issues per label (multiple issues per label are counted multiple times)
    # Expand labels to columns
    mlb = MultiLabelBinarizer()
    expandedLabelData = mlb.fit_transform(issueData[LabelsIssue.labels])
    labelClasses = mlb.classes_
    # Add labels to dataframe
    expandedLabels = pandas.DataFrame(expandedLabelData, columns=labelClasses)
    expandedLabels.columns = expandedLabels.add_prefix("label_").columns.str.replace(" ", "_")
    issueData = pandas.concat([issueData, expandedLabels], axis=1)

    ##############################
    # Plot issues per label/team
    # labels = set([label for sublist in issueData[LabelsIssue.labels] for label in sublist])
    # issuesPerTeam = issueData[[*labels]].sum()
    if activateTeamLabels:
        issuesPerTeam = issueData[[*teamLabels]].sum()
        plt.figure()
        ax_issuesPerTeam = issuesPerTeam.plot.bar(cmap='Pastel2')
        ax_issuesPerTeam.set_title("Issues per label (count = label_count_per_issue * all_issues)")
        plt.gcf().subplots_adjust(bottom=0.3)
        ax_issuesPerTeam.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "issuesPerLabel.png"), dpi=300)

    ##############################
    # Issues per milestone
    issueData['milestone_title'] = issueData['milestone'].apply(lambda x: x.get('title') if x is not None else None)
    # issueData['milestone_title'] = issueData[Labels.milestone].apply(lambda x: x['title'])
    issuesPerMilestone = issueData.groupby([LabelsIssue.state, 'milestone_title'])[LabelsIssue.state].count().unstack()
    issuesPerMilestone.plot(kind='barh', subplots=True, stacked=True, legend=False, cmap='Pastel2', figsize=(7, 5))
    # plt.gcf().subplots_adjust(left=0.03, bottom=0.12, right=0.99, top=0.92)
    plt.tight_layout()
    plt.gcf().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "issuesPerMilestone.png"), dpi=300)

    ##############################
    # Delta closed - open
    issueDataReduced = issueData.copy()
    # Scatter iid
    issueDataReduced['deltaClosedOpen'] = (issueDataReduced[LabelsIssue.closed_at] - issueDataReduced[LabelsIssue.created_at]).dt.days
    issueDataReduced.dropna(axis=0, inplace=True, subset=['deltaClosedOpen'])
    ax_deltaClosedOpenScatter = issueDataReduced[['deltaClosedOpen', LabelsIssue.iid]].plot(kind='scatter', x=LabelsIssue.iid, y='deltaClosedOpen')
    ax_deltaClosedOpenScatter.set_title("Issue lifetime | Delta = Closed - Open [days]")
    ax_deltaClosedOpenScatter.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "deltaClosedOpenScatter.png"), dpi=300)

    # Scatter CW
    ax_deltaClosedOpenScatterCW = issueDataReduced[['created_at_year', 'deltaClosedOpen', LabelsIssue.created_at_CW]].set_index(['created_at_year', LabelsIssue.created_at_CW]).plot(style=".")
    ax_deltaClosedOpenScatterCW.set_title("Issue lifetime | Delta = Closed - Open [days]")
    ax_deltaClosedOpenScatterCW.invert_xaxis()
    ax_deltaClosedOpenScatterCW.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "deltaClosedOpenCWScatter.png"), dpi=300)

    # Histogram
    ax_deltaClosedOpenHist = issueDataReduced[['deltaClosedOpen']].plot(kind='hist')
    ax_deltaClosedOpenHist.set_title("Issue lifetime | Delta = Closed - Open [days]")
    ax_deltaClosedOpenHist.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "deltaClosedOpenHist.png"), dpi=300)

    # Box plot
    ax_deltaClosedOpenBox = issueDataReduced[['deltaClosedOpen']].plot(kind='box')
    ax_deltaClosedOpenBox.set_title("Issue lifetime | Delta = Closed - Open [days]")
    ax_deltaClosedOpenBox.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "deltaClosedOpenBox.png"), dpi=300)

    # Kde plot
    ax_deltaClosedOpenKde = issueDataReduced[['deltaClosedOpen']].plot(kind='kde')
    ax_deltaClosedOpenKde.set_title("Issue lifetime | Delta = Closed - Open [days]")
    ax_deltaClosedOpenKde.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "deltaClosedOpenKde.png"), dpi=300)
    return issueData


def commitAnalysis(project):
    ##############################
    # Commits
    ##############################
    commitList = getCommitsAsList(project)
    commitData = pandas.DataFrame(commitList)
    # For testing: dump to csv in order to save time to play around with the plots
    # commitData.to_csv("./blub.csv")
    # commitData = pandas.read_csv("./blub.csv")
    # Convert date to datetime format
    commitData[LabelsCommits.created_at] = pandas.to_datetime(commitData[LabelsCommits.created_at], format="%Y-%m-%dT%H:%M:%S", utc=True)
    commitData[LabelsCommits.authored_date] = pandas.to_datetime(commitData[LabelsCommits.authored_date], format="%Y-%m-%dT%H:%M:%S", utc=True)
    commitData[LabelsCommits.committed_date] = pandas.to_datetime(commitData[LabelsCommits.committed_date], format="%Y-%m-%dT%H:%M:%S", utc=True)
    commitData['commitedDay'] = commitData[LabelsCommits.committed_date].dt.date
    commitData['commitedCW'] = commitData[LabelsCommits.committed_date].dt.strftime('%Y-%U')

    ax_commitsScatter = commitData.groupby(['commitedDay']).count().plot(kind='line', rot=90, legend=False, cmap='Pastel2', figsize=(7, 5))
    ax_commitsScatter.set_title("Line plot | commit history [commits/day]")
    plt.tight_layout()
    plt.gcf().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "commitsScatter.png"), dpi=300)

    commitData.reset_index()
    ax_commitsHist = commitData[['commitedDay', LabelsCommits.id]].groupby(['commitedDay']).count().plot(kind='hist', legend=False)
    ax_commitsHist.set_title("Histogram | commit count per day")
    ax_commitsHist.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "commitsHist.png"), dpi=300)

    commitData.reset_index()
    ax_commitsBox = commitData[['commitedDay', LabelsCommits.id]].groupby(['commitedDay']).count().plot(kind='box')
    ax_commitsBox.set_title("Box plot | commit count per day")
    ax_commitsBox.get_figure().savefig(os.path.join(IMAGE_ROOT_FOLDER, DATE_PREFIX + "commitsBox.png"), dpi=300)
    return commitData


def authenticate():
    gl = gitlab.Gitlab(URL, private_token=TOKEN, timeout=99999)
    gl.auth()           # Authenticate
    return gl


def getProject(gl):
    project = gl.projects.get(PROJECT_ID, lazy=True)
    return project


def getIssuesAsList(project):
    allIssues = project.issues.list(all=True, lazy=True)
    issueLst = []

    for issue in allIssues:
        issueLst.append(issue.attributes)
    sc.info(str(len(allIssues)) + " issues found")
    return issueLst


def getCommitsAsList(project):
    branches = project.branches.list()
    branchLst = []
    for branch in branches:
        branchLst.append(branch.attributes['name'])

    commitLst = []

    allCommits = project.commits.list(all=True, lazy=True, with_stats=True)
    for issue in allCommits:
            commitLst.append(issue.attributes)
    sc.info(str(len(allCommits)) + " commits found")

    # Not needed (`all=True` give commits from each and every branch); still here for documentation

    # for branchName in branchLst:
    #     allCommits = project.commits.list(all=True, lazy=True, ref_name=branchName, with_stats=True)
    #     print(str(len(allCommits)) + " commits found for branch: " + branchName)
    #     for issue in allCommits:
    #         issue.attributes.update({'branch': branchName})
    #         commitLst.append(issue.attributes)
    # sc.info(str(len(allCommits)) + " commits found")
    return commitLst


if __name__ == '__main__':
    sc.info("Started Repository Statistics Analyser (ReStA)")
    main()
