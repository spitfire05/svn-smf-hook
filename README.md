svn-smf-hook
============

## Description

[Subversion](https://subversion.apache.org/) post-commit hook script posting commit info to [Simple Machines Forum](http://www.simplemachines.org/)

You can use this script as post-commit hook of your svn repo,
and it'll announce each commit as new topic on selected boards.

Tested to be compatible with Simple Machines Forum 2.0.x

The arguments are the default arguments accepted by svn post-commit hook:

~~~
./svn-smf-hook.py /absolute/path/to/your/repo revision
~~~

## Curent status

Working like a charm.

This script is continously developed, so be sure to check back for updated versions! :smile:

## Dependencies

All that's needed to run this script is Python 2.6 (or newer) and subversion. No other external dependencies.

Python 3 is not supported atm, though it'd be probably easy to convert the script with [*2to3*](http://docs.python.org/2/library/2to3.html) tool.

## Installation

Just download [*svn-smf-hook.py*](https://raw.github.com/spitfire05/svn-smf-hook/master/svn-smf-hook.py) and [*svn-smf-hook.conf*](https://raw.github.com/spitfire05/svn-smf-hook/master/svn-smf-hook.conf) files and place it in your *hooks* folder. Then configure the script and run it from *post-commit* hook.

### Example *post-commit* file

``` sh
#!/bin/sh

REPO=/aboslute/path/to/your/repo
/usr/bin/env python $REPO/hooks/svn-smf-hook.py $1 $2
```

Or if you want it to be asynchronous (so the commit operation will not have to wait till posting ends):

``` sh
#!/bin/sh

REPO=/aboslute/path/to/your/repo
/usr/bin/env python $REPO/hooks/svn-smf-hook.py $1 $2 &
```

## Configuration

Before you deploy this as hook, make sure to properly configure it in *svn-smf-hook.conf* file. Config options are documented in conf file.

## Integration with Project Management Systems

**svn-smf-hook** features [Trac](http://trac.edgewall.org/) and [Redmine](http://redmine.org) integration. You can enable it by setting PMS and PMS_URL config option to the url of your trac/redmine installation.

With PMS integration enabled, the revision number, changed files and all ticket references in commit message (for example: *ticket #1234*) will be converted into links to their PMS pages.

### Supported Project Management Systems and corresponding config values

PMS value | what PMS_URL should point to | Example
--------- | ---------------------------- | -------
'trac' | Root trac address | PMS_URL = 'http://trac.myproject.net'
'redmine' | Root of the project | PMS_URL = 'http://redmine.myproject.org/projects/fooproject'

### Note about post-commit hooks

Even though this script features PMS integration, it does not work as post-commit hook refreshing repo status in PMS. To have your tickets in PMS updated on commit, use the PMS svn hook together with this script.

#### Trac

Read: http://trac.edgewall.org/wiki/TracRepositoryAdmin#Subversion

Personally, I use [this](http://trac.edgewall.org/attachment/wiki/TracMultipleProjects/ComprehensiveSolution/trac-post-commit-hook) Trac hook, and I find it working great. You can even close tickets via commit messages with it.

#### Redmine

Read: http://www.redmine.org/projects/redmine/wiki/HowTo_setup_automatic_refresh_of_repositories_in_Redmine_on_commit

## Integration with other Project Management Systems?

Please fill an issue with request, and I'll probably make it happen :wink:

Pull requests are also welcome.

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
