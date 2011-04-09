Read the Docs features
======================

This will serve as a list of all of the features that Read the Docs currently has. Some features are important enough to have their own page in the docs, others will simply be listed here.


Auto-updating
-------------

The :doc:`webhooks` page talks about the different way you can ping RTD to let us know your project has been updated. We have official support for Github, and anywhere else we have a generic post-commit hook that allows you to POST to a URL to get your documentation built.

Heavily Cached
--------------

We run Varnish in front of RTD, so a lot of the docs you look at will be served out of memory. This is really great for the "Look up and link" that happens a lot on IRC channels. The person who looks up the link will cache the page, and the person they link it to will get it served really quickly.

We also bust caches on all documentation on the RTD domain (not CNAMEs, yet) when you build your docs, so you shouldn't have problems with stale caches.

Versions
--------

Versions are supported at the Version Control level. We support tags and branches that map to versions in RTD parlance. Not all version control systems are equally supported. We would love to accept patches from users of other VCS systems to gain equivalent features across systems.

Version Control Support Matrix
-------------------------------

+------------+------------+-----------+------------+-----------+
|            |    Git     |    hg     |   bzr      |     svn   |
+============+============+===========+============+===========+
| Updating   |    Yes     |    Yes    |   Yes      |    Yes    |
+------------+------------+-----------+------------+-----------+
| Tags       |    Yes     |    Yes    |   No       |    No     |
+------------+------------+-----------+------------+-----------+
| Branches   |    Yes     |    No     |   No       |    No     |
+------------+------------+-----------+------------+-----------+
| Default    |    master  |   default |            |    trunk  |
+------------+------------+-----------+------------+-----------+


PDF Generation
--------------

When you build your project on RTD, we automatically build a PDF of your projects documentation. We also build them for every version that you upload, so we can host the PDFs of your latest documentation, as well as your latest stable releases as well.

Search
------

We provide full-text search across all of the pages of documentation hosted on our site. This uses the excellent Haystack project and Solr as the search backend. We hope to be integrating this into the site more fully in the future.

Alternate Domains
-----------------

We provide support for CNAMEs, Subdomains, and a shorturl for your project as well. This is outlined in the :doc:`alternate_domains` section.

Intersphinx Support
-------------------

All projects built on Read the Docs support :mod:`Intersphinx <sphinx:sphinx.ext.intersphinx>`. If you view source of this page you can see it in action. The configuration looks something like this::

    intersphinx_mapping = {
      'python': ('http://python.readthedocs.org/en/latest/', None),
      'django': ('http://django.readthedocs.org/en/latest/', None),
      'sphinx': ('http://sphinx.readthedocs.org/en/latest/', None),
        }

Then usage is pretty similar. You reference something using normal sphinx syntax, but can use the namespace of the project you want to reference, like so::

    :mod:`Intersphinx <sphinx.ext.intersphinx>`
    :mod:`Intersphinx <sphinx:sphinx.ext.intersphinx>`
