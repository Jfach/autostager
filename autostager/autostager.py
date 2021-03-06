import os
import re
import shutil
import socket
import time
import github3
import logger
import pull_request
from timeout import timeout
import utils

class Autostager():

    def __init__(self):
        slug = self.repo_slug().split('/')
        self.owner = slug[0]
        self.repo = slug[1]
        #self.access_token = os.environ.get('access_token')
    
    def access_token(self):
        return os.environ['access_token']

    def alphafy(self, a_string):
        pattern = "[^a-z0-9_]"
        return re.sub(pattern, "_", a_string, flags=re.IGNORECASE)


    def stage_upstream(self):
        print "========================="
        print "      STAGE UPSTREAM     "
        print "========================="
        default_branch = self.client().repository(self.owner, self.repo).default_branch
        logger.log("===> begin {0}".format(default_branch))
        p = pull_request.PullRequest(
            default_branch,
            self.authenticated_url("https://github.com/{0}".format(self.repo_slug())),
            self.base_dir(),
            default_branch,
            self.authenticated_url("https://github.com/{0}".format(self.repo_slug()))
        )
        if not p.staged():
            p.clone()
            p.fetch()
        if p.rebase() == 0:
            return
        self.client().repository(self.owner, self.repo).create_issue(
            "Failed to fast-forward {0} branch".format(default_branch),
            ":bangbang: This probably means somebody force-pushed to the branch."
        )

    def process_pull(self, pr):
        print "========================="
        print "       PROCESS PULL      "
        print "========================="
        print "Proccessing {0}".format(pr.head.label)
        logger.log("===> {0} {1}".format(pr.number, self.staging_dir(pr)))
        p = pull_request.PullRequest(
            pr.head.ref,
            self.authenticated_url(pr.as_dict()['head']['repo']['clone_url']),
            self.base_dir(),
            self.clone_dir(pr),
            self.authenticated_url(pr.as_dict()['base']['repo']['clone_url']))
        if p.staged():
            p.fetch()
            if pr.head.sha != p.local_sha():
                print "calling p.reset_hard()..."
                p.reset_hard()
                add_comment = True
            else:
                logger.log("nothing to do on {0} {1}".format(pr.number, self.staging_dir(pr)))
                add_comment = False
            print "Calling p.rebase()..."
            p.rebase()
            self.comment_or_close(p, pr, add_comment)
        else:
            p.clone()
            # check to see if its behind upstream (in the case of a reopened PR) TODO
            # what happens when someone reopens a closed pull request:
            # - the pr gets staged
            # - on the next run, the pr is unstaged and closed due to still being x commits behind
            # we want to close the pr after its opened again if it was originally closed for being x commits behind
            # we need to do this in this block, i believe 
            self.comment_or_close(p, pr)

    def comment_or_close(self, p, pr, add_comment = True):
        print "========================="
        print "    COMMENT OR CLOSE     "
        print "========================="
        default_branch = pr.as_dict()['base']['repo']['default_branch']
        if p.up2date("upstream/{0}".format(default_branch)):
            print pr.head.label + " is up to date"
            if add_comment:
                comment = ":bell: Staged `{0}` at revision {1} on {2}"
                comment = comment.format(self.clone_dir(pr), p.local_sha(), socket.gethostname())
                pr.create_comment(comment)
                logger.log(comment)
        else:
            comment = ":boom: Unstaged since {0} is dangerously behind upstream"
            comment = comment.format(self.clone_dir(pr))
            shutil.rmtree(self.staging_dir(pr))
            pr.create_comment(comment)
            pr.close()
            logger.log(comment)


    def authenticated_url(self, url):
        return re.sub(r"(^https://)", "https://" + self.access_token() + "@", url)


    def base_dir(self):
        return os.environ.get('base_dir') or '/opt/puppet/environments'


    def clone_dir(self, pr):
        return self.alphafy(pr.head.label)


    def staging_dir(self, pr):
        return os.path.join(self.base_dir(), self.clone_dir(pr))


    def repo_slug(self):
        return os.environ.get('repo_slug') # handle None return value if key does not exist?


    def client(self):
        return github3.login(token=self.access_token())


    def timeout_seconds(self):
        result = 120
        if os.environ.get('timeout'):
            result = int(os.environ['timeout'])
            assert result > 0, "timeout must be greater than zero seconds"
        return result


    def safe_dirs(self):
        return ['.', '..', 'master']

    def run(self):
        print utils.art
        self.client()
        self.stage_upstream()
        prs = self.client().repository(self.owner, self.repo).pull_requests()
        new_clones = [self.clone_dir(pr) for pr in prs]
        if os.path.exists(self.base_dir()):
            discard_dirs = set(os.listdir(self.base_dir())) - set(self.safe_dirs()) - set(new_clones)
            discard_dirs = list(discard_dirs)
            discard_dirs = [os.path.join(self.base_dir(), d) for d in discard_dirs]
            for discard_dir in discard_dirs:
                logger.log("===> Unstage {0} since PR is closed.".format(discard_dir))
                shutil.rmtree(discard_dir) 

        with timeout(self.timeout_seconds()):
            for pr in prs:
                self.process_pull(pr)

if __name__ == "__main__":
    if os.environ.get('refresh_time'):
    	refresh_time = int(os.environ['refresh_time'])
    else:
    	refresh_time = 30
    autostager = Autostager()
    while True:
    	autostager.run()
	time.sleep(refresh_time)
