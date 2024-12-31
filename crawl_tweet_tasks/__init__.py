import asyncio
import traceback
from typing import Dict, List, cast
import os
import load_dotenv
import json

load_dotenv.load_dotenv()

from twikit_main.twikit import Client
from celery import Task
from openai import OpenAI
from sqlalchemy.dialects.postgresql import Insert, insert
from sqlmodel import Session, select

from db.database import engine
from .celery_app import celery_crawler

from schemas.add_tweet_request import AddTweetRequest
from schemas.users_schema import UserCreateRequest
from models.users import User
from models.lookbacks import Lookback
from api.api_v1.tweets.services import add_tweet
from api.api_v1.users.services.user_create_request import create_user


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def analyze_tweets(tweets: List[Dict]) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    """<instruction>
                        <instructions>
                            Analyze the provided list of Twitter posts to infer details about the user. Follow these steps:
                            1. Review each post in the list to identify recurring themes, interests, and topics that the user engages with.
                            2. From your analysis, extract three keywords that represent the fields of interest for the user. These should be concise and relevant to the content of the posts.
                            3. Identify three distinct topics of interest based on the posts. For each topic, write a separate sentence that describes it without overlapping content with the other topics.
                            4. Finally, create a one-sentence description of the user that encapsulates their interests and personality based on the analysis of the posts.
                            5. The output language is always Japanese.
                            6. Ensure that the output is clear and does not contain any XML tags.
                        </instructions>
                        
                        <output_format>
                            Your ouput should be in the following format:
                                {
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
                                        "interest": ["Science", "Literature", "Environment"],
                                        "topics": [
                                            "The user is passionate about scientific advancements, particularly in physics and space exploration."
                                            "The user enjoy reading and discussing literature, especially books that delve into complex subjects."
                                            "The user is also concerned about environmental issues and actively seeks out documentaries that highlight climate change."
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
                                        "interest": ["料理芸術", "音楽", "アウトドア活動"],
                                        "topics": [
                                            "ユーザーは新しい料理体験、特にビーガン料理を楽しむことが好きです。",
                                            "ユーザーはライブ音楽に情熱を持ち、音楽フェスティバルに参加することを楽しみにしています。",
                                            "ユーザーはアウトドアアドベンチャー、特に自然の中でのハイキングを愛しています。"
                                        ],
                                        "description": "料理探索、ライブ音楽、アウトドアアドベンチャーを楽しむ活気あふれる個人です。"
                                    }
                                </output>
                            </example>
                            
                            <example>
                                <input>
                                    - "Just finished a marathon! #Running #Fitness"
                                    - "Can't get enough of the latest tech gadgets! #Technology #Innovation"
                                    - "Volunteering at the local animal shelter this weekend. #Animals #Community"
                                </input>
                                <output>
                                    {
                                        "interest": ["Fitness", "Technology", "Community Service"],
                                        "topics": [
                                            "The user is dedicated to fitness and enjoys participating in marathons and running events."
                                            "The user have a keen interest in the latest technology and innovations in the tech industry."
                                            "The user is also committed to community service, particularly in helping animals through volunteering."
                                        ],
                                        "description": "An active and tech-savvy individual who is passionate about fitness and community service."
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
                    f'Tweets list: {json.dumps([tweet["text"] for tweet in tweets])}'
                ),
            }
        ],
    )

    try:
        message = json.loads(completion.choices[0].message.content)
        response = {
            "posts_count": len(tweets),
            "favorite_count": sum([tweet["favorite_count"] for tweet in tweets]),
            "reply_count": sum([tweet["reply_count"] for tweet in tweets]),
            "retweet_count": sum([tweet["retweet_count"] for tweet in tweets]),
            "view_count": sum([tweet["view_count"] for tweet in tweets]),
            "interest": message["interest"],
            "topics": message["topics"],
            "description": message["description"]
        }
        return response
    except Exception:
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
        cookies=dict(ct0=account["ct0"], auth_token=account["auth_token"])
    )
    user = await client.get_user_by_screen_name(screen_name)
    print(user)
    person = UserCreateRequest(
        twitter_id=user.id,
        name=user.name,
        screen_name=user.screen_name,
        description=user.description,
        is_blue_verified=user.is_blue_verified,
        verified=user.verified,
        followers_count=user.followers_count,
        following_count=user.following_count,
        media_count=user.media_count,
        statuses_count=user.statuses_count
    )
    account = create_user(db, person)
    user = db.exec(select(User).where(User.twitter_id == account["twitter_id"])).first()
    
    response = []
    highlight_list = []
    highlights = await client.get_user_highlights_tweets(user_id=account["twitter_id"])

    while(len(highlight_list) < 200 and highlights):
        highlight_list.extend(highlights)
        highlights = await highlights.next()

    if len(highlight_list) < 200:
        more_tweets = await client.get_user_tweets(user_id=account["twitter_id"], tweet_type= "Tweets", count= 20)

        while(len(highlight_list) < 200 and more_tweets):
            highlight_list.extend(more_tweets)
            more_tweets = await more_tweets.next()

    for tweet in highlight_list:
        item = AddTweetRequest(
                tweet_id=tweet.id,
                user_id=user.id,
                created_at=tweet.created_at_datetime.isoformat(),
                text=tweet.text,
                is_quote_status=tweet.is_quote_status,
                reply_count=tweet.reply_count,
                favorite_count=tweet.favorite_count,
                view_count=int(tweet.view_count) if tweet.view_count else 0,
                retweet_count=tweet.retweet_count,
                retweeted_tweet_id=tweet.retweeted_tweet.id if tweet.retweeted_tweet else None,
                hashtags=tweet.hashtags
            )
        response.append(add_tweet(db, item))

    return response


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
        tweets = loop.run_until_complete(_process())
        loop.close()
        if not tweets:
            return []
        results = analyze_tweets(tweets=tweets)
        save_analysis_result(screen_name, results)
        return results
    except Exception:
        print(traceback.format_exc())
        return []
