SELECT
  username,
  COUNT(*) AS likes
FROM
  users
  JOIN likes ON likes.user_id=users.id
GROUP BY
  username;