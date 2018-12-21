/* Reveal dashboard contains a computed column `day_of_week`. The SQL expression to compupte the value seems to
   be ignored by export/import scripts so it has to be added manually */

UPDATE table_columns SET expression = "CASE
  WHEN DAYOFWEEK(rsvp_timestamp) = 1 THEN 'Sun'
  WHEN DAYOFWEEK(rsvp_timestamp) = 2 THEN 'Mon'
  WHEN DAYOFWEEK(rsvp_timestamp) = 3 THEN 'Tue'
  WHEN DAYOFWEEK(rsvp_timestamp) = 4 THEN 'Wed'
  WHEN DAYOFWEEK(rsvp_timestamp) = 5 THEN 'Thu'
  WHEN DAYOFWEEK(rsvp_timestamp) = 6 THEN 'Fri'
  ELSE 'Sat'
  END" WHERE column_name = 'day_of_week';
