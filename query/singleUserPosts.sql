SELECT
  username,
  caption
FROM
  users
  INNER JOIN posts ON posts.user_id=users.id
WHERE
  users.id=200;