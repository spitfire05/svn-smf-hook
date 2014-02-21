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

All that's needed to run this script is Python 2 and subversion. No other external dependencies.

## Installation

Just download [*svn-smf-hook.py*](https://raw2.github.com/spitfire05/svn-smf-hook/master/svn-smf-hook.py) and [*svn-smf-hook.conf*](https://raw2.github.com/spitfire05/svn-smf-hook/master/svn-smf-hook.conf) files and place it in your *hooks* folder. Then configure the script and run it from *post-commit* script.

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

## Trac integration

**svn-smf-hook** features [Trac](http://trac.edgewall.org/) integration. You can enable it by setting TRAC_URL config option to the url of your Trac installation.

With Trac integration enabled, the revision number, changed files and all ticket references in commit message (for example: *ticket #1234*) will be converted into links to their Trac pages.

### Note

Even though this script features Trac integration, it does not work as Trac's post-commit hook. To have your tickets in Trac updated on commit, use the Trac svn hook together with this script. Read: http://trac.edgewall.org/wiki/TracRepositoryAdmin#Subversion

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
