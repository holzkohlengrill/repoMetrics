import datetime
import os

####################################################################################
# Config
####################################################################################
TOKEN = r'Jiut-yH69masdfghzUklasfNc'         # token name: issue-analysis
PROJECT_ID = r'25328'
URL = r'https://gitlab.com/'

teamLabels = ['label_3D-Modelling', 'label_Blueprint', 'label_KI', 'label_Lvl_Design']      # Add your labels for team assignment and set activateTeamLabels to True
activateTeamLabels = True

IMAGE_ROOT_FOLDER = './images'
DATE = datetime.datetime.now().strftime("%Y-%m-%d_-_%Hh%Mm%S")
DATE_PREFIX = DATE + "_-_"
SET_SUBDIR = True                       # create a subdir for each run


####################################################################################
# Constants
####################################################################################

if SET_SUBDIR:
    SUBDIR = "repo-images_-_" + DATE
    IMAGE_ROOT_FOLDER = os.path.join(IMAGE_ROOT_FOLDER, SUBDIR)
    os.mkdir(IMAGE_ROOT_FOLDER)


class LabelsIssue:
    assignee = 'assignee'
    assignees = 'assignees'
    author = 'author'
    closed_at = 'closed_at'
    closed_by = 'closed_by'
    confidential = 'confidential'
    created_at = 'created_at'
    description = 'description'
    discussion_locked = 'discussion_locked'
    downvotes = 'downvotes'
    due_date = 'due_date'
    id = 'id'
    iid = 'iid'                                         # Ticket number
    labels = 'labels'
    milestone = 'milestone'
    project_id = 'project_id'
    state = 'state'                                     # Opened/Closed
    time_stats = 'time_stats'
    title = 'title'
    updated_at = 'updated_at'
    upvotes = 'upvotes'
    user_notes_count = 'user_notes_count'
    web_url = 'web_url'
    created_at_CW = 'created_at_CW'
    closed_at_CW = 'closed_at_CW'


class LabelsCommits:
    author_email = 'author_email'
    author_name = 'author_name'
    authored_date = 'authored_date'
    committed_date = 'committed_date'
    committer_email = 'committer_email'
    committer_name = 'committer_name'
    created_at = 'created_at'
    id = 'id'
    message = 'message'
    parent_ids = 'parent_ids'
    project_id = 'project_id'
    short_id = 'short_id'
    title = 'title'
