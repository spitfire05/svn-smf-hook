svn-smf-hook
============

## Description

SVN post-commit hook script postig commit info to Simple Machines Forum

You can use this script as post-commit hook of your svn repo,
and it'll announce each commit as new topic on selected boards,
designed to work with [Simple Machines Forum](http://www.simplemachines.org/).

The arguments are the default arguments accepted by svn post-commit hook:

~~~
./svn-smf-hook.py path-to-repo revision
~~~

Tested with SMF 2.0

## Installation

Just download *svn-smf-hook.py* and *svn-smf-hook.conf* files and place it in your *hooks* folder. Then configure the script and run it from *post-commit* script.

### Example *post-commit* file

``` sh
#!/bin/sh

REPO=/path/to/your/repo
/usr/bin/env python $REPO/hooks/svn-smf-hook.py $1 $2
```

## Configuration

Before you deploy this as hook, make sure to properly configure it in *svn-smf-hook.conf* file. Config options are documented in conf file.

## Trac integration

**svn-smf-hook** features [Trac](http://trac.edgewall.org/) integration. You can enable it by setting TRAC_URL config option to the url of your Trac installation.

With Trac integration enabled, the revision number, changed files and all ticket references in commit message (for example: *ticket #1234*) will be converted into links to their Trac pages.

### Note

Even though this script features Trac integration, it does not work as Trac's post-commit hook. To have your tickets in Trac updated on commit, use the Trac svn hook together with this script. Read: http://trac.edgewall.org/wiki/TracRepositoryAdmin#Subversion

## Example forum post

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

## Credits

The idea for this hook came from similiar hook for another forum software, by [FH]ctz.
