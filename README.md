The Cockpit Test Inspector project
=====================================
Intention of this project is to check if the test is nondesctructive
and have good enough cleanup after test run.

Direct inside Python
====================

```python
from unittest import TestCase
from pprint import pprint
from subprocess import check_call

from testinsp import RunChecks

class SuperTest(TestCase):
    def setUp(self):
        self.check = RunChecks()
        self.check.init()
        # self.check.store() # stores the data to file storage, not needed when used inside python

    def testPass(self):
        pass

    def test_issue_inside_etc(self):
        check_call("sudo touch /etc/cockpit/test.xx", shell=True)

    def tearDown(self) -> None:
        pprint(self.check.check())
```

Usage as separate tool
======================
You can use it as installed tool, and execute it via shell.
Command `init` stores the data into `/var/tmp/testinsp/` directory
 and then you can check it via `check` subcommand.

```bash
python testinsp/cli.py init

# do some harm stuff

python testinsp/cli.py check
```




