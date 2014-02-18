svn-smf-hook
============

SVN post-commit hook script postig commit info to Simple Machines Forum

You can use this script as post-commit hook of your svn repo,
and it'll announce each commit as new topic on selected boards,
designed to work with Simple Machines Forums.

The arguments are the default arguments accepted by svn post-commit hook:

~~~
./svn-smf-hook.py path-to-repo revision
~~~

Tested with SMF 2.0.6

NOTE: Even though this script features Trac integration, it does not work as Trac's post-commit hook. To have your tickets in Trac updated on commit, use the Trac svn hook together with this script. Read: http://trac.edgewall.org/wiki/TracRepositoryAdmin#Subversion

Before you deploy this as hook, make sure to properly configure it in *svn-smf-hook.conf* file.

The post produced by this hook will look roughly like this:

=

user_56 made revision 12185 changing the following files:

~~~
modified  /trunks/project/readme.txt
~~~
with the message:

~~~
update readme
~~~

=

The idea for this hook came from similiar hook for another forum software, by [FH]ctz.
