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

