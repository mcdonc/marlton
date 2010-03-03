Errata for "The repoze.bfg Web Framework, Version 1.2" Printed Edition
======================================================================

pp. 3
-----

The sentence:

   However, although they’re not very similar on the surface, both a
   ledger-serving application and a song-serving application could be
   successfully be written using ``repoze.bfg``.

Should read:

   However, although they’re not very similar on the surface, both a
   ledger-serving application and a song-serving application can be
   written using ``repoze.bfg``.

pp. 42
------

The title:

   Runnning The Project

Should read:

   Running The Project

pp. 47
------

The title:

   This is the function called *PasteDeploy*.

Should read:

   This is the function called by *PasteDeploy*.

pp. 51
------

In the numbered list that makes up the bottom half of the page, all
references to line numbers in the example above except "Line 1" should
be decremented by one.  E.g. instead of "Line 4"", it should read
"Line 3", and instead of "Lines 6-10" it should read "Lines 5-9", and
so on.

pp. 64
------

In the warning nearer the bottom of the page, the sentence:

  In repoze.bfg 1.0 and prior versions, the root factory was passed a
  term WSGI environment object...

Should read:

  In repoze.bfg 1.0 and prior versions, the root factory was passed a
  WSGI environment object...

pp. 67
------

The sentence:

  It passes the back the information it obtained to its caller...

Should begin:

  It passes back the information it obtained to its caller...

pp. 79
------

The sentence that begins:

  The order that route are evaluated...

Should instead begin:

  The order that routes are evaluated...

pp. 80
------

The paragraph:

  Other arguments are ``name`` and ``factory``.  These are required
  arguments but represent neither a predicate nor view configuration
  information.

Should read:

  Other arguments are ``name`` and ``factory``.  These arguments are
  neither predicate arguments nor view configuration information
  arguments.


pp. 247
-------

The example:

   ``persistint.mapping.PersistentMapping``

Should read:

   ``persistent.mapping.PersistentMapping``

pp. 350
-------

The sentence:

  Note in the call to SessionDataManager that '3600' represents the
  disuse timeout (5 minutes == 3600 seconds), and '5' represents a
  write granularity time (the session will be marked as active at most
  every five seconds).

Should read:

  Note in the call to SessionDataManager that '3600' represents the
  disuse timeout (60 minutes == 3600 seconds), and '5' represents a
  write granularity time (the session will be marked as active at most
  every five seconds).

