## Install:

If you use Python you will know what means `sudo pip install microanalytics`.

If you don't use Python, grab our most recent binary in our [releases](https://github.com/fiatjaf/microanalytics-cli/releases) page.

## Usage:

`microanalytics [tracking-code] sessions` lists the number of unique sessions in the last 45 days:
```
2014-10-08  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  22
2014-10-09  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  29
2014-10-10  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  25
2014-10-11  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  22
2014-10-12  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  22
2014-10-13  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  21
2014-10-14  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  25
2014-10-15  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  22
2014-10-16  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  28
2014-10-17  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  28
2014-10-18  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  26
2014-10-19  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  29
```

`microanalytics [tracking-code] pageviews` will do the same as `... sessions`, but for the total number of page views (the `pageView` event).

`microanalytics [tracking-code] events` lists the last 70 events dispatched at the target site:
```
+----------+----------------------------+--------------------------------+---------+----------------------+
| Event    |            Date            | Page                           | Session | Referrer             |
+----------+----------------------------+--------------------------------+---------+----------------------+
| click    | 2014-10-19 01:20:36.108026 | tos.alhur.es/desc/Ferro%20(mg) |  dfca9  | https://www.facebook |
| pageView | 2014-10-19 01:48:54.236665 | sc/Fibra%20Alimentar%20%28g%29 |  3b3a2  | https://m.facebook.c |
| pageView | 2014-10-19 02:32:17.732904 | http://alimentos.alhur.es/     |  080fa  |                      |
| click    | 2014-10-19 02:32:27.537656 | http://alimentos.alhur.es/     |  080fa  |                      |
| click    | 2014-10-19 02:33:07.567718 | ur.es/desc/Prote%C3%ADna%20(g) |  080fa  |                      |
| click    | 2014-10-19 02:33:15.119151 | alhur.es/asc/Carboidrato%20(g) |  080fa  |                      |
| click    | 2014-10-19 02:33:20.843767 | ur.es/desc/Prote%C3%ADna%20(g) |  080fa  |                      |
| click    | 2014-10-19 02:33:22.748110 | tos.alhur.es/desc/Ferro%20(mg) |  080fa  |                      |
| click    | 2014-10-19 02:33:24.147360 | tos.alhur.es/desc/Ferro%20(mg) |  080fa  |                      |
| click    | 2014-10-19 02:33:26.702914 | alhur.es/asc/Carboidrato%20(g) |  080fa  |                      |
+----------+----------------------------+--------------------------------+---------+----------------------+
```

`microanalytics [tracking-code]` will have the same result as of calling `events` and `sessions` together.

`microanalytics [tracking-code] referrals` will show a chart with all the website domains that referred a visitor to your tracked website:

```
Top referrals:
     pt.scribd.com  ▇  1
  www.facebook.com  ▇  1
    m.facebook.com  ▇▇▇▇  3
 www.google.com.br  ▇▇▇▇▇▇▇▇  6
   lm.facebook.com  ▇▇▇▇▇▇▇▇▇▇▇▇▇  10
    www.reddit.com  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  16
```

`microanalytics [tracking-code] pages` works like `... referrals`, but it shows instead data about the visited pages in your website.


