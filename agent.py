#load environment variables from .env file
import os
#from twilio.rest import Client
import discord
import asyncio
from dotenv import load_dotenv
load_dotenv()
# import google generative AI
from langchain_google_genai import ChatGoogleGenerativeAI
# import the agent related components(serpapi)
from langchain.agents import load_tools, initialize_agent, AgentType

###Old functiontion to send confirmation message via Twilio

# def send_confirmation_message(to, body):
#     # Initialize Twilio client with environment variables
#     client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
#     receipient = os.getenv('RECIPIENT_PHONE_NUMBER')
#     # Send the message
#     try:
#         message = client.messages.create(
#             to=to,
#             from_=os.getenv('TWILIO_PHONE_NUMBER'),
#             body=body
#         )
#     except Exception as e:
#         print(f"Failed to send message: {e}")
#         return None
#     print(f"Message sent successfully to {to}. Message SID: {message.sid}")
#     # Return the message SID for reference
        
#     return message.sid


#Initialize the Google Generative AI model and make the temperature 0 to make the output factual, the higher the temperature the more likely it is to hallucinate

#Function to send a message to a Discord channel, originally intended for sending confirmation messages but did not want to register for a toll free number
async def send_discord_message(message_body):
    try:
        token = os.getenv('DISCORD_BOT_TOKEN')
        channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))

        if not token or not channel_id:
            raise ValueError("Discord bot token or channel ID not set.")

        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            print(f'Logged in as {client.user}.')
            print(f'Attempting to fetch channel with ID: {channel_id}...')
            
            channel = None # Define channel here to ensure it exists
            try:
                channel = await client.fetch_channel(channel_id)
                print(f"Successfully fetched channel: '{channel.name}' in server '{channel.guild.name}'.")
            except discord.NotFound:
                print("--- !!! FATAL ERROR !!! ---")
                print("Channel not found. Your DISCORD_CHANNEL_ID in the .env file is WRONG.")
                await client.close()
                return
            except discord.Forbidden:
                print("--- !!! FATAL ERROR !!! ---")
                print("Permission denied. The bot does not have 'View Channel' permissions for this specific channel.")
                await client.close()
                return
            except Exception as e:
                print(f"An unexpected error occurred during fetch: {e}")
                await client.close()
                return

            if channel:
                await channel.send(message_body)
                print(">>> Message sent successfully! <<<")
            
            await client.close()
            print("Client is closing. Script should now finish.")

        await client.start(token)

    except Exception as e:
        print(f"Error sending Discord message: {e}")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# "serpapi" is our search tool.
# "llm-math" is a tool that lets the agent use the LLM to do math.
tools = load_tools(["serpapi", "llm-math"], llm=llm)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)




query = input("Enter your research query: ")

print(f"Running agent with query: '{query}'")
result = agent.run(query)


print("\n--- Agent's Final Answer ---")
print(result)


print("Sending Discord notification...")
discord_message = f"✅ **Research Complete!**\n\n**Query**: `{query}`\n\n**Answer**:\n>>> {result}"
asyncio.run(send_discord_message(discord_message))

print("Script finished.")


# Old way of sending confirmation message via Twilio, but did not want to register for a toll free number
#print("Search completed. Sending confirmation message...")
#sms_message = f"Your research query '{query}' has been processed successfully.'/n/Answer:{result}"
# Send confirmation message
#message_sid = send_confirmation_message(os.getenv('RECIPIENT_PHONE_NUMBER'), sms_message)