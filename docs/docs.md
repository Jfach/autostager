Intro: 
--------

Autostager contributes to projects by forking and cloning Pull Request from project's contributor. It performs an automatic staging operation on new or existing fork from Github's Pull Request.
Instead of cloning the fork's data manually from Github, Autostager will draw fork's data from Github and stage in base directory at local machine. It also allows maintainer to test and merge branches.  
Imagine you are collobrating with 80 contributors in a project, Autostager does the work for you.

However if contributor "A"  forked a repo but did not initiate any Pull Request, Autostager would not be able to stage any data from Contributor "A". 


How does Autostager works:  
--------
#####include function from autostager.py
1. call out to github APl (Pull Request)
2. for each pull request, clone each fork and its branch   
3. stage each fork and it's branch in to a directory  
⋅⋅ if the fork is already staged(exist)  
⋅⋅ ->	 fetch and rebase the fork   
⋅⋅ else  
⋅⋅ -> 	 repeat step 2  
*Step3 acts as loop to look for new and existing fork<br> 

Procedure:  
---------
#####For Maintainer
Follow (procedure) [ https://help.github.com/articles/creating-an-access-token-for-command-line-use/] to generate token for CLI use Autostager
```
export access_token=<your_token>
export repo_slug=<path of repo in github>
export base_dir=<Directory Pull Request get stage>
```
#####For contributor:
```	
git remote add <url of maintainer's repo><br>
git remote -v <br>
``` 	

example:
```
	gary@gary-HP-2000-Notebook-PC:~/Desktop/testrepo$ git remote -v 
	origin	https://github.com/Garysoccer/testrepo.git (fetch) #contributor
	origin	https://github.com/Garysoccer/testrepo.git (push)
	upstream  https://github.com/jfach/testrepo.git (fetch) #maintainer	
	upstream  https://github.com/jfach/testrepo.git (push)

```
Sync fork with Maintainer' Branch 
----------
Ensure github3 version is 0.9.3
```
pip install --pre github3.py

```
Sync Fork with Maintainer's Master Branch
--------
```
$git remote -v #check for Maintainer's remote URL. 
$git remote add upstream <https://github.com/maintainer's URL> 
$git checkout <master>
$git rebase <master>
$git fetch upstream
$git rebase upstream/master
$git push --force

```



