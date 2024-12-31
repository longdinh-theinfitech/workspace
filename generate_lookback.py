from openai import OpenAI
import json

OPENAI_API_KEY="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"

def generate_message():
    with open('data/highlights_pretty.json', 'r') as f:
        tweets = json.loads(f.read())

    highlights = sorted(tweets, key=lambda x: x['favorite_count'], reverse=True)[:4]
    api_key = OPENAI_API_KEY
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
                            Follow the below step to generate a look-back twitter post:
                                1. Begin by analyzing the provided JSON array of tweets. Each tweet is represented as a JSON object containing relevant information such as the tweet's content, date, and any associated hashtags or mentions.
                                2. Identify key themes, events, or trends that emerge from the tweets throughout the year. Look for patterns in the topics discussed, the frequency of certain hashtags, or notable interactions with other users.
                                3. Craft a concise and engaging summary for each theme or event, ensuring that the language is suitable for Twitter's character limit. Aim for a tone thatreflects the voice and style of the third-person user.
                                4. Combine the summaries into a single paragraph that captures the essence of the user's year on Twitter. Ensure that the final output is engaging and encourages interaction from followers.
                                5. The output should be formatted as a single tweet or a thread of tweets, depending on the length of the content. Ensure that the final output does not contain any XML tags.
                        </instructions>
                        <examples>
                            <example>
                                <input>
                                    [
                                        {"content": "Excited to launch my new project!", "date": "2023-01-15", "likes": 50, "retweets": 10},
                                        {"content": "Had a great time at the conference!", "date": "2023-03-20", "likes": 75, "retweets": 20},
                                        {"content": "Reflecting on the challenges of the year.", "date": "2023-12-31", "likes": 100, "retweets": 30}
                                    ]
                                </input>
                                <output>
                                    "In January, I was thrilled to announce the launch of my new project, which garnered significant attention with 50 likes and 10 retweets. By March, I attended a conference that proved to be a highlight of the year, receiving 75 likes and 20 retweets. As the year came to a close, I reflected on the challenges faced, culminating in a tweet that resonated with many, achieving 100 likes and 30 retweets."
                                </output>
                            </example>
                            <example>
                                <input>
                                    [
                                        {"content": "Just finished reading an amazing book!", "date": "2023-02-10", "likes": 30, "retweets": 5},
                                        {"content": "Celebrating my birthday with friends!", "date": "2023-05-05", "likes": 120, "retweets": 40},
                                        {"content": "Looking forward to new adventures in 2024!", "date": "2023-12-25", "likes": 80, "retweets": 15}
                                    ]
                                </input>
                                <output>
                                    "February brought a moment of joy as I shared my thoughts on an amazing book, which resonated with my followers, earning 30 likes and 5 retweets. May was a month of celebration as I marked my birthday with friends, a tweet that received an overwhelming response with 120 likes and 40 retweets. As the year wrapped up, I expressed my excitement for new adventures in 2024, garnering 80 likes and 15 retweets."
                                </output>
                            </example>
                            <example>
                                <input>
                                    [
                                        {"content": "Kicked off the year with a fitness goal!", "date": "2023-01-01", "likes": 60, "retweets": 12},
                                        {"content": "Participated in a charity run!", "date": "2023-04-15", "likes": 90, "retweets": 25},
                                        {"content": "Reflecting on personal growth this year.", "date": "2023-11-30", "likes": 110, "retweets": 35}
                                    ]
                                </input>
                                <output>
                                    "The year began with a commitment to fitness, as I kicked off my goals on January 1st, which received 60 likes and 12 retweets. In April, I participated in a charity run, a significant event that resonated with my audience, earning 90 likes and 25 retweets. By November, I took a moment to reflect on my personal growth throughout the year, a tweet that struck a chord with many, achieving 110 likes and 35 retweets."
                                </output>
                            </example>
                        </examples>
                    </instruction>"""
                ),
            },
            {
                "role": "user",
                "content": (
                    f'Tweets list: {highlights}'
                ),
            }
        ],
    )

    try:
        message = completion.choices[0].message.content
        return message
    except Exception:
        return None

if __name__ == '__main__':
    message = generate_message()
    print(message)
