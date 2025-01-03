import asyncio
import traceback
from typing import Dict, List, cast
import os
import load_dotenv
import json

load_dotenv.load_dotenv()

from datetime import datetime
from twikit_main.twikit import Client
from twikit_main.twikit.errors import AccountLocked
from celery import Task
from openai import OpenAI
from sqlalchemy.dialects.postgresql import Insert, insert
from sqlmodel import Session

from db.database import engine
from .celery_app import celery_crawler

from schemas.add_tweet_request import AddTweetRequest
from schemas.users_schema import UserCreateRequest
from models.users import User
from models.lookbacks import Lookback
from api.api_v1.tweets.services import add_tweet
from api.api_v1.crawl_twitter.services import mark_api_banned
from api.api_v1.users.services.user_create_request import create_user


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def calculate_time_since_last(post_time: datetime) -> str:
    now = datetime.now()
    
    time_difference = now - post_time
    
    total_days = time_difference.days
    weeks = total_days // 7
    days = total_days % 7
    
    if weeks > 0:
        return f"直近{weeks}週間"
    else:
        return f"直近{days}日"


def analyze_tweets(user: Dict, tweets: List[Dict]) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=api_key,
    )

    analyzed_tweets = sorted(tweets, key=lambda x: int(x["view_count"]), reverse=True)[:20]
    first_post_time = sorted(tweets, key=lambda x: x["created_at"])[0]["created_at"]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    """<instruction>
                        <instructions>
                            Analyze the provided list of Twitter posts and user's description to infer details about that user. Follow these steps:
                            1. Review each post in the list to identify recurring themes, interests, and topics that the user engages with.
                            2. From your analysis, extract three keywords that represent the fields of interest for the user. These should be concise and relevant to the content of the posts.
                            3. Identify three distinct topics of interest based on the posts. For each topic, write a separate sentence that describes it without overlapping content with the other topics.
                            4. Finally, create a one-sentence description of the user that encapsulates their interests and personality based on the analysis of the posts.
                            5. Determine the language most used in the input Tweets list and make saure that language will be used to generate the output.
                            6. Ensure that the output is clear and does not contain any XML tags.
                        </instructions>

                        <additional_information>
                            1. The input will be a list of Twitter posts that sorted by views count. The higher views count, the more important the post is.
                            2. The output should include three keywords representing the user's interests, three topics of interest, and a description of the user.
                            3. The keywords should be relevant to the content of the posts and must reflect the specific interests of the user.
                            4. The topics should be distinct and provide a clear overview of the user's interests.
                            5. The description should be concise and capture the essence of the user's personality based on the posts.
                        </additional_information>
                        
                        <output_format>
                            Your ouput should be in the following format:
                                {
                                    "Most used language": "Language used in the input Tweets list",
                                    "interest": ["Keyword 1", "Keyword 2", "Keyword 3"],
                                    "topics": ["Topic 1", "Topic 2", "Topic 3"],
                                    "description": "Description of the user."
                                }
                        </output_format>

                        <examples>
                            <example>
                                <input>
                                    - "Just finished reading a fascinating book on quantum physics! #Science #Books"
                                    - "Can't wait for the next space launch! #Space #NASA"
                                    - "Loving the new documentary on climate change. #Environment #Documentary"
                                </input>
                                <output>
                                    {
                                        'Most used language': 'English',
                                        "interest": ["Science", "Literature", "Environment"],
                                        "topics": [
                                            "Topic 1: Passionate about scientific advancements, particularly in physics and space exploration."
                                            "Topic 2: Enjoy reading and discussing literature, especially books that delve into complex subjects."
                                            "Topic 3: Concerned about environmental issues and actively seeks out documentaries that highlight climate change."
                                        ],
                                        "description": "An inquisitive individual with a strong interest in science, literature, and environmental advocacy."
                                    }
                                </output>
                            </example>
                            
                            <example>
                                <input>
                                    - "ダウンタウンの新しいビーガンレストランを試してみました！#フーディー #ビーガン"
                                    - "今度の音楽フェスティバルが楽しみです！#ライブミュージック #フェスティバル"
                                    - "週末を山でのハイキングに費やしました。#自然 #冒険"
                                </input>
                                <output>
                                    {
                                        'Most used language': 'Japanese',
                                        "interest": ["料理芸術", "音楽", "アウトドア活動"],
                                        "topics": [
                                            "トピック1: 新しい料理体験、特にビーガン料理を楽しむことが好きだ",
                                            "トピック2: ライブ音楽に情熱を持ち、音楽フェスティバルに参加することを楽しみにしている",
                                            "トピック3: アウトドアアドベンチャー、特に自然の中でのハイキングを愛している"
                                        ],
                                        "description": "料理探索、ライブ音楽、アウトドアアドベンチャーを楽しむ活気あふれる個人だ"
                                    }
                                </output>
                            </example>
                        </examples>
                    </instruction>"""
                ),
            },
            {
                "role": "user",
                "content": (
                    f'User description: {user["description"]}\n'
                    f'Tweets list: {json.dumps([tweet["text"] for tweet in analyzed_tweets])}'
                ),
            }
        ],
    )

    try:
        message = json.loads(completion.choices[0].message.content)
        retweets = [tweet for tweet in tweets if tweet["text"].startswith("RT @")]
        response = {
            "urls": [f"https://x.com/{user['screen_name']}/status/{tweet['tweet_id']}" for tweet in analyzed_tweets[:3]],
            "time_gap": calculate_time_since_last(first_post_time),
            "posts_count": len(tweets) - len(retweets),
            "favorite_count": sum([tweet["favorite_count"] for tweet in tweets]),
            "reply_count": sum([tweet["reply_count"] for tweet in tweets]),
            "retweet_count": len(retweets),
            "view_count": sum([tweet["view_count"] for tweet in tweets]),
            "interest": message["interest"],
            "topics": message["topics"],
            "description": message["description"]
        }
        return response
    except Exception as e:
        return None

async def process_person(
    screen_name: str,
    account: Dict
):
    db = Session(engine)
    client = Client(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) "
        + "Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        language="ja",
    )
    client.set_cookies(
        cookies=dict(
            ct0=account["ct0"],
            auth_token=account["auth_token"])
    )

    try:
        twitter_user = await client.get_user_by_screen_name(screen_name)
    except AccountLocked:
        print("get_user_by_screen_name", account["id"])
        mark_api_banned(db, account["id"], "get_user_by_screen_name")
        return []
        
    person = UserCreateRequest(
        twitter_id=twitter_user.id,
        name=twitter_user.name,
        screen_name=twitter_user.screen_name,
        description=twitter_user.description,
        is_blue_verified=twitter_user.is_blue_verified,
        verified=twitter_user.verified,
        followers_count=twitter_user.followers_count,
        following_count=twitter_user.following_count,
        media_count=twitter_user.media_count,
        statuses_count=twitter_user.statuses_count
    )
    new_user = create_user(db, person)
    
    response = []
    highlight_list = []
    client.set_cookies(
        cookies=dict(
            ct0=account["ct0"],
            auth_token=account["auth_token"])
    )
    try:
        highlights = await client.get_user_highlights_tweets(user_id=new_user["twitter_id"])
    except AccountLocked:
        print("get_user_highlights_tweets", account["id"])
        mark_api_banned(db, account["id"], "get_user_highlights_tweets")
        return []

    while(len(highlight_list) < 200 and highlights):
        highlight_list.extend(highlights)
        highlights = await highlights.next()

    if len(highlight_list) < 200:
        client.set_cookies(
            cookies=dict(
                ct0=account["ct0"],
                auth_token=account["auth_token"])
        )
        try:
            more_tweets = await client.get_user_tweets(user_id=new_user["twitter_id"], tweet_type= "Tweets", count= 20)
        except AccountLocked:
            mark_api_banned(db, account["id"], "get_user_tweets")
            return []

        while(len(highlight_list) < 200 and more_tweets):
            highlight_list.extend(more_tweets)
            more_tweets = await more_tweets.next()

    for tweet in highlight_list:
        item = AddTweetRequest(
                tweet_id=tweet.id,
                user_id=new_user["id"],
                created_at=tweet.created_at_datetime.isoformat(),
                text=tweet.text,
                is_quote_status=tweet.is_quote_status,
                reply_count=tweet.reply_count,
                favorite_count=tweet.favorite_count,
                view_count=int(tweet.view_count) if tweet.view_count is not None else 0,
                retweet_count=tweet.retweet_count,
                retweeted_tweet_id=tweet.retweeted_tweet.id if tweet.retweeted_tweet else None,
                hashtags=tweet.hashtags
            )
        response.append(add_tweet(db, item))

    return new_user, response


def save_analysis_result(screen_name:str, results: Lookback):
    """Insert LLM analysis result to tweets table with upsert by tweet_id"""
    try:
        db = Session(engine)
        columns = [
            "screen_name",
            "lookback_msg",
        ]
        mappings = [
            {
                "screen_name": screen_name,
                "lookback_msg": json.dumps(results),
            }
        ]
        stmt = cast(Insert, insert(Lookback)).values(mappings)
        stmt = stmt.on_conflict_do_update(
            constraint="user_unique",
            set_={x: getattr(stmt.excluded, x) for x in columns},
        )
        db.exec(stmt)
        db.commit()
    finally:
        db.close()


@celery_crawler.task(
    bind=True,
    ack_late=True,
)
def entry_task(self: Task, screen_name: str, account: dict):
    async def _process():
        return await process_person(
            screen_name=screen_name,
            account=account
        )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        user, tweets = loop.run_until_complete(_process())
        loop.close()
        if not tweets:
            return []
        results = analyze_tweets(user, tweets)
        save_analysis_result(screen_name, results)
        return results
    except Exception:
        print(traceback.format_exc())
        return []
