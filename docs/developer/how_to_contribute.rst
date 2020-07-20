*****************
How to Contribute
*****************

We'd love you to help us improve Kytos! Being a developer or not, your
feedback is important for us to fix bugs, add new features and
make it easier to create and share Network Applications.

To give us your feedback, check the most appropriate instructions in the next
section. You can also contact us directly and subscribe to mailing lists as
described in the :doc:`/home/get_help` section.

Contributing Guidelines
-----------------------

Here are the guidelines we follow for different ways of contributing:

- `Got a Question or Problem?`_
- `Found an Issue?`_
- `Want a Feature?`_
- `Want a Doc Fix?`_
- `Submission Guidelines`_
- `Coding Style`_
- `Signing the CLA`_

Got a Question or Problem?
--------------------------

If you have questions about how to use any component of the Kytos project,
direct them to our dev mailing list. We are also available on IRC. Check the
details in the :doc:`/home/get_help` section.

.. _contributing-issue:

Found an Issue?
---------------

If you find a bug or a mistake in the documentation, you can help us by
submitting an issue to our |repo|. Even better, you can submit a Pull Request
to fix it. Before sharing a fix with the Kytos Community, **please, check the**
`Submission Guidelines`_ **section**.

.. _contributing-feature-request:

Want a Feature?
---------------

You can also request a new feature by submitting an issue to our |repo|.
If you would like to implement a new feature, then consider what kind of change
it is:

- **Major Changes** that you wish to contribute to the project should be
  discussed first in our dev mailing list or IRC (see: :doc:`/home/get_help`
  section), so that we can better coordinate our efforts, prevent work
  duplication, and help you to craft the changes so they are successfully
  integrated into the project.

- **Small Changes** can be crafted and submitted to the |repo| as Pull Requests.

Before contributing, **please, check the** `Submission Guidelines`_ **section**.

.. _contributing-doc-fix:

Want a Doc Fix?
---------------

You can either submit an issue or fix it by yourself. In either case, **please,
check the** `Submission Guidelines`_ **section**. To update the documentation,
read the section below.

Updating Documentation
""""""""""""""""""""""

Kytos subprojects have a `docs` folder that generates the documentation hosted
in our website. To update it, follow these instructions:

#. Install the required packages listed in requirements-docs.txt;
#. In Python files, use `Google-style docstrings`_ (`Napoleon documentation
   <http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_
   is also a useful resource);
#. To generate the documentation, run ``make`` inside `docs` folder;
#. Open `docs/_build/dirhtml/index.html` in your browser to check the output of
   your changes;
#. Repeat steps 2 and 3 and refresh the page until you are satisfied with the
   results.

Tips and tricks
'''''''''''''''

To automatically build the documentation and refresh the browser every time a
file is changed:

#. In the `docs` folder, run ``make livehtml``;
#. Go to http://127.0.0.1:8000/index.html.

.. IMPORTANT::
  If you add or remove a page and see inconsistent results, try hitting
  `ctrl+c`, running ``make clean`` and then ``make livehtml`` again.

.. _contributing-submission-guidelines:

Submission Guidelines
---------------------

Submitting an Issue
"""""""""""""""""""

Before you submit your issue, **search the archive to check whether the issue
had already been reported**. Use the specific subproject issue tracker of our
|repo|. The more relevant information you provide, the faster contributors can
solve the issue. From the information below, please, provide as much as
possible:

- **Clear description** about your problem: what is the expected outcome and
  what actually happened?
- **Error output** or logs pasted in your issue or in a
  `Gist <http://gist.github.com/>`__. When pasting them in the issue, wrap it
  with three backticks: **\`\`\`** so it renders nicely, like ``this``;
- **Steps to reproduce** - please inform all the steps to reproduce the error;
- **Motivation or use case** - explain why this is a bug for you;
- **System details** like what library or operating system you’re
  using and their versions;
- **Tags** - tag your issue according to the version and issue type;
- **Related issues** - are there similar issues?
- **Suggestions** - if you can't fix the bug yourself, perhaps you can point
  to what might be causing the problem (i.e.: line of code, commit);
- **Working version** - if you specify the version that was working for
  you, we can find the code change that caused the issue and fix it faster.

For more information about GitHub issues, please read the `GitHub's Issues
guide <https://guides.github.com/features/issues/>`__.

Submitting a Pull Request
"""""""""""""""""""""""""

If you’re able to patch the bug or add the feature yourself, fantastic! Before
sharing your changes with Kytos community, be sure you've understood the
license and signed our `Contributor License Agreement (CLA)
<Signing the CLA_>`_.

For pull requests, Kytos subprojects use the *forking workflow*. You can follow
`this more detailed guide
<https://www.atlassian.com/git/tutorials/comparing-workflows#forking-workflow>`_
or the simplified steps below. In the next instructions, suppose you are going
to fix a bug in the *python-openflow* subproject.

One-time setup for the subproject *python-openflow*:

#. Open the `python-openflow GitHub page
   <https://github.com/kytos/python-openflow/>`_ and click in *Fork*;
#. Clone your fork: ``git clone git@github.com:myuser/python-openflow.git``;
#. Add the official repository as *upstream*: ``git remote add upstream
   https://github.com/kytos/python-openflow.git``.

For each pull request:

#. Update your fork with the latest official code (based on `this guide
   <https://help.github.com/articles/syncing-a-fork/>`_):

   a. ``git checkout master``;
   b. ``git merge --ff-only upstream/master``;
   c. ``git push``;

#. Create a branch to work on: ``git checkout -b fix-lorem-ipsum``;
#. Hack, commit, coffee, hack, ..., commit (check code recommendations in the
   next list);
#. Test your code and fix any issue: ``python3 setup.py test``;
#. Push the branch to GitHub: ``git push origin fix-lorem-ipsum``;
#. Visit your repository in GitHub and create a pull request with the push of a
   button.

For a better code and easier maintenance:

- Include appropriate test cases to avoid bugs in the future;
- Follow our `Coding Style`_;
- Avoid big commits if you can split them in meaningful smaller ones;
- Commit your changes using clear, descriptive and on-point commit messages;
- Write useful descriptions and titles;
- Add comments to help guide the reviewer;
- Add some screenshots for your front-end changes;
- Think of a pull request as a product, with the author as the seller, and
  reviewers as customers;
- Know that it's difficult to review pull requests.

For more detailed tips on creating pull requests, read `The (written) unwritten
guide to pull requests
<https://www.atlassian.com/blog/git/written-unwritten-guide-pull-requests>`_.

That's it! Thank you for your contribution!

Open Pull Requests
""""""""""""""""""

Once you’ve opened a pull request, a discussion will start around your proposed
changes. Other contributors and users may chime in, but ultimately the decision
is made by the maintainer(s). You may be asked to make some changes and, if so,
add more commits to your branch and push them – they'll automatically go into
the existing pull request.

Code contribution steps review
""""""""""""""""""""""""""""""

#.  Fork the project & clone locally
#.  Create an upstream remote and sync your local copy before you branch
#.  Branch for each separate piece of work
#.  Do the work, write good commit messages, and follow the project coding style
#.  Push to your origin repository
#.  Create a new PR in GitHub
#.  Respond to any code review feedback

Coding style
------------

We follow pycodestyle, pydocstyle with `Google-style docstrings`_ and `PEP 20
<http://www.python.org/dev/peps/pep-0020/>`_. You can check `The Best of the
Best Practices (BOBP) Guide for Python
<https://gist.github.com/sloria/7001839>`_ for a summary. Besides, we use
several linters.

Our build system checks both style and linter warnings and non-compliant pull
requests won't be merged. But don't worry, ``python3 setup.py test`` will warn
you about any problem in your code.

Signing the CLA
---------------

Please `sign <http://kytos.io/cla/>`__ our Contributor License Agreement (CLA)
before sending pull requests. For any code changes to be accepted, the CLA
must be signed. It's a quick process, we promise!

.. |repo| replace:: `GitHub repository`_
.. _GitHub repository: https://github.com/kytos/
.. _forking workflow: https://www.atlassian.com/git/tutorials/comparing-workflows#forking-workflow
.. _Google-style docstrings: https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments

