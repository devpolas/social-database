
import random
from faker import Faker
import psycopg2

fake = Faker()

# ---------- CONFIG ----------
DB_NAME = "socialdatabase"
DB_USER = "pcb"
DB_PASS = "PAI9xPPCB"
DB_HOST = "localhost"
DB_PORT = "5432"

N_USERS = 500
N_POSTS = 2000
N_COMMENTS = 5000
N_LIKES = 8000
N_HASHTAGS = 200
N_HASHTAGS_POSTS = 1000
N_FOLLOWERS = 1500
N_PHOTO_TAGS = 500
N_CAPTION_TAGS = 500
# ----------------------------

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Clear old data (optional, keeps IDs consistent)
cur.execute("TRUNCATE likes, comments, photo_tags, caption_tags, hashtags_posts, hashtags, posts, followers, users RESTART IDENTITY CASCADE;")

# USERS
print("Inserting users...")
user_ids = []
for _ in range(N_USERS):
    cur.execute("""
        INSERT INTO users (username, bio, avatar, phone, email, password, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        fake.user_name(),
        fake.text(max_nb_chars=150),
        fake.image_url(),
        None if random.random() < 0.5 else fake.phone_number(),
        fake.unique.email(),
        fake.password(),
        random.choice(["active", "inactive"])
    ))
    user_ids.append(cur.fetchone()[0])

# POSTS
print("Inserting posts...")
post_ids = []
for _ in range(N_POSTS):
    cur.execute("""
        INSERT INTO posts (url, caption, lat, lng, user_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        fake.image_url(),
        fake.sentence(nb_words=8),
        random.uniform(-90, 90) if random.random() < 0.3 else None,
        random.uniform(-180, 180) if random.random() < 0.3 else None,
        random.choice(user_ids)
    ))
    post_ids.append(cur.fetchone()[0])

# COMMENTS
print("Inserting comments...")
comment_ids = []
for _ in range(N_COMMENTS):
    cur.execute("""
        INSERT INTO comments (contents, user_id, post_id)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        fake.sentence(nb_words=12),
        random.choice(user_ids),
        random.choice(post_ids)
    ))
    comment_ids.append(cur.fetchone()[0])

# LIKES (on posts and comments)
print("Inserting likes...")
for _ in range(N_LIKES):
    if random.random() < 0.5:  # like on post
        cur.execute("""
            INSERT INTO likes (user_id, post_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (
            random.choice(user_ids),
            random.choice(post_ids)
        ))
    else:  # like on comment
        cur.execute("""
            INSERT INTO likes (user_id, comment_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (
            random.choice(user_ids),
            random.choice(comment_ids)
        ))

# HASHTAGS (guaranteed unique)
print("Inserting hashtags...")
unique_tags = set()
while len(unique_tags) < N_HASHTAGS:
    unique_tags.add(fake.word())

hashtag_ids = []
for tag in unique_tags:
    cur.execute("""
        INSERT INTO hashtags (title) VALUES (%s)
        RETURNING id
    """, (tag,))
    hashtag_ids.append(cur.fetchone()[0])

# HASHTAGS_POSTS
print("Linking hashtags to posts...")
for _ in range(N_HASHTAGS_POSTS):
    cur.execute("""
        INSERT INTO hashtags_posts (hashtag_id, post_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (
        random.choice(hashtag_ids),
        random.choice(post_ids)
    ))

# FOLLOWERS
print("Inserting followers...")
for _ in range(N_FOLLOWERS):
    leader = random.choice(user_ids)
    follower = random.choice(user_ids)
    if leader != follower:
        cur.execute("""
            INSERT INTO followers (leader_id, follower_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (leader, follower))

# PHOTO_TAGS
print("Inserting photo tags...")
for _ in range(N_PHOTO_TAGS):
    cur.execute("""
        INSERT INTO photo_tags (user_id, post_id, x, y)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (
        random.choice(user_ids),
        random.choice(post_ids),
        random.randint(0, 1000),
        random.randint(0, 1000)
    ))

# CAPTION_TAGS
print("Inserting caption tags...")
for _ in range(N_CAPTION_TAGS):
    cur.execute("""
        INSERT INTO caption_tags (user_id, post_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (
        random.choice(user_ids),
        random.choice(post_ids)
    ))

conn.commit()
cur.close()
conn.close()
print("✅ Done seeding database!")

