import json
import os
import load_dotenv

from openai import OpenAI

load_dotenv.load_dotenv()

def generate_lookback(tweets: list) -> dict:
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
