/* This piece of SQL needs to be set as `Expression` in the `day_of_week` column
 * Looks like Kinetica doesn't export this attribute when exporting dashboards */

CASE
WHEN DAYOFWEEK(rsvp_timestamp) = 1 THEN 'Sun'
WHEN DAYOFWEEK(rsvp_timestamp) = 1 THEN 'Sun'
WHEN DAYOFWEEK(rsvp_timestamp) = 2 THEN 'Mon'
WHEN DAYOFWEEK(rsvp_timestamp) = 3 THEN 'Tue'
WHEN DAYOFWEEK(rsvp_timestamp) = 4 THEN 'Wed'
WHEN DAYOFWEEK(rsvp_timestamp) = 5 THEN 'Thu'
WHEN DAYOFWEEK(rsvp_timestamp) = 6 THEN 'Fri'
ELSE 'Sat'
END