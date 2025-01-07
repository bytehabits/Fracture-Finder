#Prototype/concept file, this is the outline

from openai import OpenAI

client = OpenAI(api_key="KEY")

response = client.chat.completions.create(
  model="gpt-4-turbo",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Is there a bone in the image? If so, is it intact or broken? Please confirm with a confidence level on a percentage scale. Provide a detailed explaination"},
        {
          "type": "image_url",
          "image_url": {
            "url": "URL",
          },
        },
      ],
    }
  ],
  max_tokens=3000,
)

print(response.choices[0])
